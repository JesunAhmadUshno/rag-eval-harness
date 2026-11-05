# Real data runs (v1.2)

Until v1.0 every number in this project came from synthetic sets the
project wrote itself. That proves the harness runs. It does not prove
the harness measures anything real. This folder fixes that: the same
pipeline and the same metrics, run on two public datasets with human
gold answers (see DATASETS.md for sources, licenses, and the sampling
method).

## What runs

fetch_samples.py rebuilds the committed samples (stdlib only).
run_real_eval.py runs the BM25 pipeline (level-2-build) with and
without the stemmed-overlap reranker (level-3-deep), in two answer
modes: the whole top sentence (sentence mode, the v1.0 and v1.1
behaviour) and a short span cut from that sentence (span mode, v1.2,
level-3-deep/span_extract.py). Scoring is the Level 1 lexical metrics
plus the embedding judge (model-metrics/) when its model is available.
Output: results_real.json. rerank_experiment.py is the v1.2 reranker
transfer test; its output is results_rerank_experiment.json.

## Measured results, 2026-11-04 (v1.2 samples)

| Dataset | Variant | Passed (lexical) | Context recall | Answer relevance (token F1) | Model judge pass | Top passage holds gold |
| --- | --- | --- | --- | --- | --- | --- |
| SQuAD sample, 500 cases | sentence, no rerank | 24 of 500 | 0.828 | 0.160 | 274 of 500 | 315 of 500 |
| SQuAD sample, 500 cases | sentence, rerank | 22 of 500 | 0.828 | 0.157 | 281 of 500 | 319 of 500 |
| SQuAD sample, 500 cases | span, no rerank | 113 of 500 | 0.828 | 0.198 | 115 of 500 | 315 of 500 |
| SQuAD sample, 500 cases | span, rerank | 108 of 500 | 0.828 | 0.193 | 112 of 500 | 319 of 500 |
| HotpotQA sample, 200 cases | sentence, no rerank | 1 of 200 | 0.518 | 0.070 | 61 of 200 | 39 of 200 |
| HotpotQA sample, 200 cases | sentence, rerank | 1 of 200 | 0.518 | 0.072 | 70 of 200 | 47 of 200 |
| HotpotQA sample, 200 cases | span, no rerank | 7 of 200 | 0.518 | 0.080 | 30 of 200 | 39 of 200 |
| HotpotQA sample, 200 cases | span, rerank | 9 of 200 | 0.518 | 0.104 | 39 of 200 | 47 of 200 |

Faithfulness is 1.000 in every run, in both answer modes. That is by
construction, not a win: the answer is copied from the retrieved
context, and the span is a substring of it, so the answer tokens are
supported by definition. Semantic support reads 1.000 in sentence
mode for the same reason; in span mode it is a real measurement
(0.348 SQuAD, 0.398 HotpotQA, reranked runs).

## What the v1.2 results say, honestly

1. Span extraction is the biggest measured gain in this project.
   Sentence against span, same cases, same retrieval, same corpus:
   SQuAD lexical passes rise from 24 to 113 without rerank and from
   22 to 108 with it; relevance rises from 0.160 to 0.198. HotpotQA
   passes rise from 1 to 7 and from 1 to 9; relevance from 0.070 to
   0.080 and from 0.072 to 0.104. The wrong_or_incomplete_answer label
   count falls from 477 to 391 on SQuAD. The answer step is still the
   weaker half (the top passage holds the gold text in 319 of 500
   SQuAD cases while 108 pass), but the gap is now measured in spans
   missed or cut wrong, not in a metric mismatch.
2. The embedding judge and the lexical rule trade places. In sentence
   mode the judge passed far more cases than the lexical rule (281
   against 22 on SQuAD), because it is not fooled by wording. In span
   mode the two nearly agree in count (112 against 108), because a
   short span's static embedding is a weaker signal than a full
   sentence's. The agreement numbers are in model-metrics/README.md.
3. Retrieval is now the binding constraint on HotpotQA. Recall is
   0.518: a case needs two gold facts and the top 5 often holds one.
   Nothing in the answer step can fix a fact that was never
   retrieved. Dense retrieval is the named next step for this
   (ROADMAP v1.3 backlog).
4. Corpus growth makes cross-version comparisons tricky, so they are
   not made here. The v1.2 retrieval pool is the union of the bigger
   samples' documents (2,248 SQuAD passages against 323 in v1.1). On
   the shared first 100 SQuAD cases, sentence-mode recall reads 0.750
   in v1.2 against 0.830 recorded in v1.1. That drop is the harder
   pool, not a pipeline regression: BM25, the metrics, and the cases
   are unchanged, and the within-run sentence against span comparison
   above is the valid before and after.

## The reranker transfer test (v1.2)

Question: why does the reranker that fixed the synthetic b11 class
change so little on real data, and can a concrete change fix that?
Method: BM25 pools of 5 and 10 on the v1.2 samples; variants are the
shipped reranker, a hybrid key (alpha times normalized BM25 plus
(1 minus alpha) times stemmed coverage, alpha 0.3, 0.5, 0.7), and
pool-10 versions of both; sentence answers throughout, so the
reranker is the only moving part. Full numbers:
results_rerank_experiment.json. Headlines:

- SQuAD: hybrid at alpha 0.5 puts the gold in the top passage for
  330 of 500 cases against 319 for the shipped reranker and 315 for
  plain BM25, with relevance 0.163 against 0.157. Pool 10 adds a
  little more (332, recall 0.830).
- HotpotQA: the same hybrid falls to 39 of 200 against 47 for the
  shipped reranker, with relevance 0.068 against 0.072. Pool 10
  raises recall to 0.533 and still holds only 39.
- Diagnostics: on SQuAD the shipped reranker changes the top passage
  in 97 cases and helps gold containment in 26, hurts in 22: close
  to a coin flip. On HotpotQA it changes 63, helps 14, hurts 6. The
  short-passage bias hypothesis is not supported: the passages it
  promotes average 19.9 tokens against 17.1 for the ones it demotes
  on SQuAD. Coverage-first ordering favours longer passages, which
  is one reason gold containment can rise while sentence-mode
  relevance falls.

Decision: no reranker change ships in v1.2. The rule set in advance
was that a change must help on real data without regressing the
synthetic Deep gate; the hybrid helps one dataset and hurts the
other, and pool depth trades recall against containment. The shipped
reranker stays, the Deep gate stays green untouched, and a learned
reranker remains on the backlog with this experiment as the baseline
it has to beat on both datasets at once.

## v1.1 results, kept for the record (smaller samples, smaller corpus)

Measured 2026-11-04 on the v1.1 samples (100 SQuAD cases, 60 HotpotQA
cases, retrieval over the v1.1 corpora): SQuAD lexical pass 1 of 100
with and without rerank, recall 0.830, relevance 0.116 and 0.111,
judge pass 49 and 46 of 100. HotpotQA lexical pass 0 of 60, recall
0.523, relevance 0.066 and 0.068, judge pass 18 and 19 of 60. The
v1.1 conclusions (retrieval stronger than the answer step; the
reranker does not transfer) were retested at v1.2 scale above.
