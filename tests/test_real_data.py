"""Tests for the real-data samples and the recorded results.

These tests check the committed samples and results file structure.
They never fetch the network and never run the full pipeline in CI.
"""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REAL = os.path.join(ROOT, "real-data")
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))

from pipeline_deep import DeepRagPipeline  # noqa: E402


def load(*parts):
    with open(os.path.join(REAL, *parts), encoding="utf-8") as fh:
        return json.load(fh)


class TestSamples(unittest.TestCase):
    def test_sample_sizes(self):
        # v1.2 sizes: SQuAD every 10th of the first 5,000 validation
        # rows; HotpotQA the first 200 validation rows.
        self.assertEqual(len(load("samples", "squad_cases.json")), 500)
        self.assertEqual(len(load("samples", "hotpot_cases.json")), 200)

    def test_cases_have_gold(self):
        for name in ("squad_cases.json", "hotpot_cases.json"):
            for case in load("samples", name):
                self.assertTrue(case["question"])
                self.assertTrue(case["gold_answer"])
                self.assertTrue(case["gold_facts"])

    def test_corpus_shape(self):
        for name in ("squad_corpus.json", "hotpot_corpus.json"):
            docs = load("samples", name)
            self.assertGreater(len(docs), 10)
            for doc in docs[:5]:
                self.assertIn("id", doc)
                self.assertTrue(doc["sentences"])


VARIANTS = (
    "without_rerank",
    "with_rerank",
    "span_without_rerank",
    "span_with_rerank",
)


class TestResultsFile(unittest.TestCase):
    def test_results_structure(self):
        payload = load("results_real.json")
        self.assertIn("real", payload["data_kind"])
        self.assertEqual(payload["model_judge"]["status"], "ran")
        for key in ("squad", "hotpotqa"):
            for variant in VARIANTS:
                run = payload["datasets"][key][variant]
                self.assertEqual(run["n"], len(run["results"]))
                self.assertGreaterEqual(run["pass_rate"], 0.0)
                self.assertLessEqual(run["pass_rate"], 1.0)
                self.assertIn("model_summary", run)
                self.assertIn("top1_contains_gold", run)

    def test_span_variants_use_span_mode(self):
        payload = load("results_real.json")
        for key in ("squad", "hotpotqa"):
            for variant in VARIANTS:
                run = payload["datasets"][key][variant]
                expected = "span" if variant.startswith("span") else "sentence"
                self.assertEqual(run["answer_mode"], expected)
                for result in run["results"][:10]:
                    self.assertIn(
                        result["system_answer"], result["source_sentence"]
                    )


class TestRunnerOnSubset(unittest.TestCase):
    def test_pipeline_answers_a_real_case(self):
        cases = load("samples", "squad_cases.json")[:3]
        corpus = load("samples", "squad_corpus.json")
        pipe = DeepRagPipeline(corpus, top_k=5, use_rerank=True)
        out = pipe.answer(cases[0]["question"])
        self.assertIn("answer", out)
        self.assertTrue(out["contexts"])


if __name__ == "__main__":
    unittest.main()
