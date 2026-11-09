# Release notes: rag-eval-harness (P06)

One page per release line. Every number below comes from the level
README of that release and was Jev-gated in its own cycle. The full
release text and artifacts live on the GitHub releases page:
https://github.com/JesunAhmadUshno/rag-eval-harness/releases

## v0.1, Learn (2026-11-04)

- What shipped: a dependency-free lexical RAG evaluator, an 8-case
  synthetic golden set, a runner, and 11 unit tests.
- Measured result: 5 of 8 golden cases passed (pass rate 0.625, by
  design: 3 cases were built to fail and each was named correctly).
  Mean faithfulness 0.953, mean context recall 0.938, mean answer
  relevance 0.808.
- Release: https://github.com/JesunAhmadUshno/rag-eval-harness/releases/tag/v0.1

## v0.5, Build (2026-11-04)

- What shipped: an end-to-end BM25 RAG pipeline over a 12-document
  corpus, a budgeted judge layer with a hard call cap, agent task
  protocol scoring, and a 20-case Build golden set.
- Measured result: 19 of 20 cases passed (pass rate 0.950). The one
  failure, b11-storytime-when, was kept as the first Deep fix target.
  Judge pass: 10 calls under a cap of 10, 10 of 10 judged passed.
- Release: https://github.com/JesunAhmadUshno/rag-eval-harness/releases/tag/v0.5

## v1.0, Deep, compressed (2026-11-04)

- What shipped: a stemmed query-passage overlap reranker over the
  top-5 BM25 passages, a 32-case Deep golden set, a regression gate
  with a 0.900 pass threshold, a failure taxonomy, and a quality
  dashboard. The rest of the v2 Deep scope is named in REPORT.md
  as the v1.1 backlog.
- Measured result: pass rate 23 of 32 (0.719) without the reranker
  and 32 of 32 (1.000) with it, with no previously passing case
  regressed.
- Release: https://github.com/JesunAhmadUshno/rag-eval-harness/releases/tag/v1.0

## v1.1, research upgrade (2026-11-05)

- What shipped: real public datasets next to the synthetic set
  (SQuAD 100 cases and HotpotQA 60 cases, both CC BY-SA 4.0,
  licenses recorded in real-data/DATASETS.md), a Model2Vec
  embedding judge inside the evaluation path, and a React results
  lab replacing the single-page docs at the same Pages URL.
- Measured result, reported separately from synthetic results:
  SQuAD lexical pass 1 of 100, context recall 0.830, embedding
  judge pass 49 of 100. The synthetic reranker fix does not
  transfer to real data; that finding is published, not buried.
- Release: https://github.com/JesunAhmadUshno/rag-eval-harness/releases/tag/v1.1

## v1.2, span and scale (2026-11-05)

- What shipped: span extraction behind answer_mode="span" (the
  sentence mode stays the default), real samples raised to 500
  SQuAD and 200 HotpotQA cases, a reranker transfer experiment,
  judge calibration against a gold-derived proxy, and a per-case
  drill down on the dashboard.
- Measured result, same cases and corpora: SQuAD lexical passes
  rose from 22 to 108 of 500 and HotpotQA from 1 to 9 of 200 with
  span answers. The reranker experiment shipped no change: the
  hybrid variant helped SQuAD and hurt HotpotQA, and the negative
  result is published with diagnostics.
- Release: https://github.com/JesunAhmadUshno/rag-eval-harness/releases/tag/v1.2

## Held channels

- Social posts for every release above: HELD under the standing
  platform rules. The loop prepares drafts and never posts; Threads
  needs Jesun's one tap per post.
- The v1.3 backlog lives in REPORT.md: dense retrieval first,
  then the generative answer step, then learned reranking.
