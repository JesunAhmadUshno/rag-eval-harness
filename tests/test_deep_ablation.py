"""Tests for level-3-deep/ablation.py: the shipped variant must match the
recorded Deep and rerank-experiment numbers, so the ablation measures
the real reranker and not a look-alike."""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))

import ablation  # noqa: E402
from reranker import rerank, stem  # noqa: E402


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


class TestAblation(unittest.TestCase):
    def test_full_rule_set_matches_shipped_stem(self):
        full = ablation.make_stem(ablation.RULES)
        for word in ("libraries", "classes", "speaking", "booked", "runs", "glass", "is", "class"):
            self.assertEqual(full(word), stem(word))

    def test_shipped_rerank_matches_reranker(self):
        hits = [("The club meets on Friday.", 3.0), ("The club runs chess games.", 2.0)]
        mine = ablation.make_rerank(ablation.RULES, "coverage_f1_bm25")
        self.assertEqual(mine("Where does the club run?", hits), rerank("Where does the club run?", hits))

    def test_shipped_variant_reproduces_recorded_runs(self):
        deep = load("level-3-deep", "results_deep.json")
        exp = load("real-data", "results_rerank_experiment.json")
        out = load("level-3-deep", "results_ablation.json")
        self.assertEqual(out["synthetic_deep"]["shipped"]["passed"], deep["with"]["passed"])
        self.assertEqual(out["synthetic_deep"]["bm25_only"]["passed"], deep["without"]["passed"])
        self.assertEqual(out["synthetic_deep"]["shipped"]["b11_passed"], deep["b11"]["passed_with"])
        for ds in ("squad", "hotpotqa"):
            real = out["real_top1_contains_gold"][ds]
            self.assertEqual(real["shipped"], exp["datasets"][ds]["variants"]["current"]["top1_contains_gold"])
            self.assertEqual(real["bm25_only"], exp["datasets"][ds]["variants"]["bm25"]["top1_contains_gold"])

    def test_synthetic_run_is_live(self):
        fn = ablation.make_rerank(ablation.RULES, "coverage_f1_bm25")
        self.assertEqual(ablation.synthetic(fn)["passed"], 32)


if __name__ == "__main__":
    unittest.main()
