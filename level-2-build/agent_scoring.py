"""Level 2, Build: agent task protocol scoring.

Protocol: an agent is any callable agent(task) -> dict with keys
  answer (str), steps (int), cost_units (number).
A task is a dict with keys id, prompt, gold_answer, step_budget.

A task succeeds when the answer token F1 against the gold answer is at
least 0.50 (the same relevance line as the RAG pass rule). Labels:
- failed_task: relevance below the line.
- excess_steps: steps above the task step budget.
- excess_cost: reserved for Deep level cost bands; not emitted here.
The summary reports success rate, mean steps, and mean cost per task,
so any agent speaking this protocol is scored the same way a RAG
pipeline is scored: pass rate first, then the cost of getting there.
"""

import os
import sys

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "level-1-learn"
    ),
)
from rag_eval import answer_relevance  # noqa: E402

PASS_RELEVANCE = 0.50


def score_agent(agent, tasks):
    results = []
    for task in tasks:
        out = agent(task)
        relevance = answer_relevance(out["answer"], task["gold_answer"])
        labels = []
        if relevance < PASS_RELEVANCE:
            labels.append("failed_task")
        if out["steps"] > task["step_budget"]:
            labels.append("excess_steps")
        results.append(
            {
                "id": task["id"],
                "relevance": round(relevance, 3),
                "steps": out["steps"],
                "cost_units": out["cost_units"],
                "passed": not labels,
                "labels": labels,
            }
        )
    n = len(results)
    succeeded = sum(1 for r in results if "failed_task" not in r["labels"])
    return {
        "n": n,
        "succeeded": succeeded,
        "success_rate": succeeded / n if n else 0.0,
        "mean_steps": sum(r["steps"] for r in results) / n if n else 0.0,
        "mean_cost": sum(r["cost_units"] for r in results) / n if n else 0.0,
        "results": results,
    }
