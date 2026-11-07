"""Uncertainty and paired tests for the recorded real-data runs. Stdlib only.

The v1.2 write-ups compare pass counts (judge 274 vs 281, top-1 helped 26
vs hurt 22) with no intervals and no tests. Every run here is paired: the
same 500 SQuAD and 200 HotpotQA cases go through each variant. So this
script reads the per-case flags already in results_real.json and
results_rerank_experiment.json, with no model run and no network, and
writes:

- Wilson 95% intervals for every pass rate (lexical, judge, top-1 gold).
- Exact McNemar tests (a two-sided binomial test on the discordant pairs)
  for with vs without rerank, and for sentence vs span answers.
- An exact sign test on the reranker diagnostics (top-1 helped vs hurt).
- A 2-D judge threshold sweep (similarity x support) against the
  gold-derived proxy label from model-metrics/calibrate_judge.py, a
  seeded bootstrap 95% interval on Cohen's kappa at the shipped
  thresholds, and a 2-fold (even/odd case index) fit of the threshold
  pair so the shipped pair can be compared with one chosen on held-out
  cases. The proxy is built from gold data, not human labels.

Run: python real-data/paired_stats.py
Writes: real-data/results_paired_stats.json
"""

import json
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from rag_eval import PASS_RELEVANCE  # noqa: E402

Z95 = 1.959964
SEED = 20261107
BOOTSTRAP_RUNS = 2000
SHIPPED = (30, 25)  # similarity, support, in hundredths
SIM_GRID = list(range(10, 81, 5))
SUP_GRID = list(range(0, 51, 5))
NORM_RE = re.compile(r"[^a-z0-9]+")


def wilson(passed, n, z=Z95):
    """Wilson score interval for passed of n. Returns [low, high]."""
    if n == 0:
        return [0.0, 0.0]
    p = passed / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = (z / den) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round(centre - half, 4), round(centre + half, 4)]


def binom_two_sided(k, n):
    """Exact two-sided binomial test of k successes in n at p = 0.5."""
    if n == 0:
        return 1.0
    lo = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(lo + 1)) / 2**n
    return min(1.0, 2 * tail)


def mcnemar(a_flags, b_flags):
    """Exact McNemar on paired booleans. b = a only, c = b only."""
    only_a = sum(1 for x, y in zip(a_flags, b_flags) if x and not y)
    only_b = sum(1 for x, y in zip(a_flags, b_flags) if y and not x)
    return {
        "a_only": only_a,
        "b_only": only_b,
        "discordant": only_a + only_b,
        "p_exact": round(binom_two_sided(only_a, only_a + only_b), 4),
    }


def _norm(text):
    return " " + NORM_RE.sub(" ", text.lower()).strip() + " "


def proxy_correct(result):
    """Same rule as model-metrics/calibrate_judge.py."""
    return (
        _norm(result["gold_answer"]) in _norm(result["system_answer"])
        or result["answer_relevance"] >= PASS_RELEVANCE
    )


def kappa(judge, proxy):
    n = len(judge)
    tp = sum(1 for a, b in zip(judge, proxy) if a and b)
    fp = sum(1 for a, b in zip(judge, proxy) if a and not b)
    fn = sum(1 for a, b in zip(judge, proxy) if not a and b)
    observed = (n - fp - fn) / n
    pa, pb = (tp + fp) / n, (tp + fn) / n
    expected = pa * pb + (1 - pa) * (1 - pb)
    k = (observed - expected) / (1 - expected) if expected < 1 else 1.0
    return observed, k


def judge_flags(results, sim, sup):
    return [
        r["semantic_answer_similarity"] >= sim / 100 and r["semantic_support"] >= sup / 100
        for r in results
    ]


def best_pair(results, proxy):
    """Threshold pair with the highest agreement; ties keep the first in grid order."""
    best = None
    for sim in SIM_GRID:
        for sup in SUP_GRID:
            agree, _ = kappa(judge_flags(results, sim, sup), proxy)
            if best is None or agree > best[0]:
                best = (agree, sim, sup)
    return best[1], best[2]


def calibration(results, rng):
    proxy = [proxy_correct(r) for r in results]
    sweep = []
    for sim in SIM_GRID:
        row = []
        for sup in SUP_GRID:
            flags = judge_flags(results, sim, sup)
            agree, k = kappa(flags, proxy)
            row.append([sum(flags), round(agree, 4), round(k, 4)])
        sweep.append(row)
    shipped = judge_flags(results, *SHIPPED)
    n = len(results)
    boots = []
    for _ in range(BOOTSTRAP_RUNS):
        idx = [rng.randrange(n) for _ in range(n)]
        boots.append(kappa([shipped[i] for i in idx], [proxy[i] for i in idx])[1])
    boots.sort()
    folds = {}
    for name, fit, test in (("fit_even_test_odd", 0, 1), ("fit_odd_test_even", 1, 0)):
        fit_r = [r for i, r in enumerate(results) if i % 2 == fit]
        test_r = [r for i, r in enumerate(results) if i % 2 == test]
        fit_p = [p for i, p in enumerate(proxy) if i % 2 == fit]
        test_p = [p for i, p in enumerate(proxy) if i % 2 == test]
        sim, sup = best_pair(fit_r, fit_p)
        fitted = kappa(judge_flags(test_r, sim, sup), test_p)
        shipped_test = kappa(judge_flags(test_r, *SHIPPED), test_p)
        folds[name] = {
            "fitted_similarity": sim / 100,
            "fitted_support": sup / 100,
            "test_agreement_fitted": round(fitted[0], 4),
            "test_kappa_fitted": round(fitted[1], 4),
            "test_agreement_shipped": round(shipped_test[0], 4),
            "test_kappa_shipped": round(shipped_test[1], 4),
        }
    return {
        "proxy_correct": sum(proxy),
        "kappa_shipped": round(kappa(shipped, proxy)[1], 4),
        "kappa_bootstrap_ci95": [
            round(boots[int(0.025 * BOOTSTRAP_RUNS)], 4),
            round(boots[int(0.975 * BOOTSTRAP_RUNS) - 1], 4),
        ],
        "sweep_cells": "[judge_passed, agreement, kappa] per similarity row x support column",
        "sweep": sweep,
        "two_fold": folds,
    }


def main():
    with open(os.path.join(HERE, "results_real.json"), encoding="utf-8") as fh:
        real = json.load(fh)
    with open(os.path.join(HERE, "results_rerank_experiment.json"), encoding="utf-8") as fh:
        rerank_exp = json.load(fh)
    rng = random.Random(SEED)
    payload = {
        "generated_by": "real-data/paired_stats.py",
        "data_kind": "real public datasets, recorded per-case results; not synthetic",
        "interval": "Wilson score, 95%",
        "paired_test": "exact McNemar (two-sided binomial on discordant pairs, p = 0.5)",
        "bootstrap": {"runs": BOOTSTRAP_RUNS, "seed": SEED},
        "grid": {"similarity": [s / 100 for s in SIM_GRID], "support": [s / 100 for s in SUP_GRID]},
        "datasets": {},
    }
    for dataset, variants in real["datasets"].items():
        out = {"variants": {}, "rerank_effect": {}, "mode_effect": {}, "calibration": {}}
        for variant, run in variants.items():
            res = run["results"]
            n = len(res)
            counts = {
                "lexical": sum(r["passed"] for r in res),
                "judge": sum(bool(r["model_judge_pass"]) for r in res),
                "top1_contains_gold": sum(bool(r["top1_contains_gold"]) for r in res),
            }
            out["variants"][variant] = {
                "n": n,
                **{f"{k}_passed": v for k, v in counts.items()},
                **{f"{k}_ci95": wilson(v, n) for k, v in counts.items()},
            }
            out["calibration"][variant] = calibration(res, rng)

        def flags(variant, key):
            return [bool(r[key]) for r in variants[variant]["results"]]

        for mode, without, with_ in (
            ("sentence", "without_rerank", "with_rerank"),
            ("span", "span_without_rerank", "span_with_rerank"),
        ):
            out["rerank_effect"][mode] = {
                key: mcnemar(flags(without, key), flags(with_, key))
                for key in ("passed", "model_judge_pass", "top1_contains_gold")
            }
        for rr, sentence, span in (
            ("without_rerank", "without_rerank", "span_without_rerank"),
            ("with_rerank", "with_rerank", "span_with_rerank"),
        ):
            out["mode_effect"][rr] = {
                key: mcnemar(flags(sentence, key), flags(span, key))
                for key in ("passed", "model_judge_pass")
            }
        diag = rerank_exp["datasets"][dataset]["reranker_diagnostics"]
        helped, hurt = diag["top1_helped_gold"], diag["top1_hurt_gold"]
        out["reranker_sign_test"] = {
            "helped": helped,
            "hurt": hurt,
            "p_exact": round(binom_two_sided(helped, helped + hurt), 4),
        }
        payload["datasets"][dataset] = out
        sentence = out["rerank_effect"]["sentence"]
        print(
            f"{dataset}: judge without-only {sentence['model_judge_pass']['a_only']} "
            f"with-only {sentence['model_judge_pass']['b_only']} "
            f"p {sentence['model_judge_pass']['p_exact']}; "
            f"sign test {helped} vs {hurt} p {out['reranker_sign_test']['p_exact']}"
        )
    out_path = os.path.join(HERE, "results_paired_stats.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
