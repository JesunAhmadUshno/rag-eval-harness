"""Reranker transfer experiment (v1.2): why the synthetic win stalls.

The v1.1 finding: the stemmed-overlap reranker took the synthetic
Deep set from 0.719 to 1.000 and changed almost nothing on real data.
This script tests concrete explanations and candidate fixes on the
real samples, with the same before and after discipline:

Variants (all return 5 contexts; the answer is the top context):
- bm25: plain BM25 order.
- current: the shipped reranker (coverage, then F1, then BM25)
  over the BM25 top 5.
- hybrid_a: a hybrid key, alpha * normalised BM25 + (1 - alpha) *
  stemmed coverage, over the BM25 top 5, for alpha in 0.3, 0.5, 0.7.
- current_pool10: the shipped reranker over the BM25 top 10.
- hybrid_pool10: the best hybrid alpha over the BM25 top 10.

Measurements per variant: mean context recall, the share of cases
whose top passage contains the gold answer text (the direct test of
what a reranker can change on this pipeline, since contexts are a
set and only the top passage feeds the answer), lexical pass rate,
and mean answer relevance, all with the sentence answer step so the
reranker is the only moving part.

Diagnostics for the shipped reranker: how often it changes the top
passage, how often that change helps or hurts gold containment, and
the mean length of the passages it promotes versus the ones it
demotes (the short-passage bias check: stemmed F1 rewards short
passages, because precision divides by passage length).

Output: results_rerank_experiment.json. Nothing in this file touches
the synthetic sets; real and synthetic numbers are never mixed.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))

from pipeline import BM25Index, content_tokens  # noqa: E402
from rag_eval import context_recall, score_case  # noqa: E402
from reranker import overlap_scores, rerank  # noqa: E402

NORM_RE = re.compile(r"[^a-z0-9]+")


def load_json(name):
    with open(os.path.join(HERE, "samples", name), encoding="utf-8") as fh:
        return json.load(fh)


def contains_gold(text, gold):
    norm_text = " " + NORM_RE.sub(" ", text.lower()).strip() + " "
    norm_gold = " " + NORM_RE.sub(" ", gold.lower()).strip() + " "
    return norm_gold in norm_text


def hybrid_rerank(query, hits, alpha):
    """Reorder hits by alpha * normalised BM25 + (1 - alpha) * coverage."""
    if not hits:
        return list(hits)
    top_score = max(score for _, score in hits) or 1.0
    decorated = []
    for idx, (text, score) in enumerate(hits):
        coverage, f1 = overlap_scores(query, text)
        key = alpha * (score / top_score) + (1 - alpha) * coverage
        decorated.append((text, score, key, f1, idx))
    decorated.sort(key=lambda item: (-item[2], -item[3], -item[1], item[4]))
    return [(text, score) for text, score, _, _, _ in decorated]


def measure(cases, contexts_per_case):
    """Score a list of per-case context lists with the sentence answer."""
    recalls, passes, relevances, top1_gold = [], 0, [], 0
    for case, contexts in zip(cases, contexts_per_case):
        recalls.append(context_recall(contexts, case["gold_facts"]))
        if contexts and contains_gold(contexts[0], case["gold_answer"]):
            top1_gold += 1
        scored = score_case(
            {
                "id": case["id"],
                "answer": contexts[0] if contexts else "",
                "contexts": contexts,
                "gold_facts": case["gold_facts"],
                "gold_answer": case["gold_answer"],
            }
        )
        passes += 1 if scored["passed"] else 0
        relevances.append(scored["answer_relevance"])
    n = len(cases)
    return {
        "n": n,
        "mean_context_recall": round(sum(recalls) / n, 4) if n else 0.0,
        "top1_contains_gold": top1_gold,
        "top1_contains_gold_rate": round(top1_gold / n, 4) if n else 0.0,
        "passed": passes,
        "pass_rate": round(passes / n, 4) if n else 0.0,
        "mean_answer_relevance": round(sum(relevances) / n, 4) if n else 0.0,
    }


def run_dataset(cases, corpus):
    index = BM25Index(corpus)
    pools5, pools10 = [], []
    for case in cases:
        pools10.append(index.search_passages(case["question"], top_k=10))
        pools5.append(pools10[-1][:5])

    def contexts(pool_lists, fn):
        return [[text for text, _ in fn(case, pool)] for case, pool in zip(cases, pool_lists)]

    variants = {
        "bm25": contexts(pools5, lambda case, pool: pool),
        "current": contexts(pools5, lambda case, pool: rerank(case["question"], pool)),
        "current_pool10": contexts(
            pools10, lambda case, pool: rerank(case["question"], pool)[:5]
        ),
    }
    for alpha in (0.3, 0.5, 0.7):
        variants[f"hybrid_{alpha}"] = contexts(
            pools5,
            lambda case, pool, a=alpha: hybrid_rerank(case["question"], pool, a),
        )
        variants[f"hybrid_pool10_{alpha}"] = contexts(
            pools10,
            lambda case, pool, a=alpha: hybrid_rerank(case["question"], pool, a)[:5],
        )
    results = {name: measure(cases, ctx) for name, ctx in variants.items()}

    # Diagnostics on the shipped reranker over the top 5.
    changed = helped = hurt = 0
    promoted_lens, demoted_lens = [], []
    for case, pool in zip(cases, pools5):
        if not pool:
            continue
        reordered = rerank(case["question"], pool)
        if reordered[0][0] == pool[0][0]:
            continue
        changed += 1
        before = contains_gold(pool[0][0], case["gold_answer"])
        after = contains_gold(reordered[0][0], case["gold_answer"])
        if after and not before:
            helped += 1
        elif before and not after:
            hurt += 1
        promoted_lens.append(len(content_tokens(reordered[0][0])))
        demoted_lens.append(len(content_tokens(pool[0][0])))
    diagnostics = {
        "top1_changed": changed,
        "top1_helped_gold": helped,
        "top1_hurt_gold": hurt,
        "mean_promoted_passage_tokens": round(
            sum(promoted_lens) / len(promoted_lens), 2
        )
        if promoted_lens
        else 0.0,
        "mean_demoted_passage_tokens": round(
            sum(demoted_lens) / len(demoted_lens), 2
        )
        if demoted_lens
        else 0.0,
    }
    return {"variants": results, "reranker_diagnostics": diagnostics}


def main():
    payload = {
        "generated": "2026-11-04",
        "data_kind": "real public datasets (see DATASETS.md); not synthetic",
        "method": (
            "BM25 pools of 5 and 10 from the project pipeline; rerank "
            "variants as documented in this file's docstring; sentence "
            "answer step; Level 1 lexical metrics."
        ),
        "datasets": {},
    }
    for key, cases_name, corpus_name in [
        ("squad", "squad_cases.json", "squad_corpus.json"),
        ("hotpotqa", "hotpot_cases.json", "hotpot_corpus.json"),
    ]:
        cases = load_json(cases_name)
        corpus = load_json(corpus_name)
        payload["datasets"][key] = run_dataset(cases, corpus)
        print(f"== {key} ({len(cases)} cases)")
        for name, m in payload["datasets"][key]["variants"].items():
            print(
                f"  {name:18s} recall {m['mean_context_recall']:.3f} "
                f"top1-gold {m['top1_contains_gold']:3d}/{m['n']} "
                f"pass {m['passed']:3d} rel {m['mean_answer_relevance']:.3f}"
            )
        print("  diagnostics:", payload["datasets"][key]["reranker_diagnostics"])
    out_path = os.path.join(HERE, "results_rerank_experiment.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
