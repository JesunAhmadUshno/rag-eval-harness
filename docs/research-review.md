# Research review: rag-eval-harness v1.2

Reviewed 2026-11-07 against a doctoral-level research rubric. Each
criterion gets a grade before and after this change (A strong, B
adequate, C weak, D missing), the evidence, what this change fixed, and
for every gap still open, the exact compute or data it needs. The rule
applied: any gap that can be closed without a GPU, a paid API or a run
longer than about five minutes is closed here.

Every number below is produced by a script in this repo:
level-3-deep/results_deep.json, real-data/results_real.json,
real-data/results_rerank_experiment.json, model-metrics/calibration.json,
and the two files added by this change, real-data/results_paired_stats.json
(real-data/paired_stats.py) and level-3-deep/results_ablation.json
(level-3-deep/ablation.py). All of them run offline with the standard
library in a few seconds.

## Summary

| Criterion | Before | After | Main remaining need |
| --- | --- | --- | --- |
| Research question | B | B | none |
| Hypotheses | C | B | pre-registration for the next experiment |
| Method | B | B+ | generative answer step (LLM) |
| Baselines | C | B- | dense retrieval run, reference BM25 package |
| Statistics and uncertainty | D | B+ | human labels for metric validity |
| Reproducibility | A- | A | none |
| Threats to validity | C | B+ | held-out set from an independent author |
| Related work | B- | B | none |
| Limitations | B | A- | none |

## 1. Research question

Can a small, transparent, standard-library harness measure RAG quality
honestly, and does a targeted fix for one failure class (right document,
wrong passage on top, "b11") hold up outside the data it was built on?
The question is clear and falsifiable, and the repo answers the second
half in the negative on real data. Grade B: the question is sound but
was only sharpened into the transfer question after v1.0. No change
needed.

## 2. Hypotheses

Before: no hypothesis was written down before an experiment. After:
the implied hypotheses are stated here, explicitly marked post hoc.

- H1 (synthetic): the stemmed-overlap reranker raises the Deep pass
  rate. Result: 23 to 32 of 32, b11 class 5 to 13 of 13. Confirmed, but
  in-distribution (see section 7).
- H2 (transfer): the reranker raises gold-in-top-passage on real data.
  Result: SQuAD 315 to 319 of 500, HotpotQA 39 to 47 of 200. Exact
  McNemar p 0.6655 and 0.1153. Not supported.
- H3 (answer step): span answers beat sentence answers on lexical pass.
  Result: SQuAD 24 to 113 of 500 (p < 0.0001), HotpotQA 1 to 7 of 200
  (p 0.0312). Supported.

Remaining gap: none of these was registered before the data was seen.
Needed: a written, dated pre-registration (a markdown file hashed into
git before the run) for the next experiment, for example the dense
retrieval baseline below. No compute needed, only the discipline of
writing it first.

## 3. Method

BM25 over sentences (k1 1.5, b 0.75), extractive answers, three lexical
metrics with documented pass lines (0.8 / 0.8 / 0.5), an embedding judge
(minishlab/potion-base-8M) on CPU, a budgeted judge layer, and a CI
regression gate at 0.900. The method is fully specified in code and
docstrings. Grade B+ after this change because the reranker is now
ablated (section 4).

Remaining gap: faithfulness is 1.000 by construction because every
answer is a retrieved sentence or a span inside one, so the
hallucination metric is never exercised on real data. Needed: a
generative answer step, which means either a local instruct model on a
GPU or a paid LLM API, run over the 700 real questions in both rerank
settings (1,400 generations), then rescored by the existing metrics.

## 4. Baselines and ablations

Before: BM25 vs BM25 plus rerank, and the v1.2 hybrid and pool-10
variants. No ablation of the reranker's own parts.

Fixed in this change: level-3-deep/ablation.py removes one part at a
time and measures the synthetic set and real top-1 gold separately.

- The plural -s stem rule does all the synthetic work: without it the
  Deep set falls to 24 of 32 and the b11 class to 5 of 13. Dropping any
  of the other four rules leaves 31 or 32 of 32.
- The F1 sort key is not needed: coverage then BM25 also reaches 32 of
  32, and on real SQuAD puts gold on top in 331 cases against 319 for
  the shipped key. F1-first keys fall to 260. The F1 key's bias toward
  short passages, already suspected in v1.2 (promoted 19.92 vs demoted
  17.14 tokens), is the likely reason.

Remaining gaps:

- No dense retrieval baseline, although retrieval is the stated
  ceiling (HotpotQA context recall 0.518). Needed: the third-party
  model2vec package and a one-time download of an embedding model (for
  example potion-base-8M, already used by the judge), then embedding the
  committed passages on CPU. This needs network access and a dependency
  outside the standard library, so it is out of scope for this
  offline change. It must be pre-registered first (section 2).
- No comparison against a reference implementation. Needed: rank_bm25
  or Pyserini (Pyserini needs Java) for a BM25 cross-check on the same
  samples, and Ragas, which needs an LLM (GPU or paid API). Both break
  the repo's standard-library rule, so they need an explicit decision
  to add an optional dependency.

## 5. Statistics and uncertainty

Before: grade D. Pass counts were compared with no intervals and no
tests, although every comparison is paired (the same cases go through
each variant).

Fixed in this change (real-data/paired_stats.py, also computed live on
the dashboard and checked against each other at build time):

- Wilson 95% intervals for every pass rate. Example: SQuAD judge passes
  274 of 500 (0.504 to 0.591) without rerank and 281 of 500 (0.518 to
  0.605) with it.
- Exact McNemar tests on the per-case flags. SQuAD judge: 16 cases pass
  only without rerank, 23 only with, p 0.3368. None of the 12 rerank
  tests survives a Bonferroni correction (0.05 / 12); the smallest is
  HotpotQA span judge passes, 3 vs 12, p 0.0352, which should be read as
  a lead, not a finding.
- Exact sign test on the reranker diagnostics: SQuAD top-1 helped 26 vs
  hurt 22, p 0.6655; HotpotQA 14 vs 6, p 0.1153. "No transfer" cannot be
  told apart from zero effect.
- Judge calibration: a 2-D threshold sweep (similarity 0.10 to 0.80,
  support 0.00 to 0.50, steps of 0.05) replaces the 1-D sweep; a seeded
  bootstrap (2,000 resamples) puts kappa at the shipped thresholds at
  0.5607 (0.488 to 0.6268) for SQuAD sentence answers and 0.7111 (0.6315
  to 0.7843) for span answers; a 2-fold fit (even vs odd case index)
  shows that a fitted pair beats the shipped pair on held-out SQuAD
  halves but not always on HotpotQA, so the shipped constants are
  defensible but not optimal.

Remaining gap: every agreement number is against a proxy label built
from gold strings plus the same lexical relevance metric, so it is
partly circular, and the lexical metric's own validity is unmeasured.
Needed: human correctness labels for a stratified sample, for example
200 SQuAD and 200 HotpotQA answers labelled by two annotators
(inter-annotator kappa reported), which then serves as the reference
for both the lexical pass rule and the judge. This is human time, not
compute.

## 6. Reproducibility

Before: A-. Standard library only, committed samples and results, CI
reruns the Deep set and the regression gate. After: A. CI now also
reruns ablation.py and paired_stats.py and fails on any byte drift in
their outputs, and the dashboard build fails unless its JavaScript ports
reproduce results_deep.json, the Learn golden set, calibration.json,
results_ablation.json and results_paired_stats.json.

## 7. Threats to validity

Before: C. The synthetic 32 of 32 was presented next to real results
without saying the test set was written after the failure was seen.

Fixed in this change: the README and the dashboard now say that the 12
d-cases in the b11 class were written after the b11 failure, so 32 of
32 is an in-distribution confirmation. The origin claim (72.7 percent to
95 percent on a private pipeline) and the project self-grade are
labelled self-reported. Multiple comparisons are stated with a
Bonferroni threshold.

Remaining gaps:

- A held-out synthetic set written blind to the reranker cannot be
  produced by anyone who has read reranker.py, which includes the author
  of this change. Needed: about 30 new library questions with gold
  answers written by a person who has not seen the reranker or the b11
  cases, committed with a date before the first run.
- The origin claim needs the private pipeline's run logs or a public
  rerun; neither is in the repo.
- The agent-scoring track uses five scripted toy agents, so its 100
  percent and 0 percent success rates show the scorer working, not agent
  behaviour. Needed: a real agent under test (the planned P07 project).

## 8. Related work

The earlier dashboard listed the RAG, Ragas, BM25, Lost in the Middle,
DPR, Sentence-BERT, SQuAD and HotpotQA papers. The new dashboard keeps
them and adds the sources for the two statistical methods now used
(McNemar 1947, Wilson 1927). Grade B: the positioning against Ragas is
by metric names only, not by measured comparison (see section 4).

## 9. Limitations

The repo already named most limits in DOSSIER.md. After this change the
dashboard has a LIMITS window that pulls its numbers from the result
files, and this review adds the compute or data each one needs. Samples
rather than full splits remain: 500 SQuAD and 200 HotpotQA validation
questions. Needed for the full splits: a network download through
real-data/fetch_samples.py and the model2vec judge for the embedding
scores. The run time over the full splits has not been measured; it is
expected to exceed this change's five-minute budget, so it is left for
a dedicated run.
