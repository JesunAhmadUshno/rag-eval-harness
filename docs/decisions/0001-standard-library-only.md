# 0001: The harness runs on the Python standard library

Date: 2026-11-04. Status: accepted.

Context: the project's value is that a reader can check every score by
hand and rerun every number offline.

Decision: the evaluator, pipeline, reranker, span extractor, statistics
and calibration use the standard library only. The embedding judge
(model2vec) is the one optional dependency; without it the lexical run
completes and records the judge as not run, never as zero.

Consequences: no reference BM25 package, Ragas or dense retriever is
compared yet; each needs an explicit decision to add an optional
dependency (REPORT.md, research review section 4).
