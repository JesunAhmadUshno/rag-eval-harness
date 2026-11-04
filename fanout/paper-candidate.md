# Paper candidate brief: RAG eval harness paper

Tracker row: "RAG eval harness paper" (publications pipeline tracker)
Project: P06 rag-eval-harness
Status: CANDIDATE, updated brief, 2026-11-04
Submission note: submission is Jesun's tap. Nothing is submitted by
this brief, and no venue has been contacted.

## Working title

Failure-labelled evaluation for small RAG pipelines: lexical metrics, a
budgeted judge layer, and a reranking fix proven on synthetic golden sets

## Abstract draft

Based only on the measured v1.0 results recorded in the repo. Numbers
below are from synthetic corpora and are stated as such.

Retrieval-augmented generation (RAG) systems fail in distinct places:
retrieval can miss the supporting facts, answers can state claims the
context does not support, and a grounded answer can still answer the
wrong question. A single blended score cannot direct a fix. This work
presents an open, dependency-free evaluation harness that scores each
failure place with a lexical metric (context recall, faithfulness, and
answer relevance), assigns one failure label per failing case, and
carries the same scoring discipline through an end-to-end pipeline and
a ranking study. At Learn level, on an 8-case synthetic golden set, the
harness passed 5 of 8 cases (0.625 by design, with three cases built to
fail) at mean faithfulness 0.953, context recall 0.938, and answer
relevance 0.808, and labelled each designed failure correctly. At Build
level, a BM25 pipeline with an extractive answer step passed 19 of 20
synthetic cases (0.950) at faithfulness 1.000, recall 1.000, and
relevance 0.970, under a budgeted judge layer that held a hard cap of
10 calls with 10 of 10 judged cases passed; the single failure exposed
a wrong-passage-on-top ranking defect. At Deep level, on a 32-case
synthetic set, a stemmed-overlap reranker raised the pass rate from
23 of 32 (0.719) without reranking to 32 of 32 (1.000) with reranking,
raised the wrong-passage class from 5 of 13 to 13 of 13, and passed a
CI regression gate at a 0.900 threshold, with a budgeted judge pass of
15 calls and 15 of 15 judged passed. The harness ships with 39 unit
tests. The corpora are synthetic, the judge is a lexical proxy rather
than an LLM judge, and the agent results use toy demo agents; the paper
claims the measurement discipline and the reranking result on these
sets, not production performance.

## Method outline

1. Metrics: three lexical ratios over content tokens (lowercase words
   and numbers, stopwords removed), each checkable by hand. Context
   recall: share of gold facts covered by retrieved context at an 80
   percent token coverage line. Faithfulness: share of answer content
   tokens present in the context. Answer relevance: token F1 between
   the answer and the gold answer. Pass lines: faithfulness at least
   0.80, recall at least 0.80, relevance at least 0.50.
2. Failure taxonomy: one primary label per failure, so counts sum to
   the failure total. RAG labels: hallucination, retrieval_miss,
   wrong_passage_on_top, wrong_or_incomplete_answer. Agent labels
   beside them: loop_trap, tool_misuse, silent_wrong_answer,
   excess_steps.
3. Pipeline: BM25 retrieval over a local corpus, top 5 passages,
   extractive answer (top passage verbatim). Corpus integrity tests
   assert every gold fact is covered, so every case is answerable in
   principle.
4. Budgeted judge: any judge callable wrapped with a hard max_calls
   cap, deterministic sampling by case id hash, and public cost
   accounting. Skipped cases are counted as not judged, never passed.
   The default judge is a deterministic lexical proxy.
5. Reranker: re-score the top 5 BM25 passages by stemmed query
   coverage, then stemmed token F1, then BM25 score. The stemmer is a
   small documented rule set. An ablation flag reproduces the Build
   behaviour exactly, so before and after are measured on the same set.
6. Regression gate: a CI check that runs the full Deep set with
   reranking and fails if the pass rate drops below the recorded
   threshold (0.900) or a baseline case regresses.
7. Agent protocol: agents scored on success rate, mean steps, and mean
   cost per task, proven on toy demo agents at v1.0.

## Results table

Measured 2026-11-04, synthetic corpora only, from the level READMEs in
the repo.

| Level | Cases | Passed | Faithfulness | Recall | Relevance | Judge | Tests |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Learn | 8 | 5 of 8 (0.625, by design) | 0.953 | 0.938 | 0.808 | n/a | 11 |
| Build | 20 | 19 of 20 (0.950) | 1.000 | 1.000 | 0.970 | 10 calls, cap 10, 10 of 10 judged passed | 13 |
| Deep, no rerank | 32 | 23 of 32 (0.719) | 1.000 | 1.000 | 0.764 (per level-3-deep/README.md) | n/a | 15 Deep, 39 total |
| Deep, with rerank | 32 | 32 of 32 (1.000) | 1.000 | 1.000 | 1.000 (per level-3-deep/README.md) | 15 calls, 15 of 15 passed | 15 Deep, 39 total |

Note on the Deep rows: the relevance means in this table are the
before and after means recorded in level-3-deep/README.md. The headline
Deep claim used in the fan-out set is the pass counts, the b11 class
(5 of 13 to 13 of 13), the judge line, and the gate result.

Grades on the house 10,000 scale (not paper results): Learn 8,700,
Build 8,700, Deep (compressed) 7,900.

## Venue class note

Per the publications pipeline tracker, this candidate is classed as:
journal (AJSE class) or conference. One venue at a time, per the
tracker stage rules. No venue is named as submitted, accepted, or
contacted in this brief. Fees, if any, arise only after acceptance and
remain Jesun's call under the free-only rule.

## Limits the paper must carry

- Synthetic corpora only (8, 20, and 32 fictional library cases). No
  production or real-corpus claim.
- The judge is a lexical proxy, not an LLM judge. Paraphrase is missed
  by the lexical metrics.
- The answer step is extractive, so faithfulness at 1.000 is partly by
  construction.
- Agent results are from toy demo agents that prove the protocol.
- Compressed Deep only. The v1.1 backlog (LLM judge, generative answer
  step, real agent, larger real corpus, learned reranking) is future
  work, named in ROADMAP.md in the repo.

## Submission gate

Submission is Jesun's tap and nothing is submitted. This brief updates
the candidate only. The tracker row update is made by the batch
coordinator from the delivery report, not by this file.
