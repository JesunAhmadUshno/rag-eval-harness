"""Run the harness on the real-data samples and write results_real.json.

Method, stated plainly so the numbers can be checked:
- Retrieval and answering use the project's own pipeline: BM25 over
  sentences with an extractive top-passage answer (level-2-build), run
  with and without the stemmed-overlap reranker (level-3-deep).
- Scoring uses the Level 1 lexical metrics (level-1-learn/rag_eval.py)
  and the embedding judge (model-metrics/embedding_judge.py) when the
  model is available. If the model cannot load, the lexical run still
  completes and the model section is recorded as not run, with the
  reason, never as zeros presented as scores.
- Results are reported per dataset, separate from every synthetic set.
  Nothing in this file mixes real and synthetic numbers.

Run with a Python that has model2vec installed for the model section:
  python real-data/run_real_eval.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))
sys.path.insert(0, os.path.join(ROOT, "model-metrics"))

from pipeline_deep import DeepRagPipeline  # noqa: E402
from rag_eval import score_case  # noqa: E402


def load_json(name):
    with open(os.path.join(HERE, "samples", name), encoding="utf-8") as fh:
        return json.load(fh)


def run_dataset(cases, corpus, use_rerank):
    pipe = DeepRagPipeline(corpus, top_k=5, use_rerank=use_rerank)
    per_case = []
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
        scored["system_answer"] = out["answer"]
        scored["question"] = case["question"]
        scored["gold_answer"] = case["gold_answer"]
        scored["contexts"] = out["contexts"]
        per_case.append(scored)
    n = len(per_case)
    label_counts = {}
    for result in per_case:
        for label in result["labels"]:
            label_counts[label] = label_counts.get(label, 0) + 1
    return {
        "n": n,
        "passed": sum(1 for r in per_case if r["passed"]),
        "pass_rate": round(sum(1 for r in per_case if r["passed"]) / n, 4)
        if n
        else 0.0,
        "mean_faithfulness": round(
            sum(r["faithfulness"] for r in per_case) / n, 4
        )
        if n
        else 0.0,
        "mean_context_recall": round(
            sum(r["context_recall"] for r in per_case) / n, 4
        )
        if n
        else 0.0,
        "mean_answer_relevance": round(
            sum(r["answer_relevance"] for r in per_case) / n, 4
        )
        if n
        else 0.0,
        "label_counts": label_counts,
        "results": per_case,
    }


def add_model_scores(dataset_runs):
    """Attach embedding judge scores per case and summary means."""
    from embedding_judge import EmbeddingJudge, Model2VecEmbedder, ModelUnavailable

    judge = EmbeddingJudge(Model2VecEmbedder())
    try:
        # Probe the model once before scoring anything.
        judge.embedder(["probe"])
    except ModelUnavailable as exc:
        return {"status": "not_run", "reason": str(exc)}
    for run in dataset_runs.values():
        for variant in run.values():
            sims, sups, passes = [], [], 0
            for result in variant["results"]:
                verdict = judge(
                    {"gold_answer": result["gold_answer"]},
                    result["system_answer"],
                    result["contexts"],
                )
                result["semantic_answer_similarity"] = verdict[
                    "semantic_answer_similarity"
                ]
                result["semantic_support"] = verdict["semantic_support"]
                result["model_judge_pass"] = verdict["judge_pass"]
                sims.append(verdict["semantic_answer_similarity"])
                sups.append(verdict["semantic_support"])
                passes += 1 if verdict["judge_pass"] else 0
            n = len(variant["results"])
            variant["model_summary"] = {
                "mean_semantic_answer_similarity": round(sum(sims) / n, 4)
                if n
                else 0.0,
                "mean_semantic_support": round(sum(sups) / n, 4) if n else 0.0,
                "model_judge_passed": passes,
                "model_judge_pass_rate": round(passes / n, 4) if n else 0.0,
            }
    return {"status": "ran", "model": judge.model_name}


def main():
    datasets = {}
    for key, cases_name, corpus_name in [
        ("squad", "squad_cases.json", "squad_corpus.json"),
        ("hotpotqa", "hotpot_cases.json", "hotpot_corpus.json"),
    ]:
        cases = load_json(cases_name)
        corpus = load_json(corpus_name)
        datasets[key] = {
            "without_rerank": run_dataset(cases, corpus, use_rerank=False),
            "with_rerank": run_dataset(cases, corpus, use_rerank=True),
        }
        for variant, run in datasets[key].items():
            print(
                f"{key} {variant}: {run['passed']}/{run['n']} passed "
                f"({run['pass_rate']}), recall {run['mean_context_recall']}, "
                f"relevance {run['mean_answer_relevance']}"
            )
    model_section = add_model_scores(datasets)
    print("model judge:", model_section)
    payload = {
        "generated": "2026-11-04",
        "data_kind": "real public datasets (see DATASETS.md); not synthetic",
        "method": (
            "BM25 retrieval plus extractive top-passage answer "
            "(level-2-build pipeline), with and without the level-3 "
            "stemmed-overlap reranker; Level 1 lexical metrics; "
            "embedding judge from model-metrics when available."
        ),
        "model_judge": model_section,
        "datasets": datasets,
    }
    out_path = os.path.join(HERE, "results_real.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
