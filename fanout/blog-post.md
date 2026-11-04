# One Score Hides the Failure: Building a RAG Eval Harness in the Open

By Jesun Ahmad Ushno
Date: 2026-11-04
Status: DRAFT, written fan-out for P06 rag-eval-harness v1.0. Not posted.

## The problem

A retrieval-augmented generation (RAG) system can fail in three different
places. Retrieval can miss the facts, so the answer never had a chance.
The answer can invent claims its context does not support. Or the system
can retrieve well, stay grounded, and still answer the wrong question.
One blended score hides which place broke, and a fix aimed at the wrong
place wastes the work.

This project, P06 in Roadmap v3, builds one small metric per failure
place, labels every failure, and grows that idea from a teaching set to
an end-to-end pipeline to a ranking fix guarded by a regression gate.
All code is in the open, runs with the Python 3.12 standard library
only, and needs no model, no API, and no credential.

Repository: https://github.com/JesunAhmadUshno/rag-eval-harness

## Past, present, future (the dossier, condensed)

Past: public eval tools in the Ragas class and one-off notebook scoring
already exist. The history of the problem and the prior art are recorded
in DOSSIER.md and NOVELTY.md in the repo. The novelty claim there stays
marked PROPOSED. This post makes no novelty claim beyond the measured
work below.

Present: v1.0 closes three levels on 2026-11-04. Learn built the three
lexical metrics and a failure taxonomy. Build ran the harness end to end
on a BM25 pipeline with a budgeted judge layer and agent protocol
scoring. Compressed Deep built the single hardest Deep capability in
the spec, a stemmed-overlap reranker that fixes the b11 class of
failure (right document retrieved, wrong passage on top), plus the CI
regression gate, the expanded failure taxonomy, and the quality
dashboard. Grades on the house 10,000 scale: Learn 8,700, Build 8,700,
Deep (compressed) 7,900.

Future: the rest of the v2 Deep scope is named in ROADMAP.md in the repo
as the v1.1 backlog. It includes an LLM judge behind the existing
budget interface, a generative answer step, evaluation of a real agent
once P07 exists, a larger real corpus, and a comparison against a
learned reranker. None of that is done, and none of it is claimed here.

## Main results claim

At v1.0, on synthetic corpora only: Learn passed 5 of 8 cases (0.625 by design) with mean faithfulness 0.953, context recall 0.938, and answer relevance 0.808 across 11 tests; Build passed 19 of 20 cases (0.950) with faithfulness 1.000, recall 1.000, and relevance 0.970, with the one failure b11-storytime-when, a judge cap of 10 calls with 10 of 10 judged passed, and 13 Build tests; compressed Deep, on 32 cases, passed 23 of 32 (0.719) without reranking and 32 of 32 (1.000) with reranking, the b11 class rose from 5 of 13 to 13 of 13, the judge made 15 calls with 15 of 15 passed, the regression gate passed at a 0.900 threshold, and there are 15 Deep tests and 39 tests in total.

Every number in that claim comes from a run recorded in the level
READMEs in the repo, on synthetic corpora. Read the limits section
below before quoting any of it.

## Results by level

### Level 1, Learn (release v0.1)

The golden set holds 8 synthetic cases about a fictional library. Three
cases were built to fail, one per failure type, so a 0.625 pass rate is
the harness working by design, not a system failing.

| Measure | Result |
| --- | --- |
| Cases | 8 synthetic cases |
| Passed | 5 of 8 (0.625, by design) |
| Mean faithfulness | 0.953 |
| Mean context recall | 0.938 |
| Mean answer relevance | 0.808 |
| Failure labels | hallucination 1, retrieval_miss 1, wrong_or_incomplete_answer 1 |
| Tests | 11 |

### Level 2, Build (release v0.5)

The pipeline retrieves the top 5 passages with BM25 over a 12-document
synthetic corpus and answers with the top passage. The judge layer wraps
any judge callable in a hard call cap, deterministic sampling, and cost
accounting. The default judge is a local lexical proxy, not an LLM.

| Measure | Result |
| --- | --- |
| Cases | 20 synthetic cases |
| Passed | 19 of 20 (0.950) |
| Mean faithfulness | 1.000 |
| Mean context recall | 1.000 |
| Mean answer relevance | 0.970 |
| One failure | b11-storytime-when, labelled wrong_or_incomplete_answer |
| Judge | 10 calls made, cap 10, 10 of 10 judged passed |
| Tests | 13 Build tests (24 total with Learn) |

The b11 failure was kept in the record on purpose. Retrieval found the
right document and stayed grounded, but the top passage was the session
length sentence, not the schedule sentence. That ranking defect became
the Deep level fix target.

### Level 3, Deep, compressed (release v1.0)

The Deep golden set holds 32 cases over a 24-document synthetic corpus.
The 20 Build cases are carried in as regression cases. The b11 class is
13 cases, each built so several passages from the right document share
the query terms and only one answers the question. The reranker
re-scores the top 5 BM25 passages by stemmed query coverage, then
stemmed token F1, then the BM25 score.

| Measure | Without rerank | With rerank |
| --- | --- | --- |
| Cases passed | 23 of 32 | 32 of 32 |
| Pass rate | 0.719 | 1.000 |
| b11 class passed (13 cases) | 5 of 13 | 13 of 13 |
| Judge | n/a | 15 calls, 15 of 15 judged passed |
| Regression gate | n/a | Threshold 0.900, PASS |
| Tests | n/a | 15 Deep tests, 39 total |

No case that passed without reranking regressed with it, on this set.

## Honest limits

- Synthetic corpora only. The Learn, Build, and Deep sets are fictional
  library cases (8, 20, and 32 cases). A pass rate of 1.000 on a
  synthetic set of 32 cases proves the reranking mechanism and the
  gate, not production quality.
- The judge is a lexical proxy, not an LLM judge. The budget cap,
  sampling, and cost accounting are real and tested. The semantic
  judgment an LLM would add is not present, and lexical metrics miss
  paraphrase.
- The answer step is extractive. Faithfulness at 1.000 in Build and
  Deep is partly by construction, because the answer is a retrieved
  passage. The generative step that makes hallucination possible in
  this harness is v1.1 backlog.
- The agent scoring is proven on toy demo agents only. They prove the
  protocol and the taxonomy, not a real agent.
- Compressed Deep is not the full v2 Deep scope. The remainder is the
  named v1.1 backlog in ROADMAP.md.
- The runs executed on the Muse VM, not the assigned BlackBoxV2 node.

## Where to go next

- Tutorial: fanout/tutorial.md in the repo, a step-by-step module that
  runs all three levels, the tests, and the regression gate.
- Releases: v0.1 (Learn), v0.5 (Build), v1.0 (Learn, Build, compressed
  Deep) on the GitHub repo linked above.
- License: code Apache-2.0, tutorials CC BY 4.0.
