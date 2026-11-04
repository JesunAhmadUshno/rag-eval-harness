"""Level 3, Deep: failure taxonomies for RAG cases and agent tasks.

Every failed item gets exactly ONE primary label, chosen by the
priority order in each function. That rule is deliberate: the counts
in a taxonomy table then sum to the number of failures, so a reader
can check the table against the run totals by hand.

RAG labels (priority order):
- hallucination: faithfulness below the pass line.
- retrieval_miss: context recall below the pass line.
- wrong_passage_on_top: recall and faithfulness pass, relevance fails.
  The right document and the gold fact were retrieved, but the top
  passage does not answer the question. This is the b11 class.
- wrong_or_incomplete_answer: relevance fails for any other reason.

Agent labels (priority order), from the SPEC Deep scope:
- loop_trap: repeated actions, or steps at or above twice the budget.
- tool_misuse: the agent used a tool other than the task expected tool.
- excess_steps: steps above budget (but below the loop trap line).
- silent_wrong_answer: relevance fails, steps and tool look normal.
  The agent returned a wrong answer with no visible distress signal.
- failed_task: relevance fails for any other reason.
"""

PASS_FAITHFULNESS = 0.80
PASS_RECALL = 0.80
PASS_RELEVANCE = 0.50


def rag_primary_label(result):
    """One primary label for a scored RAG case, or None when it passed."""
    if result["passed"]:
        return None
    if result["faithfulness"] < PASS_FAITHFULNESS:
        return "hallucination"
    if result["context_recall"] < PASS_RECALL:
        return "retrieval_miss"
    if result["answer_relevance"] < PASS_RELEVANCE:
        return "wrong_passage_on_top"
    return "wrong_or_incomplete_answer"


def agent_primary_label(task_result):
    """One primary label for a scored agent task, or None on success.

    task_result keys: relevance, steps, step_budget, tool_used,
    expected_tool, repeated_actions (bool).
    A task counts as failed when it carries a primary label. A correct
    answer delivered inside a loop trap or with the wrong tool is
    still a failure of process, and is labelled as one.
    """
    steps = task_result["steps"]
    budget = task_result["step_budget"]
    if task_result.get("repeated_actions") or steps >= 2 * budget:
        return "loop_trap"
    if task_result.get("tool_used") != task_result.get("expected_tool"):
        return "tool_misuse"
    if steps > budget:
        return "excess_steps"
    if task_result["relevance"] < PASS_RELEVANCE:
        return "silent_wrong_answer"
    return None


def build_taxonomy(rag_results, agent_results):
    """Count primary labels. Returns counts plus failure totals.

    rag_results: scored cases from the Learn scorer (dicts with the
    metric keys and a passed flag).
    agent_results: dicts accepted by agent_primary_label, each with
    an id key.
    """
    rag_counts = {}
    rag_failed = 0
    for result in rag_results:
        label = rag_primary_label(result)
        if label is not None:
            rag_failed += 1
            rag_counts[label] = rag_counts.get(label, 0) + 1
    agent_counts = {}
    agent_failed = 0
    for result in agent_results:
        label = agent_primary_label(result)
        if label is not None:
            agent_failed += 1
            agent_counts[label] = agent_counts.get(label, 0) + 1
    return {
        "rag_counts": rag_counts,
        "rag_failed": rag_failed,
        "agent_counts": agent_counts,
        "agent_failed": agent_failed,
        "total_failed": rag_failed + agent_failed,
        "total_labelled": sum(rag_counts.values()) + sum(agent_counts.values()),
    }
