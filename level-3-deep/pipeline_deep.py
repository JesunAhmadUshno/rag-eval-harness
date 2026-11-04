"""Level 3, Deep: the Build pipeline plus the reranking step.

DeepRagPipeline retrieves the same top-k BM25 passages as Build, then
optionally reranks them with reranker.rerank before the extractive
answer step takes the top passage. use_rerank=False reproduces the
Build behaviour exactly, which is how the before and after numbers in
the Deep README are measured on the same golden set.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
sys.path.insert(0, HERE)

from pipeline import RagPipeline  # noqa: E402
from reranker import rerank  # noqa: E402
from rag_eval import score_case  # noqa: E402


class DeepRagPipeline(RagPipeline):
    def __init__(self, corpus, top_k=5, use_rerank=True):
        super().__init__(corpus, top_k=top_k)
        self.use_rerank = use_rerank

    def answer(self, question):
        hits = self.index.search_passages(question, top_k=self.top_k)
        if self.use_rerank:
            hits = rerank(question, hits)
        contexts = [text for text, _ in hits]
        return {
            "answer": contexts[0] if contexts else "",
            "contexts": contexts,
            "scores": [score for _, score in hits],
        }


def evaluate_cases(corpus, cases, use_rerank):
    """Run the Deep pipeline over cases and score with the Learn scorer."""
    pipe = DeepRagPipeline(corpus, use_rerank=use_rerank)
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
        scored["answer"] = out["answer"]
        scored["top_context"] = out["contexts"][0] if out["contexts"] else ""
        results.append(scored)
    n = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "n": n,
        "passed": passed,
        "pass_rate": passed / n if n else 0.0,
        "mean_faithfulness": sum(r["faithfulness"] for r in results) / n if n else 0.0,
        "mean_context_recall": sum(r["context_recall"] for r in results) / n if n else 0.0,
        "mean_answer_relevance": sum(r["answer_relevance"] for r in results) / n if n else 0.0,
        "results": results,
    }
