# rag-eval-harness

An evaluation harness for RAG systems, the public version of a real pipeline that went from a 72.7 percent pass rate to 95 percent or more (self-reported, to be proven in public here).

Status: LEARN DONE and BUILD DONE 2026-11-04 (ROADMAP-V3-BATCH).
Level 1 code runs with 11 passing unit tests and one measured golden
set run. Level 2 runs end to end (below) with 13 Build tests, 24 tests
total. Deep is not started. The Wave 0 scaffold claim is superseded by
this line. Project: P06. Fleet node: BlackBoxV2. Wave: Wave 1.

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

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
