"""Tests for real-data/paired_stats.py: hand-checkable statistics and
agreement with the recorded calibration.json. No network, no model."""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "real-data"))

import paired_stats as ps  # noqa: E402


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


class TestStats(unittest.TestCase):
    def test_binomial_two_sided(self):
        # 1 of 4 at p = 0.5: P(X <= 1) = 5/16, doubled = 0.625.
        self.assertAlmostEqual(ps.binom_two_sided(1, 4), 0.625)
        self.assertAlmostEqual(ps.binom_two_sided(3, 4), 0.625)
        self.assertEqual(ps.binom_two_sided(0, 0), 1.0)

    def test_wilson_known_value(self):
        # 274 of 500: p = 0.548, Wilson 95% about 0.504 to 0.591.
        lo, hi = ps.wilson(274, 500)
        self.assertAlmostEqual(lo, 0.5042, places=3)
        self.assertAlmostEqual(hi, 0.5911, places=3)

    def test_mcnemar_counts(self):
        out = ps.mcnemar([True, True, False, False], [True, False, True, True])
        self.assertEqual((out["a_only"], out["b_only"]), (1, 2))


class TestRecorded(unittest.TestCase):
    def test_reproduces_calibration_json(self):
        real = load("real-data", "results_real.json")
        cal = load("model-metrics", "calibration.json")
        for dataset, variants in real["datasets"].items():
            for variant, run in variants.items():
                res = run["results"]
                proxy = [ps.proxy_correct(r) for r in res]
                agree, kappa = ps.kappa(ps.judge_flags(res, 30, 25), proxy)
                want = cal["datasets"][dataset][variant]["judge_vs_proxy"]
                self.assertAlmostEqual(round(agree, 4), want["agreement"])
                self.assertAlmostEqual(round(kappa, 4), want["cohen_kappa"])

    def test_committed_output_matches_inputs(self):
        out = load("real-data", "results_paired_stats.json")
        squad = out["datasets"]["squad"]
        self.assertEqual(squad["variants"]["without_rerank"]["judge_passed"], 274)
        self.assertEqual(squad["variants"]["with_rerank"]["judge_passed"], 281)
        sign = squad["reranker_sign_test"]
        self.assertEqual((sign["helped"], sign["hurt"]), (26, 22))
        self.assertGreater(sign["p_exact"], 0.05)
        judge = squad["rerank_effect"]["sentence"]["model_judge_pass"]
        self.assertEqual(judge["b_only"] - judge["a_only"], 281 - 274)


if __name__ == "__main__":
    unittest.main()
