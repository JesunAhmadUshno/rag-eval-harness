"""Level 1, Learn: a tiny deterministic RAG evaluator. Stdlib only.

Three lexical metrics, each in the open so a reader can check them by hand:

- context_recall: how many of the gold facts the retrieved context covers.
  A fact counts as covered when at least 80 percent of its content tokens
  appear in the retrieved context.
- faithfulness: how much of the answer is supported by the context.
  The share of answer content tokens that appear in the context.
- answer_relevance: how close the answer is to the gold answer.
  The token F1 between the answer and the gold answer. This is a lexical
  proxy: it misses paraphrases. An LLM judge is Build level work (PROPOSAL.md).

A case passes when faithfulness >= 0.80, context_recall >= 0.80, and
answer_relevance >= 0.50. Every failed case gets one or more labels from
the seed failure taxonomy: hallucination, retrieval_miss,
wrong_or_incomplete_answer.
"""

import math
import re

STOPWORDS = frozenset(
    "a an the is are was were be been of to in on for and or as at by "
    "it its this that these those from with without into over under".split()
)

TOKEN_RE = re.compile(r"[a-z0-9]+")

RECALL_COVERAGE = 0.80
PASS_FAITHFULNESS = 0.80
PASS_RECALL = 0.80
PASS_RELEVANCE = 0.50


def content_tokens(text):
    """Lowercase word and number tokens, stopwords removed, order kept."""
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def _token_set(text):
    return set(content_tokens(text))


def faithfulness(answer, contexts):
    """Share of answer content tokens supported by the context. 0.0 to 1.0."""
    answer_tokens = _token_set(answer)
    if not answer_tokens:
        return 0.0
    context_tokens = set()
    for chunk in contexts:
        context_tokens |= _token_set(chunk)
    return len(answer_tokens & context_tokens) / len(answer_tokens)


def context_recall(contexts, gold_facts):
    """Share of gold facts covered by the context. 0.0 to 1.0."""
    if not gold_facts:
        return 0.0
    context_tokens = set()
    for chunk in contexts:
        context_tokens |= _token_set(chunk)
    covered = 0
    for fact in gold_facts:
        fact_tokens = _token_set(fact)
        if not fact_tokens:
            continue
        overlap = len(fact_tokens & context_tokens) / len(fact_tokens)
        if overlap >= RECALL_COVERAGE:
            covered += 1
    return covered / len(gold_facts)


def answer_relevance(answer, gold_answer):
    """Token F1 between the answer and the gold answer. 0.0 to 1.0."""
    answer_tokens = _token_set(answer)
    gold_tokens = _token_set(gold_answer)
    if not answer_tokens or not gold_tokens:
        return 0.0
    shared = len(answer_tokens & gold_tokens)
    if shared == 0:
        return 0.0
    precision = shared / len(answer_tokens)
    recall = shared / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def failure_labels(scores):
    """Seed failure taxonomy: one label per metric below its pass line."""
    labels = []
    if scores["faithfulness"] < PASS_FAITHFULNESS:
        labels.append("hallucination")
    if scores["context_recall"] < PASS_RECALL:
        labels.append("retrieval_miss")
    if scores["answer_relevance"] < PASS_RELEVANCE:
        labels.append("wrong_or_incomplete_answer")
    return labels


def score_case(case):
    """Score one golden case. Returns the metrics, pass flag, and labels."""
    scores = {
        "faithfulness": faithfulness(case["answer"], case["contexts"]),
        "context_recall": context_recall(case["contexts"], case["gold_facts"]),
        "answer_relevance": answer_relevance(case["answer"], case["gold_answer"]),
    }
    labels = failure_labels(scores)
    return {
        "id": case["id"],
        **scores,
        "passed": not labels,
        "labels": labels,
    }


def score_all(cases):
    """Score every case and summarise: pass rate, means, label counts."""
    results = [score_case(case) for case in cases]
    n = len(results)
    label_counts = {}
    for result in results:
        for label in result["labels"]:
            label_counts[label] = label_counts.get(label, 0) + 1
    passed = sum(1 for r in results if r["passed"])
    return {
        "n": n,
        "passed": passed,
        "pass_rate": passed / n if n else 0.0,
        "mean_faithfulness": math.fsum(r["faithfulness"] for r in results) / n if n else 0.0,
        "mean_context_recall": math.fsum(r["context_recall"] for r in results) / n if n else 0.0,
        "mean_answer_relevance": math.fsum(r["answer_relevance"] for r in results) / n if n else 0.0,
        "label_counts": label_counts,
        "results": results,
    }
