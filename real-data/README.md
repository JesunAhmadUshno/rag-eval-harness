# Real data runs (v1.1)

Until v1.0 every number in this project came from synthetic sets the
project wrote itself. That proves the harness runs. It does not prove
the harness measures anything real. This folder fixes that: the same
pipeline and the same metrics, run on two public datasets with human
gold answers (see DATASETS.md for sources and licenses).

## What runs

fetch_samples.py rebuilds the committed samples (stdlib only, a few
hundred rows at most). run_real_eval.py runs the BM25 plus extractive
answer pipeline (level-2-build), with and without the stemmed-overlap
reranker (level-3-deep), scores with the Level 1 lexical metrics, and
adds the embedding judge (model-metrics/) when its model is available.
Output: results_real.json.

## Measured results, 2026-11-04

| Dataset | Variant | Passed (lexical) | Context recall | Answer relevance (token F1) | Model judge pass |
| --- | --- | --- | --- | --- | --- |
| SQuAD sample, 100 cases | no rerank | 1 of 100 | 0.830 | 0.116 | 49 of 100 |
| SQuAD sample, 100 cases | rerank | 1 of 100 | 0.830 | 0.111 | 46 of 100 |
| HotpotQA sample, 60 cases | no rerank | 0 of 60 | 0.523 | 0.066 | 18 of 60 |
| HotpotQA sample, 60 cases | rerank | 0 of 60 | 0.523 | 0.068 | 19 of 60 |

Faithfulness is 1.000 in every run. That is by construction, not a win:
an extractive answer is copied from the retrieved context, so it cannot
be unfaithful to it. The same holds for semantic support (1.000).

## What the results say, honestly

1. Retrieval is the stronger half. The gold fact sits in the top 5
   passages for 83 percent of SQuAD cases. Multi-hop HotpotQA is harder:
   52 percent recall, and 46 of 60 cases miss at least one gold fact.
2. The answer step is the weak half. The pipeline answers with a whole
   sentence; the gold answers are short spans. Token F1 against a short
   span punishes a correct sentence, so answer relevance is low and the
   wrong_or_incomplete_answer label fires on 99 of 100 SQuAD cases. The
   embedding judge, which is not fooled by wording, passes about half of
   the SQuAD cases. The gap between the two judges is the size of the
   metric mismatch, measured.
3. The reranker does not transfer. It fixed the synthetic b11 class
   completely at Deep level, and on real data it changes almost nothing
   (SQuAD relevance 0.116 to 0.111, HotpotQA recall unchanged). A fix
   proven only on synthetic data is a hypothesis, and this is the proof.
4. The next fix is named, not hidden: span extraction, answering with
   the short span instead of the whole sentence, is v1.2 backlog item 1
   in ROADMAP.md. Until it lands, these pass rates are the honest state
   of the pipeline on real data.
