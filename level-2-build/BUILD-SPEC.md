# Build Spec: rag-eval-harness Level 2

## Objective
Close Build per SPEC.md acceptance: the system runs end to end, tests
pass, and one benchmark table with method is in the README. Build adds
three capabilities on top of the Learn lexical evaluator:
1. A real end-to-end RAG pipeline (retrieve, then answer) over a local
   corpus, scored by the same Learn metrics.
2. A judge layer with an explicit budget and sampling rule, so judge
   cost is controlled and written up (register item 702).
3. An agent task protocol: any callable agent that returns an answer,
   a step count, and a cost is scored for success rate, mean steps,
   and cost per task, the same pass and label discipline as RAG cases.

## Assumptions
- No external API, no credentials, no spend. The default judge is a
  deterministic local proxy. The judge interface accepts any callable,
  so a real LLM judge can be plugged in later without code changes.
- Corpus and golden set stay in the fictional Northlight Library domain
  used at Learn level, expanded. Synthetic, and named as synthetic.
- P07 agent-from-scratch does not exist yet, so agent scoring is proven
  against two toy demo agents, not claimed against a real agent.

## Commands
- Test: python -m unittest discover -s tests -p "test_build*.py" -v
- Run: python level-2-build/run_build.py
- Full: python -m unittest discover -s tests -v

## Boundaries
- Always: stdlib only, deterministic seeded behaviour, hand-checkable
  numbers, results recorded exactly as measured.
- Never: an external call, a new credential, a claim that the local
  judge is an LLM, or a grade for a scaffold.

## Success criteria
- BM25 retrieval ranks the gold document first on the probe queries
  asserted in tests.
- Every golden fact is covered by the corpus (answerability test).
- The pipeline end-to-end run produces a measured pass rate and mean
  metrics, recorded in the README with method.
- Judge budget is never exceeded in tests, including when the budget
  is smaller than the case count, and sampling is deterministic.
- Agent scoring returns exact success, steps, and cost values for the
  fake agents in tests.
