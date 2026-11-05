"""Tests for the embedding judge. A fake embedder is injected, so no
model is ever downloaded in CI. Stdlib unittest only."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "model-metrics"))

from embedding_judge import (  # noqa: E402
    EmbeddingJudge,
    Model2VecEmbedder,
    ModelUnavailable,
    cosine,
)


class FakeEmbedder:
    """Maps exact strings to fixed vectors."""

    VECTORS = {
        "the broncos won": [1.0, 0.0],
        "denver broncos": [0.9, 0.1],
        "context about denver broncos winning": [0.95, 0.05],
        "unrelated weather text": [0.0, 1.0],
    }

    def __call__(self, texts):
        return [self.VECTORS[t] for t in texts]


class TestCosine(unittest.TestCase):
    def test_identical_is_one(self):
        self.assertAlmostEqual(cosine([1.0, 2.0], [1.0, 2.0]), 1.0)

    def test_orthogonal_is_zero(self):
        self.assertAlmostEqual(cosine([1.0, 0.0], [0.0, 1.0]), 0.0)

    def test_zero_vector_is_zero(self):
        self.assertEqual(cosine([0.0, 0.0], [1.0, 1.0]), 0.0)


class TestEmbeddingJudge(unittest.TestCase):
    def setUp(self):
        self.judge = EmbeddingJudge(FakeEmbedder())
        self.case = {"gold_answer": "denver broncos"}

    def test_similar_answer_passes(self):
        verdict = self.judge(
            self.case,
            "the broncos won",
            ["context about denver broncos winning"],
        )
        self.assertGreater(verdict["semantic_answer_similarity"], 0.9)
        self.assertTrue(verdict["judge_pass"])
        self.assertEqual(verdict["model"], "minishlab/potion-base-8M")

    def test_unrelated_answer_fails(self):
        verdict = self.judge(
            self.case, "unrelated weather text", ["unrelated weather text"]
        )
        self.assertLess(verdict["semantic_answer_similarity"], 0.3)
        self.assertFalse(verdict["judge_pass"])

    def test_empty_answer_scores_zero(self):
        verdict = self.judge(self.case, "", ["anything"])
        self.assertEqual(verdict["semantic_answer_similarity"], 0.0)
        self.assertFalse(verdict["judge_pass"])

    def test_support_uses_best_context(self):
        verdict = self.judge(
            self.case,
            "denver broncos",
            ["unrelated weather text", "context about denver broncos winning"],
        )
        self.assertGreater(verdict["semantic_support"], 0.9)


class TestModelUnavailable(unittest.TestCase):
    def test_missing_model_raises_with_reason(self):
        embedder = Model2VecEmbedder(model_name="minishlab/does-not-exist-xx")
        with self.assertRaises(ModelUnavailable):
            embedder(["probe"])


if __name__ == "__main__":
    unittest.main()
