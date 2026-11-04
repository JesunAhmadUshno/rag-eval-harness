"""Level 3, Deep: the CI regression gate named in the SPEC Deep scope.

The gate runs the full Deep golden set with reranking, then compares
the result against the recorded baseline in baseline.json:

- the pass rate must be at or above the baseline threshold, and
- no case that passed in the baseline may fail now.

Exit code 0 means the gate passed. Exit code 1 means a regression:
the failing case ids and the pass rate are printed so CI logs name
exactly what broke. This module is the regression test; the baseline
is only ever updated by a deliberate, reviewed run of run_deep.py
followed by recording the new numbers here, never automatically.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))

from pipeline import load_corpus  # noqa: E402
from pipeline_deep import evaluate_cases  # noqa: E402


def load_baseline(path=None):
    with open(path or os.path.join(HERE, "baseline.json"), encoding="utf-8") as fh:
        return json.load(fh)


def check_regression(current_results, baseline):
    """Compare scored results against a baseline dict.

    baseline keys: threshold (float), passed_ids (list of case ids).
    Returns (ok, problems) where problems is a list of strings.
    """
    n = len(current_results)
    passed_ids = {r["id"] for r in current_results if r["passed"]}
    pass_rate = len(passed_ids) / n if n else 0.0
    problems = []
    if pass_rate < baseline["threshold"]:
        problems.append(
            f"pass rate {pass_rate:.3f} is below threshold {baseline['threshold']:.3f}"
        )
    for case_id in baseline["passed_ids"]:
        if case_id not in passed_ids:
            problems.append(f"regressed case: {case_id}")
    return (not problems), problems


def main(argv=None):
    baseline = load_baseline()
    corpus = load_corpus(os.path.join(HERE, "corpus_deep.json"))
    with open(os.path.join(HERE, "golden_set_deep.json"), encoding="utf-8") as fh:
        cases = json.load(fh)
    summary = evaluate_cases(corpus, cases, use_rerank=True)
    ok, problems = check_regression(summary["results"], baseline)
    print(f"Regression gate: pass rate {summary['pass_rate']:.3f} "
          f"({summary['passed']} of {summary['n']}), "
          f"threshold {baseline['threshold']:.3f}")
    if ok:
        print("Regression gate: PASS")
        return 0
    for problem in problems:
        print(f"Regression gate: FAIL {problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
