# LinkedIn post draft: P06 rag-eval-harness v1.0

Status: DRAFT NOT POSTED
Date drafted: 2026-11-04
Author: Jesun Ahmad Ushno
Rule for this platform: the link goes in the first comment, not in the
post body. The first comment line is at the end of this file.

## Post body

One blended score hides where a RAG system broke. So I built the eval
harness that names the failure instead.

rag-eval-harness v1.0 is done: Learn, Build, and a compressed Deep,
all open, all measured, Python standard library only.

Learn: three lexical metrics, one per failure place, on an 8-case
synthetic golden set. 5 of 8 passed, and that 0.625 is by design.
Three cases were built to fail, and the harness labelled each one
correctly: hallucination, retrieval miss, wrong or incomplete answer.

Build: an end-to-end BM25 pipeline under a judge layer with a hard
call cap. 19 of 20 synthetic cases passed (0.950). The one failure,
b11, found the right document and still put the wrong passage on top.
I kept it in the record. It became the Deep target.

Deep (compressed): a stemmed-overlap reranker, a 32-case set, and a CI
regression gate at a 0.900 threshold. Without reranking: 23 of 32
(0.719). With reranking: 32 of 32 (1.000). The b11 class went from
5 of 13 to 13 of 13. 39 tests in total, all passing.

The honest limits, in the post and not in a footnote: synthetic
corpora only, the judge is a lexical proxy and not an LLM judge, and
the agent scoring is proven on toy demo agents. A 1.000 on 32
synthetic cases proves the mechanism and the gate, not production
quality. The rest of the Deep scope is named as the v1.1 backlog in
the repo, not claimed as done.

Grades, house scale: Learn 8,700, Build 8,700, Deep 7,900 of 10,000.

If you eval RAG systems: which failure class costs you the most time,
retrieval, grounding, or ranking?

## First comment (post this as the first comment, per the standing rule)

Repo, releases v0.1, v0.5, and v1.0, and the full tutorial: https://github.com/JesunAhmadUshno/rag-eval-harness
