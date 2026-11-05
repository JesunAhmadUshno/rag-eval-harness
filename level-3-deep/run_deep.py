"""Level 3, Deep runner: before and after reranking on the Deep golden
set, a budgeted judge pass, agent taxonomy demo runs, the failure
taxonomy, and the quality dashboard. Stdlib only.

Run: python level-3-deep/run_deep.py
Writes: level-3-deep/dashboard.md and level-3-deep/results_deep.json
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from agent_deep import score_agent_deep  # noqa: E402
from dashboard import write_dashboard  # noqa: E402
from judge import BudgetedJudge, LexicalJudge  # noqa: E402
from pipeline import load_corpus  # noqa: E402
from pipeline_deep import evaluate_cases  # noqa: E402
from taxonomy import build_taxonomy  # noqa: E402

DEMO_TASKS = [
    {"id": "a1", "prompt": "hours", "gold_answer": "opens at 8 am",
     "step_budget": 5, "expected_tool": "catalog"},
    {"id": "a2", "prompt": "wifi", "gold_answer": "northlight guest network",
     "step_budget": 5, "expected_tool": "catalog"},
    {"id": "a3", "prompt": "loans", "gold_answer": "borrow a book for three weeks",
     "step_budget": 5, "expected_tool": "catalog"},
    {"id": "a4", "prompt": "rooms", "gold_answer": "study rooms hold up to six people",
     "step_budget": 5, "expected_tool": "catalog"},
]

_ANSWERS = {
    "hours": "opens at 8 am",
    "wifi": "northlight guest network",
    "loans": "borrow a book for three weeks",
    "rooms": "study rooms hold up to six people",
}


def careful_agent(task):
    return {"answer": _ANSWERS[task["prompt"]], "steps": 2, "cost_units": 3,
            "tool_used": "catalog", "repeated_actions": False}


def loopy_agent(task):
    """Right tool, right answer, but trapped re-checking the same step."""
    return {"answer": _ANSWERS[task["prompt"]], "steps": 12, "cost_units": 11,
            "tool_used": "catalog", "repeated_actions": True}


def wrong_tool_agent(task):
    """Answers from a web search when the task requires the catalog tool."""
    return {"answer": "the library is a nice place", "steps": 3, "cost_units": 4,
            "tool_used": "web_search", "repeated_actions": False}


def silent_agent(task):
    """Wrong answer, normal steps, right tool: no distress signal at all."""
    return {"answer": "the library is a nice place", "steps": 2, "cost_units": 3,
            "tool_used": "catalog", "repeated_actions": False}


def sloppy_agent(task):
    """Wrong answer and over the step budget, from the Build demo."""
    return {"answer": "the library is a nice place", "steps": 8, "cost_units": 9,
            "tool_used": "catalog", "repeated_actions": False}


DEMO_AGENTS = [
    ("careful", careful_agent),
    ("loopy", loopy_agent),
    ("wrong_tool", wrong_tool_agent),
    ("silent", silent_agent),
    ("sloppy", sloppy_agent),
]


def run_all():
    corpus = load_corpus(os.path.join(HERE, "corpus_deep.json"))
    with open(os.path.join(HERE, "golden_set_deep.json"), encoding="utf-8") as fh:
        cases = json.load(fh)
    case_by_id = {c["id"]: c for c in cases}

    without = evaluate_cases(corpus, cases, use_rerank=False)
    with_rerank = evaluate_cases(corpus, cases, use_rerank=True)

    b11_ids = [c["id"] for c in cases if c.get("case_class") == "b11"]
    without_by_id = {r["id"]: r for r in without["results"]}
    with_by_id = {r["id"]: r for r in with_rerank["results"]}
    b11 = {
        "n": len(b11_ids),
        "ids": b11_ids,
        "passed_without": sum(1 for i in b11_ids if without_by_id[i]["passed"]),
        "passed_with": sum(1 for i in b11_ids if with_by_id[i]["passed"]),
    }

    from pipeline_deep import DeepRagPipeline

    pipe = DeepRagPipeline(corpus, use_rerank=True)
    answers, contexts_list = [], []
    for case in cases:
        out = pipe.answer(case["question"])
        answers.append(out["answer"])
        contexts_list.append(out["contexts"])
    judge = BudgetedJudge(LexicalJudge(), max_calls=15, sample_rate=1.0, cost_per_call=1)
    verdicts = judge.judge_all(cases, answers, contexts_list)
    judged = [v for v in verdicts if v is not None]
    judge_summary = {
        "calls_made": judge.calls_made,
        "calls_skipped": judge.calls_skipped,
        "total_cost": judge.total_cost,
        "judged": len(judged),
        "judged_passed": sum(1 for v in judged if v["judge_pass"]),
    }

    agent_results_all = []
    agent_summaries = {}
    for name, agent in DEMO_AGENTS:
        summary = score_agent_deep(agent, DEMO_TASKS)
        agent_summaries[name] = {
            "success_rate": summary["success_rate"],
            "mean_steps": summary["mean_steps"],
            "mean_cost": summary["mean_cost"],
        }
        agent_results_all.extend(summary["results"])

    # The RAG taxonomy counts the failures of the without-rerank run:
    # those are the actual failures the reranker was built against.
    # The with-rerank failure count is recorded separately below.
    taxonomy = build_taxonomy(without["results"], agent_results_all)
    taxonomy["total_failed"] = taxonomy["rag_failed"] + taxonomy["agent_failed"]
    taxonomy["total_labelled"] = (
        sum(taxonomy["rag_counts"].values()) + sum(taxonomy["agent_counts"].values())
    )

    summary = {
        "n": len(cases),
        "without": {k: without[k] for k in
                    ("n", "passed", "pass_rate", "mean_faithfulness",
                     "mean_context_recall", "mean_answer_relevance")},
        "with": {k: with_rerank[k] for k in
                 ("n", "passed", "pass_rate", "mean_faithfulness",
                  "mean_context_recall", "mean_answer_relevance")},
        "b11": b11,
        "judge": judge_summary,
        "taxonomy": taxonomy,
        "rag_failed_with": sum(1 for r in with_rerank["results"] if not r["passed"]),
        "agent_tasks": len(agent_results_all),
        "agent_summaries": agent_summaries,
        "with_results": with_rerank["results"],
        "without_results": without["results"],
        "agent_results": agent_results_all,
    }
    return summary, case_by_id


def main():
    summary, _ = run_all()
    print(f"Deep golden set: {summary['n']} cases")
    print(f"Without rerank: {summary['without']['passed']} passed, "
          f"pass rate {summary['without']['pass_rate']:.3f}")
    print(f"With rerank:    {summary['with']['passed']} passed, "
          f"pass rate {summary['with']['pass_rate']:.3f}")
    b11 = summary["b11"]
    print(f"b11 class: {b11['n']} cases, without {b11['passed_without']} passed, "
          f"with {b11['passed_with']} passed")
    print(f"Means (with): faithfulness {summary['with']['mean_faithfulness']:.3f}, "
          f"recall {summary['with']['mean_context_recall']:.3f}, "
          f"relevance {summary['with']['mean_answer_relevance']:.3f}")
    tax = summary["taxonomy"]
    print(f"Taxonomy: RAG {tax['rag_counts']} (failed {tax['rag_failed']}), "
          f"agent {tax['agent_counts']} (failed {tax['agent_failed']})")
    judge = summary["judge"]
    print(f"Judge: {judge['calls_made']} calls, cost {judge['total_cost']}, "
          f"skipped {judge['calls_skipped']}, judged pass "
          f"{judge['judged_passed']} of {judge['judged']}")
    for name, agent_summary in summary["agent_summaries"].items():
        print(f"Agent {name}: success {agent_summary['success_rate']:.3f}, "
              f"mean steps {agent_summary['mean_steps']:.1f}, "
              f"mean cost {agent_summary['mean_cost']:.1f}")
    for r in summary["with_results"]:
        if not r["passed"]:
            print(f"  FAIL with rerank: {r['id']} rel {r['answer_relevance']:.3f}")
    write_dashboard(summary, os.path.join(HERE, "dashboard.md"))
    record = {k: summary[k] for k in
              ("n", "without", "with", "b11", "judge", "taxonomy",
               "rag_failed_with", "agent_tasks", "agent_summaries")}
    record["with_passed_ids"] = [r["id"] for r in summary["with_results"] if r["passed"]]
    record["with_failed_ids"] = [r["id"] for r in summary["with_results"] if not r["passed"]]
    with open(os.path.join(HERE, "results_deep.json"), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1)
    print("Wrote dashboard.md and results_deep.json")


if __name__ == "__main__":
    main()
