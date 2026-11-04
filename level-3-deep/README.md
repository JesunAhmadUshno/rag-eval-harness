# Level 3, Deep: rag-eval-harness

Status: DONE 2026-11-04 (ROADMAP-V3-BATCH, Sprint 1), as a COMPRESSED
Deep under the December Compression Protocol. Compressed means: the
single hardest capability in the SPEC Deep scope was built, tested,
and benchmarked in full, and the rest of the v2 Deep scope is named
as the v1.1 backlog in ROADMAP.md at the repo root. It is not the
full v2 Deep scope, and this README does not claim it is.
Spec for this level: DEEP-SPEC.md in this folder.

## What was built

1. A reranker (reranker.py) that fixes the b11 class of failure:
   right document retrieved, wrong passage on top. BM25 length
   normalisation rewards a short distractor passage when both share
   the same exact query terms, and exact matching misses the one
   separating term when it is inflected (query "run", passage
   "runs"). The reranker re-scores the top 5 BM25 passages by
   stemmed query coverage, then stemmed token F1, then the BM25
   score. The stemmer is a small documented rule set (plural and
   verb endings) in stdlib only. pipeline_deep.py runs it after
   retrieval and before the extractive answer step;
   use_rerank=False reproduces Build behaviour exactly, which is
   how the before and after numbers below were measured on the
   same set.
2. An expanded Deep golden set (golden_set_deep.json): 32 cases
   over a 24-document corpus (corpus_deep.json, the 12 Build
   documents plus 12 new). The 20 Build cases are carried in as
   regression cases with their ids unchanged. The b11 class is 13
   cases: the original b11-storytime-when plus 12 new cases
   (d01 to d12), each built so several passages from the right
   document share the query terms and only one answers the
   question. A corpus integrity test asserts every gold fact is
   covered by the corpus, so every case is answerable in principle.
3. A regression gate (regression_gate.py), the CI regression test
   the SPEC Deep scope names. It runs the full Deep set with
   reranking and exits non-zero when the pass rate drops below the
   recorded threshold (0.90 in baseline.json) or any case that
   passed in the baseline regresses. Tests prove it passes on the
   current results and fails on a deliberately regressed fixture.
4. A failure taxonomy (taxonomy.py) with one primary label per
   failure, so the counts sum to the failure total and a reader can
   check the table by hand. RAG labels: hallucination,
   retrieval_miss, wrong_passage_on_top, wrong_or_incomplete_answer.
   Agent labels beside them, from the SPEC Deep scope: loop_trap,
   tool_misuse, silent_wrong_answer, excess_steps, assigned by
   agent_deep.py to five demo agents (careful, loopy, wrong_tool,
   silent, sloppy) over the Build demo tasks extended with an
   expected tool field.
5. A quality dashboard (dashboard.py): run_deep.py regenerates
   dashboard.md and results_deep.json from each run. No number in
   the dashboard is hand typed.

## Run it

```text
python level-3-deep/run_deep.py
python level-3-deep/regression_gate.py
python -m unittest discover -s tests -p "test_deep*.py" -v
```

No dependencies. Python 3.12 standard library only.

## Measured results (2026-11-04, Muse VM, Python 3.12.3)

Method: the same Deep pipeline and the same Learn scorer in both
columns; the only difference is the reranking step. Judge pass:
BudgetedJudge, max_calls 15, sample_rate 1.0, cost 1 unit per call,
over the reranked answers.

| Measure | Without rerank | With rerank |
| --- | --- | --- |
| Cases passed | 23 of 32 | 32 of 32 |
| Pass rate | 0.719 | 1.000 |
| Mean faithfulness | 1.000 | 1.000 |
| Mean context recall | 1.000 | 1.000 |
| Mean answer relevance | 0.764 | 1.000 |
| b11 class passed (13 cases) | 5 | 13 |
| Judge (reranked run) | n/a | 15 calls, cost 15, 15 of 15 judged pass |

The b11 fix is real on this set: the 8 b11-class cases that failed
without reranking (b11-storytime-when, d01, d03, d04, d06, d09, d10,
d11) all pass with it, and no case that passed without reranking
regressed with it. One regression-class case, b15-events-bookclub,
also failed without reranking on the expanded corpus (a movie club
passage outranked the book club passage) and passes with reranking.
Its primary label is also wrong_passage_on_top, so the taxonomy
count for that label is 9, one more than the b11-class failure
count of 8. Both numbers are stated here so the table can be
checked against results_deep.json.

Agent demo (Deep protocol, 4 tasks each): careful scored success
1.000, mean steps 2.0, mean cost 3.0. The four defective demos each
failed all 4 tasks with their designed label: loopy loop_trap
(steps 12.0, cost 11.0), wrong_tool tool_misuse (steps 3.0, cost
4.0), silent silent_wrong_answer (steps 2.0, cost 3.0), sloppy
excess_steps (steps 8.0, cost 9.0). These are toy agents that prove
the taxonomy, not a real agent. The P07 agent does not exist yet.

## Failure modes

From the actual Deep runs (taxonomy.py, one primary label each):

RAG failures, without rerank run, 9 of 32 cases:
- wrong_passage_on_top: 9. Every failure in the without run was
  this class: faithfulness and recall at 1.000, relevance below
  the line. The corpus and retrieval were never the problem on
  this set; passage ranking was.
- hallucination: 0, retrieval_miss: 0, wrong_or_incomplete_answer: 0.
  Expected at this level: the answer step is extractive, so the
  answer is a retrieved passage by construction and cannot drift
  from the context. The generative step that makes hallucination
  possible is v1.1 backlog (ROADMAP.md item 2).

RAG failures, with rerank run: 0 of 32 cases.

Agent failures, demo runs, 16 of 20 tasks:
- loop_trap: 4 (the loopy demo, repeated actions at 12 steps
  against a budget of 5, correct answer delivered too late to
  count as success).
- tool_misuse: 4 (the wrong_tool demo, web search used where the
  task required the catalog tool).
- silent_wrong_answer: 4 (the silent demo, wrong answer at normal
  steps and cost with the right tool: no distress signal).
- excess_steps: 4 (the sloppy demo, wrong answer at 8 steps
  against a budget of 5).

Known failure modes of the reranker itself:
- It can only reorder the top 5 BM25 passages. A gold passage
  ranked below 5 by BM25 stays unreachable; recall at the passage
  level is the ceiling, and on a larger corpus that ceiling will
  bind. ROADMAP.md item 4 is where that gets measured.
- The stemmer is rule based and small. It conflates some distinct
  words and misses irregular forms. On this set it caused no
  regression; that is a measured fact about this set, not a
  general claim.
- Coverage-first ordering can prefer a longer passage that merely
  mentions every query term over a shorter one that answers. The
  F1 tiebreak limits this, and the Deep set contains no such case;
  a larger corpus is expected to produce some (ROADMAP.md item 5
  compares a learned reranker on the same discipline).

## Limits, stated plainly

- Compressed Deep, by the protocol named above. The full v2 Deep
  scope is not done; its remainder is ROADMAP.md (LLM judge,
  generative answer step, real P07 agent, larger real corpus,
  learned reranking, workshop paper submission, which is Jesun's
  tap).
- The corpus and golden set are synthetic and fictional, 32 cases.
  A pass rate of 1.000 on a synthetic set this size proves the
  reranking mechanism and the gate, not production quality.
- The judge is still the local lexical proxy from Build, not an
  LLM. The budget machinery is real; the semantic judgment is not.
- The run executed on the Muse VM, not the assigned BlackBoxV2 node.
