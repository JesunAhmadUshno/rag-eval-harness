"""Run the confirmatory cycle locked in docs/decisions/0004.

Runs the committed harness (real-data/run_real_eval.py's run_dataset,
unmodified) on the confirmatory slices fetched by
fetch_confirmatory.py, and computes exactly the locked analysis:

- Primary (H-C1): SQuAD, sentence vs span, no rerank, Level 1 lexical
  pass, exact McNemar at alpha 0.05; CONFIRMED iff span passes exceed
  sentence passes AND p < 0.05.
- Secondary (H-C2): the same on HotpotQA, reported separately.
- Effect: pass rates with Wilson 95% intervals, discordant counts,
  and the paired pass-rate difference with a percentile bootstrap
  95% interval (10,000 resamples, seed 20261117, the seed fixed in
  the lock).

The rerank-on variants are run and recorded but are exploratory only,
as the lock states. The embedding judge is not run (not part of the
locked analysis). Stdlib only.

Run: python real-data/confirmatory/run_confirmatory.py
Writes: real-data/confirmatory/results_confirmatory.json (new file)
"""

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REAL = os.path.dirname(HERE)
ROOT = os.path.dirname(REAL)
sys.path.insert(0, REAL)
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))
sys.path.insert(0, os.path.join(ROOT, "model-metrics"))

from paired_stats import mcnemar, wilson  # noqa: E402
from run_real_eval import VARIANTS, run_dataset  # noqa: E402

SEED = 20261117
BOOTSTRAP_RUNS = 10000
ALPHA = 0.05


def load_json(name):
    with open(os.path.join(HERE, "samples", name), encoding="utf-8") as fh:
        return json.load(fh)


def bootstrap_diff_ci(a_flags, b_flags, rng):
    """Percentile bootstrap 95% CI for mean(b) - mean(a), paired resampling."""
    n = len(a_flags)
    diffs = [int(y) - int(x) for x, y in zip(a_flags, b_flags)]
    boots = []
    for _ in range(BOOTSTRAP_RUNS):
        idx = [rng.randrange(n) for _ in range(n)]
        boots.append(sum(diffs[i] for i in idx) / n)
    boots.sort()
    return [
        round(boots[int(0.025 * BOOTSTRAP_RUNS)], 4),
        round(boots[int(0.975 * BOOTSTRAP_RUNS) - 1], 4),
    ]


def locked_test(sentence_flags, span_flags, rng):
    """The analysis fixed in docs/decisions/0004 for one dataset."""
    mc = mcnemar(sentence_flags, span_flags)
    n = len(sentence_flags)
    s_pass = sum(sentence_flags)
    p_pass = sum(span_flags)
    verdict = (
        "CONFIRMED"
        if p_pass > s_pass and mc["p_exact"] < ALPHA
        else "NOT CONFIRMED"
    )
    return {
        "n": n,
        "sentence_passed": s_pass,
        "sentence_rate": round(s_pass / n, 4),
        "sentence_ci95": wilson(s_pass, n),
        "span_passed": p_pass,
        "span_rate": round(p_pass / n, 4),
        "span_ci95": wilson(p_pass, n),
        "difference_span_minus_sentence": round((p_pass - s_pass) / n, 4),
        "difference_ci95_bootstrap": bootstrap_diff_ci(
            sentence_flags, span_flags, rng
        ),
        "mcnemar": mc,
        "alpha": ALPHA,
        "verdict": verdict,
    }


def main():
    rng = random.Random(SEED)
    payload = {
        "generated_by": "real-data/confirmatory/run_confirmatory.py",
        "lock": "docs/decisions/0004-confirmatory-lock-span-extraction.md (2026-11-17)",
        "data_kind": (
            "real public datasets, confirmatory slices disjoint from the "
            "exploratory samples: SQuAD validation rows 5000-9999 every "
            "10th (500 cases); HotpotQA distractor validation rows "
            "200-699 (500 cases); corpora built from those rows only"
        ),
        "metric": "Level 1 lexical pass (pass lines 0.8 / 0.8 / 0.5)",
        "paired_test": "exact McNemar (two-sided binomial on discordant pairs, p = 0.5)",
        "bootstrap": {"runs": BOOTSTRAP_RUNS, "seed": SEED},
        "datasets": {},
    }
    for key, cases_name, corpus_name, role in [
        ("squad", "squad_cases.json", "squad_corpus.json", "primary H-C1"),
        ("hotpotqa", "hotpot_cases.json", "hotpot_corpus.json", "secondary H-C2"),
    ]:
        cases = load_json(cases_name)
        corpus = load_json(corpus_name)
        runs = {}
        for variant_name, use_rerank, answer_mode in VARIANTS:
            run = run_dataset(cases, corpus, use_rerank, answer_mode)
            runs[variant_name] = run
            print(
                f"{key} {variant_name}: {run['passed']}/{run['n']} passed "
                f"({run['pass_rate']})"
            )

        def flags(variant):
            return [bool(r["passed"]) for r in runs[variant]["results"]]

        entry = {
            "role": role,
            "n_cases": len(cases),
            "n_documents": len(corpus),
            "n_passages": sum(len(d["sentences"]) for d in corpus),
            "variants": {
                name: {
                    "passed": runs[name]["passed"],
                    "n": runs[name]["n"],
                    "pass_rate": runs[name]["pass_rate"],
                    "pass_ci95": wilson(runs[name]["passed"], runs[name]["n"]),
                    "mean_answer_relevance": runs[name]["mean_answer_relevance"],
                    "mean_context_recall": runs[name]["mean_context_recall"],
                    "top1_contains_gold": runs[name]["top1_contains_gold"],
                }
                for name, _, _ in VARIANTS
            },
            "locked_test_no_rerank": locked_test(
                flags("without_rerank"), flags("span_without_rerank"), rng
            ),
            "exploratory_only": {
                "locked_test_with_rerank_descriptive": locked_test(
                    flags("with_rerank"), flags("span_with_rerank"), rng
                ),
                "note": (
                    "Computed with the same code for completeness; "
                    "exploratory only under the lock, no confirmatory weight."
                ),
            },
            "per_case_passed": {
                name: [bool(r["passed"]) for r in runs[name]["results"]]
                for name, _, _ in VARIANTS
            },
            "case_ids": [c["id"] for c in cases],
        }
        payload["datasets"][key] = entry
        lt = entry["locked_test_no_rerank"]
        print(
            f"{key} LOCKED TEST ({role}): sentence {lt['sentence_passed']}, "
            f"span {lt['span_passed']}, McNemar discordants "
            f"{lt['mcnemar']['a_only']} vs {lt['mcnemar']['b_only']}, "
            f"p {lt['mcnemar']['p_exact']}, verdict {lt['verdict']}"
        )
    out_path = os.path.join(HERE, "results_confirmatory.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
