"""Level 1 Learn tests. Every expected value below was computed by hand
from the formulas in level-1-learn/rag_eval.py before the code ran.
Run: python -m unittest discover -s tests -p "test_learn*.py" -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from rag_eval import (  # noqa: E402
    answer_relevance,
    content_tokens,
    context_recall,
    faithfulness,
    score_all,
    score_case,
)


class TestTokens(unittest.TestCase):
    def test_stopwords_and_case(self):
        self.assertEqual(
            content_tokens("The Library opens at 8 AM."),
            ["library", "opens", "8", "am"],
        )

    def test_hyphen_splits(self):
        self.assertEqual(content_tokens("Northlight-Guest"), ["northlight", "guest"])


class TestMetrics(unittest.TestCase):
    def test_faithfulness_full_support(self):
        self.assertEqual(
            faithfulness("opens at 8 am", ["Library opens at 8 am on weekdays"]), 1.0
        )

    def test_faithfulness_partial_support(self):
        # Answer tokens: study, rooms, hold, up, twenty, people, include,
        # projector (8). Supported by context: 5. 5/8 = 0.625.
        self.assertAlmostEqual(
            faithfulness(
                "The study rooms hold up to twenty people and include a projector.",
                ["The study rooms hold up to six people."],
            ),
            0.625,
        )

    def test_faithfulness_empty_answer(self):
        self.assertEqual(faithfulness("", ["any context"]), 0.0)

    def test_context_recall_half(self):
        self.assertEqual(
            context_recall(
                ["Membership includes borrowing up to ten books."],
                ["borrowing up to ten books", "free access to the computer lab"],
            ),
            0.5,
        )

    def test_answer_relevance_f1(self):
        # Shared 5, precision 5/8, recall 5/6, F1 = 0.714 (3 dp).
        self.assertAlmostEqual(
            answer_relevance(
                "The study rooms hold up to twenty people and include a projector.",
                "The study rooms hold up to six people.",
            ),
            0.714,
            places=3,
        )

    def test_answer_relevance_no_overlap(self):
        self.assertEqual(
            answer_relevance(
                "The reading room seats forty people.",
                "Members can borrow a book for three weeks.",
            ),
            0.0,
        )


class TestGoldenSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "level-1-learn", "golden_set.json")
        with open(path, encoding="utf-8") as fh:
            cls.cases = json.load(fh)
        cls.summary = score_all(cls.cases)

    def test_golden_summary_counts(self):
        self.assertEqual(self.summary["n"], 8)
        self.assertEqual(self.summary["passed"], 5)
        self.assertAlmostEqual(self.summary["pass_rate"], 0.625)

    def test_each_failure_label_appears_once(self):
        self.assertEqual(
            self.summary["label_counts"],
            {
                "hallucination": 1,
                "retrieval_miss": 1,
                "wrong_or_incomplete_answer": 1,
            },
        )

    def test_designed_cases_carry_designed_labels(self):
        by_id = {c["id"]: c for c in self.cases}
        self.assertEqual(
            score_case(by_id["g03-room-hallucination"])["labels"], ["hallucination"]
        )
        self.assertEqual(
            score_case(by_id["g04-membership-retrieval-miss"])["labels"],
            ["retrieval_miss"],
        )
        self.assertEqual(
            score_case(by_id["g05-loan-wrong-answer"])["labels"],
            ["wrong_or_incomplete_answer"],
        )


if __name__ == "__main__":
    unittest.main()
