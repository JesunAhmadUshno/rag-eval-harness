"""Level 3, Deep: agent scoring with the Deep failure taxonomy.

The Build protocol scores success, steps, and cost. Deep keeps that
protocol and adds the fields the taxonomy needs: each agent returns
tool_used and repeated_actions beside answer, steps, and cost_units,
and each task names its expected_tool. Scoring is still the same
relevance line as Build (token F1 at least 0.50 against the gold
answer); the primary failure label comes from taxonomy.py, one label
per failed task, so the taxonomy counts sum to the failure total.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
sys.path.insert(0, HERE)

from rag_eval import answer_relevance  # noqa: E402
from taxonomy import agent_primary_label  # noqa: E402


def score_agent_deep(agent, tasks):
    results = []
    for task in tasks:
        out = agent(task)
        relevance = answer_relevance(out["answer"], task["gold_answer"])
        record = {
            "id": task["id"],
            "relevance": round(relevance, 3),
            "steps": out["steps"],
            "step_budget": task["step_budget"],
            "cost_units": out["cost_units"],
            "tool_used": out.get("tool_used", task["expected_tool"]),
            "expected_tool": task["expected_tool"],
            "repeated_actions": bool(out.get("repeated_actions", False)),
        }
        record["label"] = agent_primary_label(record)
        record["passed"] = record["label"] is None
        results.append(record)
    n = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "n": n,
        "passed": passed,
        "success_rate": passed / n if n else 0.0,
        "mean_steps": sum(r["steps"] for r in results) / n if n else 0.0,
        "mean_cost": sum(r["cost_units"] for r in results) / n if n else 0.0,
        "results": results,
    }
