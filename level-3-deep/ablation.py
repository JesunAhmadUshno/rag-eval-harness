"""Ablation of the stemmed-overlap reranker. Stdlib only, runs in seconds.

reranker.py combines two choices: five stem rules and a three-key sort
(stemmed coverage, then stemmed F1, then BM25). Neither was ablated in
v1.2. This script removes one piece at a time and measures:

- synthetic: cases passed on the 32-case Deep golden set and on its
  13-case b11 class (Level 1 scorer, sentence answers), and
- real: cases whose top passage contains the gold answer, over the BM25
  top 5, on the committed SQuAD (500) and HotpotQA (200) samples.

Synthetic and real numbers are kept in separate blocks and never mixed.
The "shipped" variant must reproduce results_deep.json (32 of 32, b11 13
of 13) and results_rerank_experiment.json ("current" top-1 319 and 47);
tests/test_deep_ablation.py pins that.

Run: python level-3-deep/ablation.py
Writes: level-3-deep/results_ablation.json
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
sys.path.insert(0, os.path.join(ROOT, "real-data"))

from pipeline import BM25Index, load_corpus  # noqa: E402
from rag_eval import score_case  # noqa: E402
from rerank_experiment import contains_gold  # noqa: E402
from reranker import STOPWORDS, TOKEN_RE  # noqa: E402

RULES = ("ies", "sses", "ing", "ed", "s")


def make_stem(rules):
    def stem(token):
        if "ies" in rules and len(token) > 4 and token.endswith("ies"):
            return token[:-3] + "y"
        if "sses" in rules and token.endswith("sses"):
            return token[:-2]
        if "ing" in rules and len(token) > 5 and token.endswith("ing"):
            return token[:-3]
        if "ed" in rules and len(token) > 4 and token.endswith("ed"):
            return token[:-2]
        if "s" in rules and len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
            return token[:-1]
        return token

    return stem


def make_rerank(rules, key):
    stem = make_stem(rules)

    def tokens(text):
        return {stem(t) for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS}

    def rerank(query, hits):
        q = tokens(query)
        decorated = []
        for idx, (text, score) in enumerate(hits):
            p = tokens(text)
            shared = len(q & p) if q and p else 0
            cov = shared / len(q) if q and p else 0.0
            prec = shared / len(p) if q and p else 0.0
            f1 = 2 * prec * cov / (prec + cov) if shared else 0.0
            sort_key = {
                "coverage_f1_bm25": (-cov, -f1, -score, idx),
                "coverage_bm25": (-cov, -score, idx),
                "f1_bm25": (-f1, -score, idx),
                "f1_coverage_bm25": (-f1, -cov, -score, idx),
            }[key]
            decorated.append((sort_key, text, score))
        decorated.sort(key=lambda item: item[0])
        return [(text, score) for _, text, score in decorated]

    return rerank


VARIANTS = {"bm25_only": None, "shipped": (RULES, "coverage_f1_bm25"), "no_stemming": ((), "coverage_f1_bm25")}
for _rule in RULES:
    VARIANTS[f"drop_rule_{_rule}"] = (tuple(r for r in RULES if r != _rule), "coverage_f1_bm25")
VARIANTS["key_coverage_bm25"] = (RULES, "coverage_bm25")
VARIANTS["key_f1_bm25"] = (RULES, "f1_bm25")
VARIANTS["key_f1_coverage_bm25"] = (RULES, "f1_coverage_bm25")


def load_json(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


def synthetic(variant_fn):
    corpus = load_corpus(os.path.join(HERE, "corpus_deep.json"))
    cases = load_json("level-3-deep", "golden_set_deep.json")
    index = BM25Index(corpus)
    passed = b11 = 0
    for case in cases:
        hits = index.search_passages(case["question"], top_k=5)
        if variant_fn:
            hits = variant_fn(case["question"], hits)
        contexts = [t for t, _ in hits]
        ok = score_case({
            "id": case["id"], "answer": contexts[0] if contexts else "", "contexts": contexts,
            "gold_facts": case["gold_facts"], "gold_answer": case["gold_answer"],
        })["passed"]
        passed += ok
        b11 += ok and case.get("case_class") == "b11"
    return {"n": len(cases), "passed": passed, "b11_passed": b11}


def real(pools, cases, variant_fn):
    hit = 0
    for case, pool in zip(cases, pools):
        ranked = variant_fn(case["question"], pool) if variant_fn else pool
        hit += bool(ranked) and contains_gold(ranked[0][0], case["gold_answer"])
    return hit


def run():
    fns = {name: (make_rerank(*spec) if spec else None) for name, spec in VARIANTS.items()}
    out = {
        "generated_by": "level-3-deep/ablation.py",
        "variants": {name: ({"rules": list(spec[0]), "key": spec[1]} if spec else "no rerank")
                     for name, spec in VARIANTS.items()},
        "synthetic_deep": {name: synthetic(fn) for name, fn in fns.items()},
        "real_top1_contains_gold": {},
    }
    for key, cases_name, corpus_name in (("squad", "squad_cases.json", "squad_corpus.json"),
                                         ("hotpotqa", "hotpot_cases.json", "hotpot_corpus.json")):
        cases = load_json("real-data", "samples", cases_name)
        index = BM25Index(load_json("real-data", "samples", corpus_name))
        pools = [index.search_passages(c["question"], top_k=5) for c in cases]
        out["real_top1_contains_gold"][key] = {"n": len(cases),
                                               **{name: real(pools, cases, fn) for name, fn in fns.items()}}
    return out


def main():
    out = run()
    for name, s in out["synthetic_deep"].items():
        r = out["real_top1_contains_gold"]
        print(f"{name:22s} deep {s['passed']:2d}/32 b11 {s['b11_passed']:2d}/13 "
              f"squad top1 {r['squad'][name]:3d} hotpot top1 {r['hotpotqa'][name]:3d}")
    with open(os.path.join(HERE, "results_ablation.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print("wrote results_ablation.json")


if __name__ == "__main__":
    main()
