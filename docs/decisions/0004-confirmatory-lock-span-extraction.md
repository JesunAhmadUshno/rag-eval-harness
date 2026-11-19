# 0004: Confirmatory lock: the span-extraction gain is the single primary hypothesis

Date: 2026-11-17. Status: accepted (locked before any confirmatory run).

Context: every result in this repo is post hoc. The hypotheses in
PROPOSAL.md were written on 2026-11-07, after all runs existed, and
PROPOSAL.md names the confirmatory process (hypotheses, pass lines and
analysis plan written and locked before any confirmatory run) but does
not choose a hypothesis or set a pass line; its candidate list does not
include the span-extraction comparison at all. The one significant
measured gain of the exploratory cycle is post hoc H3, the answer step:
on the committed samples, span answers beat sentence answers on the
Level 1 lexical pass, without rerank, SQuAD 24 to 113 of 500 (exact
McNemar discordants: sentence-only 21, span-only 110, p < 0.0001) and
HotpotQA 1 to 7 of 200 (discordants 0 and 6, p 0.0312), recorded in
real-data/results_paired_stats.json. On 2026-11-17 the Owner ruled
(default 8 of the gap-closure decision batch): the span-extraction gain
is locked as the single primary confirmatory hypothesis. This entry is
that lock. It is written before the confirmatory data is fetched and
before anything runs.

Decision: the confirmatory cycle is exactly the following, and nothing
else in it is confirmatory.

Primary hypothesis (H-C1): on previously unused SQuAD validation cases,
span answers give a higher lexical pass rate than sentence answers.

- Data: 500 new SQuAD cases, every 10th row of validation rows 5,000
  to 9,999 as served by the Hugging Face datasets server, the same
  deterministic stride method as real-data/fetch_samples.py (which
  took every 10th row of rows 0 to 4,999), disjoint from every case
  used in the exploratory cycle. The retrieval corpus is built from
  the new rows' contexts only, with the same build_squad normalization
  as fetch_samples.py. No shuffling, no filtering by outcome.
- Arms: the committed harness at HEAD 406d7a7, unmodified.
  DeepRagPipeline with answer_mode "sentence" against answer_mode
  "span" (level-3-deep/span_extract.py), use_rerank False in both
  arms, top_k 5, the same cases through both arms (paired).
- Metric: the Level 1 lexical pass, level-1-learn/rag_eval.py
  score_case with its frozen pass lines (faithfulness 0.8, context
  recall 0.8, answer relevance 0.5). This is the metric post hoc H3
  was scored on.
- Test and threshold: exact McNemar, the two-sided binomial test on
  discordant pairs at p = 0.5, computed exactly as
  real-data/paired_stats.py computes it. Alpha 0.05. H-C1 is
  CONFIRMED if and only if the span pass count exceeds the sentence
  pass count AND p < 0.05; otherwise it is NOT CONFIRMED.
- Effect reporting: both pass rates with Wilson 95% intervals (the
  repo convention), the discordant counts, and the paired difference
  in pass rates (span minus sentence) with a percentile bootstrap 95%
  interval, 10,000 resamples, seed 20261117. The bootstrap is the only
  randomness in the analysis; the fetch, the pipeline and the McNemar
  test are deterministic. Seed policy: that one seed, fixed here.

Secondary locked test (H-C2): the same comparison on 500 previously
unused HotpotQA distractor validation cases, rows 200 to 699 (the
prefix continuation of the exploratory first 200), corpus built by
build_hotpot from those rows only. Same arms, metric, test and
threshold. H-C2 is reported separately as CONFIRMED or NOT CONFIRMED
under the same rule; it does not change the H-C1 verdict.

Everything else stays exploratory: the rerank-on variants of both
datasets are run and recorded for completeness but carry no
confirmatory weight, and neither do post hoc H1, H2, the
embedding-judge comparisons, or any other framing of the span
comparison (including with-rerank McNemar tests). The embedding judge
is not part of the locked analysis: the hypothesis is about the
lexical pass, and the judge needs a model download.

Consequences: the confirmatory run uses new scripts only, under
real-data/confirmatory/, and writes only new files
(real-data/confirmatory/results_confirmatory.json and its sample
files). No frozen result file is edited, and the committed harness
code is not modified. The verdict is reported against the rule above
exactly as it comes out, confirmed or not confirmed.
