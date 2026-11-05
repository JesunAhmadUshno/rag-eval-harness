"""Level 2, Build runner: end-to-end pipeline evaluation, a budgeted
judge pass, and the agent protocol demo. Stdlib only.

Run: python level-2-build/run_build.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from agent_scoring import score_agent  # noqa: E402
from judge import BudgetedJudge, LexicalJudge  # noqa: E402
from pipeline import RagPipeline, load_corpus  # noqa: E402
from rag_eval import score_case  # noqa: E402


def evaluate_pipeline(pipe, cases):
    results = []
    for case in cases:
        out = pipe.answer(case["question"])
        scored = score_case(
            {
                "id": case["id"],
                "answer": out["answer"],
                "contexts": out["contexts"],
                "gold_facts": case["gold_facts"],
                "gold_answer": case["gold_answer"],
            }
        )
        results.append(scored)
    n = len(results)
    passed = sum(1 for r in results if r["passed"])
    label_counts = {}
    for r in results:
        for label in r["labels"]:
            label_counts[label] = label_counts.get(label, 0) + 1
    return {
        "n": n,
        "passed": passed,
        "pass_rate": passed / n if n else 0.0,
        "mean_faithfulness": sum(r["faithfulness"] for r in results) / n,
        "mean_context_recall": sum(r["context_recall"] for r in results) / n,
        "mean_answer_relevance": sum(r["answer_relevance"] for r in results) / n,
        "label_counts": label_counts,
        "results": results,
    }


DEMO_TASKS = [
    {"id": "a1", "prompt": "hours", "gold_answer": "opens at 8 am", "step_budget": 5},
    {"id": "a2", "prompt": "wifi", "gold_answer": "northlight guest network", "step_budget": 5},
    {"id": "a3", "prompt": "loans", "gold_answer": "borrow a book for three weeks", "step_budget": 5},
    {"id": "a4", "prompt": "rooms", "gold_answer": "study rooms hold up to six people", "step_budget": 5},
]


def careful_agent(task):
    table = {
        "hours": "opens at 8 am",
        "wifi": "northlight guest network",
        "loans": "borrow a book for three weeks",
        "rooms": "study rooms hold up to six people",
    }
    return {"answer": table[task["prompt"]], "steps": 2, "cost_units": 3}


def sloppy_agent(task):
    return {"answer": "the library is a nice place", "steps": 8, "cost_units": 9}


def main():
    corpus = load_corpus(os.path.join(HERE, "corpus.json"))
    with open(os.path.join(HERE, "golden_set_build.json"), encoding="utf-8") as fh:
        cases = json.load(fh)
    pipe = RagPipeline(corpus)
    summary = evaluate_pipeline(pipe, cases)
    print(f"Pipeline: {summary['passed']} of {summary['n']} passed, "
          f"pass rate {summary['pass_rate']:.3f}")
    print(f"Means: faithfulness {summary['mean_faithfulness']:.3f}, "
          f"recall {summary['mean_context_recall']:.3f}, "
          f"relevance {summary['mean_answer_relevance']:.3f}")
    print(f"Failure labels: {summary['label_counts']}")
    for r in summary["results"]:
        verdict = "PASS" if r["passed"] else "FAIL " + ",".join(r["labels"])
        print(f"  {r['id']}: faith {r['faithfulness']:.3f} "
              f"recall {r['context_recall']:.3f} rel {r['answer_relevance']:.3f} {verdict}")

    answers = [pipe.answer(c["question"])["answer"] for c in cases]
    contexts = [pipe.answer(c["question"])["contexts"] for c in cases]
    judge = BudgetedJudge(LexicalJudge(), max_calls=10, sample_rate=1.0, cost_per_call=1)
    enriched = [dict(c, gold_answer=c["gold_answer"]) for c in cases]
    verdicts = judge.judge_all(enriched, answers, contexts)
    judged = [v for v in verdicts if v is not None]
    judge_passed = sum(1 for v in judged if v["judge_pass"])
    print(f"Judge: {judge.calls_made} calls, cost {judge.total_cost}, "
          f"skipped {judge.calls_skipped}, judged pass {judge_passed} of {len(judged)}")

    for name, agent in (("careful", careful_agent), ("sloppy", sloppy_agent)):
        s = score_agent(agent, DEMO_TASKS)
        print(f"Agent {name}: success {s['success_rate']:.3f}, "
              f"mean steps {s['mean_steps']:.1f}, mean cost {s['mean_cost']:.1f}")


if __name__ == "__main__":
    main()
