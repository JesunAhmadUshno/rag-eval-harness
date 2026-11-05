"""Build web/src/data/site-data.json from the recorded result files.

Every number on the dashboard comes from a file in this repo:
- Learn summary: computed here from level-1-learn/golden_set.json with
  the project's own rag_eval.py (same code the Learn run uses).
- Build summary: the measured run recorded in the root README benchmark
  table (2026-11-04), because the Build runner prints to stdout only.
- Deep summary: level-3-deep/results_deep.json.
- Real data: real-data/results_real.json plus the sample case files
  (joined by id for the simulator's gold facts). The per-case drill
  down rows come from the two reranked variants (sentence and span),
  trimmed for page size; the full records stay in results_real.json.
No number is typed in by hand except the Build row, whose source is
named in the JSON itself.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from rag_eval import score_all  # noqa: E402


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    learn_cases = load("level-1-learn", "golden_set.json")
    learn = score_all(learn_cases)
    for key in ("results",):
        learn.pop(key, None)

    deep = load("level-3-deep", "results_deep.json")
    real = load("real-data", "results_real.json")

    gold_facts = {}
    questions = {}
    for name in ("squad_cases.json", "hotpot_cases.json"):
        for case in load("real-data", "samples", name):
            gold_facts[case["id"]] = case["gold_facts"]
            questions[case["id"]] = case["question"]

    real_summary = {}
    real_cases = []
    sim_cases = []
    for dataset, variants in real["datasets"].items():
        real_summary[dataset] = {}
        for variant, run in variants.items():
            real_summary[dataset][variant] = {
                k: run[k]
                for k in (
                    "n",
                    "passed",
                    "pass_rate",
                    "mean_faithfulness",
                    "mean_context_recall",
                    "mean_answer_relevance",
                    "top1_contains_gold",
                    "label_counts",
                )
            }
            if "model_summary" in run:
                real_summary[dataset][variant]["model_summary"] = run[
                    "model_summary"
                ]
        for variant in ("with_rerank", "span_with_rerank"):
            for result in variants[variant]["results"]:
                real_cases.append(
                    {
                        "dataset": dataset,
                        "variant": variant,
                        "id": result["id"],
                        "question": result["question"][:140],
                        "gold_answer": result["gold_answer"],
                        "answer": result["system_answer"][:200],
                        "passed": result["passed"],
                        "model_judge_pass": result.get("model_judge_pass"),
                        "labels": result["labels"],
                        "answer_relevance": round(
                            result["answer_relevance"], 3
                        ),
                    }
                )
        for result in variants["with_rerank"]["results"][:4]:
            sim_cases.append(
                {
                    "id": result["id"],
                    "kind": f"real ({dataset})",
                    "question": result["question"],
                    "answer": result["system_answer"],
                    "contexts": result["contexts"],
                    "gold_answer": result["gold_answer"],
                    "gold_facts": gold_facts.get(
                        result["id"], [result["gold_answer"]]
                    ),
                }
            )

    for case in learn_cases[:4]:
        sim_cases.append(
            {
                "id": case["id"],
                "kind": "synthetic (Learn golden set)",
                "question": case.get("question", case["id"]),
                "answer": case["answer"],
                "contexts": case["contexts"],
                "gold_answer": case["gold_answer"],
                "gold_facts": case["gold_facts"],
            }
        )

    payload = {
        "generated": "2026-11-04",
        "learn": learn,
        "build": {
            "source": "Root README benchmark table, measured run 2026-11-04",
            "n": 20,
            "passed": 19,
            "pass_rate": 0.95,
            "mean_faithfulness": 1.0,
            "mean_context_recall": 1.0,
            "mean_answer_relevance": 0.97,
        },
        "deep": {
            "without": deep["without"],
            "with": deep["with"],
            "b11": deep["b11"],
            "taxonomy": deep["taxonomy"],
            "judge": deep["judge"],
        },
        "real": real_summary,
        "real_cases": real_cases,
        "model_judge": real["model_judge"],
        "sim_cases": sim_cases,
    }
    out = os.path.join(HERE, "src", "data", "site-data.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
