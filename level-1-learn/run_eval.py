"""Run the Level 1 evaluator on the golden set and print the result table.

Usage: python level-1-learn/run_eval.py
Exit code 0 when the run completes. A failing case is data, not a crash:
the harness exists to name failures, so the summary prints either way.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_eval import score_all  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(os.path.join(HERE, "golden_set.json"), encoding="utf-8") as fh:
        cases = json.load(fh)
    summary = score_all(cases)
    print("case                              faith  recall  relev  verdict  labels")
    for r in summary["results"]:
        verdict = "PASS" if r["passed"] else "FAIL"
        labels = ",".join(r["labels"]) if r["labels"] else "-"
        print(
            f"{r['id']:<33} {r['faithfulness']:.3f}  {r['context_recall']:.3f}"
            f"   {r['answer_relevance']:.3f}  {verdict:<7}  {labels}"
        )
    print(
        f"summary: {summary['passed']} of {summary['n']} passed "
        f"(pass rate {summary['pass_rate']:.3f}); "
        f"mean faithfulness {summary['mean_faithfulness']:.3f}, "
        f"mean context recall {summary['mean_context_recall']:.3f}, "
        f"mean answer relevance {summary['mean_answer_relevance']:.3f}"
    )
    print("failure label counts:", summary["label_counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
