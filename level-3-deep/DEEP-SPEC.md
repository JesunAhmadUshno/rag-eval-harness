# Deep Spec: rag-eval-harness Level 3 (compressed Deep)

## Objective
Close Deep in compressed form per the December Compression Protocol:
the single hardest capability in the SPEC Deep scope, built, tested,
benchmarked, with a failure modes section. That capability is the
ranking fix for the b11 class of failure (right document retrieved,
wrong passage on top), proven on an expanded golden set, with the CI
regression gate, failure taxonomy, and quality dashboard the SPEC
names. The rest of the v2 Deep scope is the v1.1 backlog in the repo
root REPORT.md, named there, not silently dropped.

## What Deep adds
1. reranker.py: stemmed query-passage overlap reranking over the
   top-k BM25 passages (coverage, then F1, then BM25). Stdlib only.
2. corpus_deep.json and golden_set_deep.json: 24 documents (the 12
   Build documents plus 12 new), 32 cases: the 20 Build cases as
   regression cases, plus 12 new cases of the b11 class (several
   passages from the right document, only one answers the question).
   The original b11 case is included, so the b11 class is 13 cases.
3. regression_gate.py: runs the full Deep set with reranking and
   fails with a non-zero exit when the pass rate drops below the
   baseline threshold (0.90) or any baseline passing case regresses.
   baseline.json records the baseline from the 2026-11-04 run.
4. taxonomy.py: one primary label per failure, so counts sum to the
   failure total. RAG labels beside agent labels (loop_trap,
   tool_misuse, silent_wrong_answer, excess_steps) from real demo
   agent runs scored by agent_deep.py.
5. dashboard.py plus run_deep.py: the runner measures before and
   after reranking, runs the budgeted judge and the agent demos, and
   regenerates dashboard.md and results_deep.json from the run.

## Commands
- Test: python -m unittest discover -s tests -p "test_deep*.py" -v
- Run: python level-3-deep/run_deep.py
- Gate: python level-3-deep/regression_gate.py
- Full: python -m unittest discover -s tests -v

## Boundaries
- Always: stdlib only, deterministic, numbers recorded exactly as
  measured, before and after shown for the b11 class specifically.
- Never: an external call, a new credential, a spend, a claim that
  the local judge is an LLM, or a grade for a scaffold.

## Success criteria
- The reranker puts the answering passage on top for the b11 class,
  asserted per case in tests.
- The regression gate passes on current results and fails on a
  deliberately regressed fixture, both asserted in tests.
- Taxonomy counts sum to the failure total, asserted in tests.
- The dashboard is generated from a run, never hand edited.
