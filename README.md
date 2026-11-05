# rag-eval-harness

An evaluation harness for RAG systems, the public version of a real pipeline that went from a 72.7 percent pass rate to 95 percent or more (self-reported, to be proven in public here).

Status: v1.1 RESEARCH UPGRADE DONE 2026-11-04 (ROADMAP-V3-BATCH).
v1.0 (Learn, Build, compressed Deep) plus: real public dataset runs
(SQuAD and HotpotQA samples, license checked, real-data/), a model
inside the evaluation path (an embedding judge on CPU, model-metrics/),
and a React results lab live at
https://jesunahmadushno.github.io/rag-eval-harness/ (source in web/).
Tests: 52 in total, regression gate passing at a 0.900 threshold.
Project grade at v1.1: 8,000 of 10,000, deductions named in DOSSIER.md.
Project: P06. Fleet node: BlackBoxV2. Wave: Wave 1.

## Start here

1. Read SPEC.md for scope and acceptance criteria.
2. Read DOSSIER.md for the past, present, and future of this problem (v1).
3. Read NOVELTY.md for the proposed novelty (DRAFT, pending the Jev claim_check gate).
4. Start at level-1-learn/README.md, then level-2-build, then level-3-deep.

## Level map

- Level 1, Learn: the core idea, built small and clean, with a teaching path.
- Level 2, Build: a real working system other people can run.
- Level 3, Deep: benchmarks, optimization, evaluation, hard cases.

## Benchmarks

| Test | Result |
| --- | --- |
| Level 1 golden set, 8 synthetic cases, lexical metrics (method: level-1-learn/README.md), 2026-11-04 | 5 of 8 passed, pass rate 0.625 by design (3 cases built to fail, each named correctly: hallucination 1, retrieval_miss 1, wrong_or_incomplete_answer 1). Mean faithfulness 0.953, mean context recall 0.938, mean answer relevance 0.808. |
| Level 2 end-to-end run, 20 synthetic cases, BM25 retrieval plus extractive answer, scored by the Level 1 metrics (method: level-2-build/README.md), 2026-11-04 | The pipeline passed 19 of 20 cases (pass rate 0.950), with mean faithfulness 1.000, mean context recall 1.000, and mean answer relevance 0.970. The one failure is b11-storytime-when, labelled wrong_or_incomplete_answer. Judge pass: 10 calls made under a cap of 10, 10 cases skipped as not judged, 10 of 10 judged passed. |
| Level 3 Deep (compressed) run, 32 synthetic cases, same pipeline with and without the stemmed-overlap reranker, scored by the Level 1 metrics (method: level-3-deep/README.md), 2026-11-04 | Without rerank the pipeline passed 23 of 32 cases (pass rate 0.719); with rerank it passed 32 of 32 (pass rate 1.000). The b11 class of 13 cases (right document, wrong passage on top) went from 5 of 13 passed without rerank to 13 of 13 with rerank. Judge pass on the reranked run: 15 calls made, 15 of 15 judged passed. Regression gate: threshold 0.900, PASS. Tests: 15 Deep tests, 39 tests in total. |
| Real data run, SQuAD sample (REAL, public dataset, CC BY-SA 4.0), 100 cases, same pipeline, Level 1 metrics plus the embedding judge (method: real-data/README.md), 2026-11-04 | Lexical pass 1 of 100 with and without rerank. Context recall 0.830. Answer relevance 0.116 without rerank, 0.111 with. Embedding judge pass 49 of 100 without rerank, 46 of 100 with. Faithfulness 1.000 by construction (extractive answers). |
| Real data run, HotpotQA sample (REAL, public dataset, CC BY-SA 4.0), 60 cases, same method, 2026-11-04 | Lexical pass 0 of 60 with and without rerank. Context recall 0.523 in both variants. Answer relevance 0.066 without rerank, 0.068 with. Embedding judge pass 18 of 60 without rerank, 19 of 60 with. |

## Fan-out

Written fan-out for v1.0, drafted 2026-11-04. Drafts only, nothing
posted externally by this set.

- Blog post: fanout/blog-post.md
- Tutorial (course module P06-rag-eval-harness): fanout/tutorial.md
- Website project page copy: fanout/website-page.md
- LinkedIn post draft (marked DRAFT NOT POSTED): fanout/linkedin-post.md
- Paper candidate brief: fanout/paper-candidate.md

## Dashboard

The results lab is a React app in web/, deployed to GitHub Pages:
https://jesunahmadushno.github.io/rag-eval-harness/
It carries an interactive results lab, a live in-browser run of the
lexical evaluator (a JavaScript port verified score-for-score against
the Python code on 20 cases), the dataset record, the references, full
documentation, and the prototype history. Synthetic and real results
are labelled and never mixed, there and here.

## Novelty

Stated honestly in NOVELTY.md. The v1.1 claims went through the Jev
claim_check gate on 2026-11-04 (model jev-1.13.0): all five claims
routed REVIEW, none blocked, none overstated past their evidence.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
