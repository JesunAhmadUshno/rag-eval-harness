# Report: rag-eval-harness (P06)

Status: EXPLORATORY, 2026-11-08. Every result below comes from runs made
without a locked plan (see PROPOSAL.md), so the hypotheses are scored
as post hoc. A confirmatory cycle under a newly locked PROPOSAL.md is
planned; it is not part of this migration and nothing in it has run.

## Background

Retrieval-augmented generation (RAG) systems fail in three places:
retrieval misses the fact, the answer drifts from the context, or the
answer does not address the question. Public tools (Ragas class) score
these with LLM judges. This project builds a small harness a reader can
check by hand: lexical metrics, a budgeted judge layer, a CPU embedding
judge, a failure taxonomy and a CI regression gate, and runs it on
synthetic sets and on two public datasets.

Origin claim, not evidenced here: the project began as the public
version of a real pipeline that went from a 72.7 percent pass rate to
95 percent or more. That claim is self-reported. The private pipeline's
run logs are not in this repo and no public rerun exists, so it is not
a result of this project and is not used in any verdict.

## Method

Pipeline: BM25 over sentences (k1 1.5, b 0.75), extractive answers
(whole top sentence, or a span cut from it by
level-3-deep/span_extract.py), optionally reranked by
level-3-deep/reranker.py (stemmed query coverage, then stemmed token
F1, then BM25, over the top 5). Scoring: the Level 1 lexical metrics
(level-1-learn/rag_eval.py; pass lines faithfulness 0.8, context
recall 0.8, answer relevance 0.5), the embedding judge
(model-metrics/embedding_judge.py; similarity 0.30, support 0.25), and
the budgeted judge layer (level-2-build/judge.py). Data: synthetic sets
written for this project (8, 20 and 32 cases) and deterministic prefix
samples of SQuAD validation (500 cases) and HotpotQA distractor (200
cases), both CC BY-SA 4.0 (real-data/DATASETS.md). Statistics: Wilson
95% intervals, exact McNemar tests on paired per-case flags, an exact
sign test on reranker diagnostics, Bonferroni over the 12 rerank tests
(real-data/paired_stats.py). Compute: CPU only, Python 3.12 standard
library; the embedding judge needs the model2vec package. Runs: Muse
VM, Python 3.12.3, 2026-11-04 to 2026-11-07.

## Results

### Hypotheses (post hoc), scored

| Hypothesis | Result | Evidence | Verdict |
| --- | --- | --- | --- |
| H1 the reranker raises the synthetic Deep pass rate | 23 to 32 of 32; b11 class 5 to 13 of 13 | level-3-deep/results_deep.json | Supported, in-distribution only: the 12 d-cases were written after the b11 failure was seen |
| H2 the reranker raises gold-in-top-passage on real data | SQuAD 315 (Wilson 95% 0.587 to 0.671) to 319 of 500 (0.595 to 0.679), helped 26 vs hurt 22, sign p 0.6655; HotpotQA 39 to 47 of 200, helped 14 vs hurt 6, p 0.1153 | real-data/results_paired_stats.json | Not supported (miss) |
| H3 span answers beat sentence answers on lexical pass | SQuAD 24 to 113 of 500 without rerank (McNemar 21 vs 110, p < 0.0001); HotpotQA 1 to 7 of 200 (0 vs 6, p 0.0312) | real-data/results_paired_stats.json | Supported |

None of the 12 rerank tests survives Bonferroni (0.05 / 12); the
smallest is HotpotQA span judge passes, 3 vs 12, p 0.0352, a lead and
not a finding. SQuAD embedding-judge passes are 274 of 500 (0.504 to
0.591) without rerank and 281 (0.518 to 0.605) with it, McNemar 16 vs
23, p 0.3368.

### Every measured run


| Test | Result |
| --- | --- |
| Level 1 golden set, 8 synthetic cases, lexical metrics (method: level-1-learn/README.md), 2026-11-04 | 5 of 8 passed, pass rate 0.625 by design (3 cases built to fail, each named correctly: hallucination 1, retrieval_miss 1, wrong_or_incomplete_answer 1). Mean faithfulness 0.953, mean context recall 0.938, mean answer relevance 0.808. |
| Level 2 end-to-end run, 20 synthetic cases, BM25 retrieval plus extractive answer, scored by the Level 1 metrics (method: level-2-build/README.md), 2026-11-04 | The pipeline passed 19 of 20 cases (pass rate 0.950), with mean faithfulness 1.000, mean context recall 1.000, and mean answer relevance 0.970. The one failure is b11-storytime-when, labelled wrong_or_incomplete_answer. Judge pass: 10 calls made under a cap of 10, 10 cases skipped as not judged, 10 of 10 judged passed. |
| Level 3 Deep (compressed) run, 32 synthetic cases, same pipeline with and without the stemmed-overlap reranker, scored by the Level 1 metrics (method: level-3-deep/README.md), 2026-11-04 | Without rerank the pipeline passed 23 of 32 cases (pass rate 0.719); with rerank it passed 32 of 32 (pass rate 1.000). The b11 class of 13 cases (right document, wrong passage on top) went from 5 of 13 passed without rerank to 13 of 13 with rerank. Judge pass on the reranked run: 15 calls made, 15 of 15 judged passed. Regression gate: threshold 0.900, PASS. Tests: 15 Deep tests, 39 tests in total. |
| Real data run, SQuAD sample (REAL, public dataset, CC BY-SA 4.0), 100 cases, same pipeline, Level 1 metrics plus the embedding judge (method: real-data/README.md), 2026-11-04 (v1.1) | Lexical pass 1 of 100 with and without rerank. Context recall 0.830. Answer relevance 0.116 without rerank, 0.111 with. Embedding judge pass 49 of 100 without rerank, 46 of 100 with. Faithfulness 1.000 by construction (extractive answers). |
| Real data run, HotpotQA sample (REAL, public dataset, CC BY-SA 4.0), 60 cases, same method, 2026-11-04 (v1.1) | Lexical pass 0 of 60 with and without rerank. Context recall 0.523 in both variants. Answer relevance 0.066 without rerank, 0.068 with. Embedding judge pass 18 of 60 without rerank, 19 of 60 with. |
| Real data run, SQuAD sample (REAL, public dataset, CC BY-SA 4.0), 500 cases, sentence and span answer modes (method: real-data/README.md), 2026-11-04 (v1.2) | Sentence answers: lexical pass 24 of 500 without rerank, 22 with; context recall 0.828; relevance 0.160 and 0.157; embedding judge pass 274 and 281. Span answers: lexical pass 113 of 500 without rerank, 108 with; relevance 0.198 and 0.193; judge pass 115 and 112. The top passage holds the gold answer in 315 of 500 cases (319 with rerank). |
| Real data run, HotpotQA sample (REAL, public dataset, CC BY-SA 4.0), 200 cases, same method, 2026-11-04 (v1.2) | Sentence answers: lexical pass 1 of 200 in both variants; context recall 0.518; relevance 0.070 and 0.072; embedding judge pass 61 and 70. Span answers: lexical pass 7 of 200 without rerank, 9 with; relevance 0.080 and 0.104; judge pass 30 and 39. Retrieval is the binding constraint: recall 0.518 on a two-fact dataset. |


Per-variant real-data tables: real-data/README.md. Judge calibration
(Cohen's kappa against a gold-derived proxy, bootstrap intervals):
model-metrics/README.md and real-data/results_paired_stats.json.

## Misses

- H2: the flagship synthetic fix does not transfer to real data.
- The v1.2 reranker transfer test (real-data/rerank_experiment.py):
  no candidate helped both datasets, so no change shipped
  (docs/decisions/0002).
- The lexical metric is not valid on real sentence answers: SQuAD
  sentence answers pass lexically in 24 of 500 while the top passage
  holds the gold answer in 315.

## Threats to validity

- Synthetic sets were written by the author; the Deep b11 cases after
  the failure was seen.
- Faithfulness is 1.000 by construction (extractive answers), so the
  hallucination check is never exercised on real data.
- Judge agreement is measured against a proxy built from gold strings
  and the same lexical metric, so it is partly circular; no human
  labels exist.
- Samples, not full splits (500 of 10,570 SQuAD, 200 of 7,405
  HotpotQA). BM25 is the only retriever: no dense baseline and no
  reference implementation comparison, so the ML field profile's
  "baselines a reviewer would expect" item is not met.
- The agent-scoring track uses five scripted toy agents.

## Reproduction status

reproduce.sh regenerates results_deep.json, dashboard.md,
results_ablation.json, results_rerank_experiment.json,
results_paired_stats.json and calibration.json from the committed
evidence and fails on any byte change; CI runs it on Python 3.11 and
3.12. real-data/results_real.json is recorded evidence: its embedding
judge scores need model2vec and a one-time model download
(real-data/run_real_eval.py), so CI does not regenerate it. The
dashboard build fails unless its JavaScript ports reproduce the Python
results.

## Conclusion

The harness runs end to end on synthetic and real data, and its
statistics are reproducible from the evidence. The answer to the
question's second half is negative: the b11 reranker fix holds on the
set written around it and shows no detectable effect on real data. The
largest measured gain is the answer step (span extraction), not
reranking. A confirmatory cycle under a newly locked PROPOSAL.md is
planned.

## Fan-out

Written fan-out for v1.0, drafted 2026-11-04. Drafts only, nothing
posted externally by this set.

- Blog post: fanout/blog-post.md
- Tutorial (course module P06-rag-eval-harness): fanout/tutorial.md
- Website project page copy: fanout/website-page.md
- LinkedIn post draft (marked DRAFT NOT POSTED): fanout/linkedin-post.md
- Paper candidate brief: fanout/paper-candidate.md

## Dashboard

Live dashboard: https://jesunahmadushno.github.io/rag-eval-harness/

The dashboard is a React app in site/, built and deployed to GitHub
Pages by .github/workflows/pages.yml. Every number on it is read from
the result files in this repo at build time or computed in the browser
from them. What runs live: a BM25 and stemmed-reranker playground over
the Deep corpus (a JavaScript port of level-2-build/pipeline.py and
level-3-deep/reranker.py, with the ablation switches), the Level 1
lexical scorer, a judge threshold calibrator over the recorded
per-case embedding scores, and Wilson intervals plus exact paired
tests on the recorded real runs. A per-case browser replays the 700
recorded real questions in all four variants. `npm run build` runs
site/src/rag.check.mjs first and fails unless the browser code
reproduces results_deep.json (23 and 32 of 32), the Learn golden set
(5 of 8), calibration.json, results_ablation.json and
results_paired_stats.json. The earlier results lab in web/ stays as
source; everything it showed is on the new page. Synthetic and real
results are labelled and never mixed, there and here.

## Statistics and ablation (added in the research review, 2026-11-07)

- real-data/paired_stats.py writes real-data/results_paired_stats.json:
  Wilson 95% intervals for every pass rate, exact McNemar tests for
  with vs without rerank and sentence vs span, an exact sign test on
  the reranker diagnostics, a 2-D judge threshold sweep, a bootstrap
  interval on kappa and a 2-fold threshold fit. Headline: SQuAD judge
  passes 274 vs 281 is McNemar p 0.34; top-1 helped 26 vs hurt 22 is
  sign test p 0.67. None of the 12 rerank tests survives a Bonferroni
  correction; span vs sentence answers does (SQuAD p < 0.0001).
- level-3-deep/ablation.py writes level-3-deep/results_ablation.json:
  the plural -s stem rule does all the synthetic work (without it,
  24 of 32), and the F1 sort key is not needed (coverage then BM25
  also reaches 32 of 32, and puts gold on top in 331 SQuAD cases
  against 319 for the shipped key).
- The 32 of 32 Deep result is in-distribution: the 12 d-cases in the
  b11 class were written after the b11 failure was seen.
- The full research review, with the fixed gaps and the compute or
  data each open gap needs, is the Research review section below.

## Claim gate

Novelty is stated in the section below. The v1.1 claims went through the Jev
claim_check gate on 2026-11-04 (model jev-1.13.0): all five claims
routed REVIEW, none blocked, none overstated past their evidence.
The v1.2 claims go through the same gate at ship time; the routes
are recorded in the History section below.


## Novelty (moved from NOVELTY.md)

Status: updated at v1.2, 2026-11-04. The five public claims in this
cycle went through the Jev claim_check gate (model jev-1.13.0, 2,084
input tokens): all routed REVIEW, none blocked. REVIEW means the claims
stand as measured and are stated with their evidence, not upgraded to
certainty.

### What is actually different here

| Prior art | What it does | What this project does differently | Measured difference |
| --- | --- | --- | --- |
| Public eval tools (Ragas class) | Reference-free LLM-judged metrics for RAG, strong and widely used | This harness is stdlib-first and fully inspectable: lexical metrics a reader can verify by hand, a budgeted judge layer with cost accounting, and a CPU embedding judge with the model name inside every verdict | On the 500-case real SQuAD sample at v1.2, sentence answers pass 22 of 500 lexically against 281 of 500 by the embedding judge; span answers pass 108 against 112. The pair measures the metric mismatch instead of hiding it behind one score, in both answer modes |
| One-off notebook scoring | Ad hoc runs, numbers without a regression gate | A CI regression gate at 0.900, a failure taxonomy with counts, and levels that each ship with tests | 65 tests; the gate has held through Learn, Build, Deep, and the v1.1 and v1.2 upgrades |
| Synthetic-only portfolio demos | Benchmarks on data the author wrote, reported as results | Real public datasets (SQuAD, HotpotQA, CC BY-SA 4.0) run through the same pipeline, reported separately, including where the project looks bad | The Deep reranker fix (synthetic pass 0.719 to 1.000) does not transfer to real data. At v1.2 the transfer was tested with candidate fixes at five times the sample size: a hybrid key helped SQuAD and hurt HotpotQA, so nothing shipped. That negative result is published in the README, not buried |

### Honest size

The novelty is modest and methodological, not algorithmic: no new
metric is claimed. The value is a small, open harness that measures
itself on real data and prints what it finds, including a flagship fix
failing to transfer. If a reader needs an LLM judge or reference-free
scoring at scale, Ragas is the stronger tool today; this project says
so in its own dossier.

## Research review, 2026-11-07 (moved from docs/research-review.md)

Reviewed 2026-11-07 against a doctoral-level research checklist. Each
criterion gets the evidence, what the review fixed, and for every gap
still open, the exact compute or data it needs. The rule
applied: any gap that can be closed without a GPU, a paid API or a run
longer than about five minutes is closed here.

Every number below is produced by a script in this repo:
level-3-deep/results_deep.json, real-data/results_real.json,
real-data/results_rerank_experiment.json, model-metrics/calibration.json,
and the two files added by this change, real-data/results_paired_stats.json
(real-data/paired_stats.py) and level-3-deep/results_ablation.json
(level-3-deep/ablation.py). All of them run offline with the standard
library in a few seconds.

### Summary

| Criterion | Main remaining need |
| --- | --- |
| Research question | none |
| Hypotheses | pre-registration for the next experiment |
| Method | generative answer step (LLM) |
| Baselines | dense retrieval run, reference BM25 package |
| Statistics and uncertainty | human labels for metric validity |
| Reproducibility | none |
| Threats to validity | held-out set from an independent author |
| Related work | none |
| Limitations | none |

### 1. Research question

Can a small, transparent, standard-library harness measure RAG quality
honestly, and does a targeted fix for one failure class (right document,
wrong passage on top, "b11") hold up outside the data it was built on?
The question is clear and falsifiable, and the repo answers the second
half in the negative on real data. The question is sound but
was only sharpened into the transfer question after v1.0. No change
needed.

### 2. Hypotheses

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

### 3. Method

BM25 over sentences (k1 1.5, b 0.75), extractive answers, three lexical
metrics with documented pass lines (0.8 / 0.8 / 0.5), an embedding judge
(minishlab/potion-base-8M) on CPU, a budgeted judge layer, and a CI
regression gate at 0.900. The method is fully specified in code and
docstrings. The reranker is now ablated (section 4).

Remaining gap: faithfulness is 1.000 by construction because every
answer is a retrieved sentence or a span inside one, so the
hallucination metric is never exercised on real data. Needed: a
generative answer step, which means either a local instruct model on a
GPU or a paid LLM API, run over the 700 real questions in both rerank
settings (1,400 generations), then rescored by the existing metrics.

### 4. Baselines and ablations

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

### 5. Statistics and uncertainty

Before: pass counts were compared with no intervals and no
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

### 6. Reproducibility

Before: standard library only, committed samples and results, CI
reruns the Deep set and the regression gate. After: CI now also
reruns ablation.py and paired_stats.py and fails on any byte drift in
their outputs, and the dashboard build fails unless its JavaScript ports
reproduce results_deep.json, the Learn golden set, calibration.json,
results_ablation.json and results_paired_stats.json.

### 7. Threats to validity

Before: the synthetic 32 of 32 was presented next to real results
without saying the test set was written after the failure was seen.

Fixed in this change: the README and the dashboard now say that the 12
d-cases in the b11 class were written after the b11 failure, so 32 of
32 is an in-distribution confirmation. The origin claim (72.7 percent to
95 percent on a private pipeline) is labelled self-reported; the
project's self-assessment has since been moved out of the public repo. Multiple comparisons are stated with a
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

### 8. Related work

The earlier dashboard listed the RAG, Ragas, BM25, Lost in the Middle,
DPR, Sentence-BERT, SQuAD and HotpotQA papers. The new dashboard keeps
them and adds the sources for the two statistical methods now used
(McNemar 1947, Wilson 1927). The positioning against Ragas is
by metric names only, not by measured comparison (see section 4).

### 9. Limitations

The repo already named most limits in DOSSIER.md. After this change the
dashboard has a LIMITS window that pulls its numbers from the result
files, and this review adds the compute or data each one needs. Samples
rather than full splits remain: 500 SQuAD and 200 HotpotQA validation
questions. Needed for the full splits: a network download through
real-data/fetch_samples.py and the model2vec judge for the embedding
scores. The run time over the full splits has not been measured; it is
expected to exceed this change's five-minute budget, so it is left for
a dedicated run.

## History

### README at v1.2 (moved from README.md, 2026-11-08)

Status: v1.2 SPAN AND SCALE DONE 2026-11-04 (ROADMAP-V3-BATCH).
v1.1 plus: span extraction for the answer step
(level-3-deep/span_extract.py), real samples raised to 500 SQuAD and
200 HotpotQA cases, a reranker transfer test with candidate fixes
(none shipped; the negative result is recorded), an embedding judge
calibration check against gold-derived proxy labels, and a per-case
drill down in the results lab. Tests: 65 in total, regression gate
passing at a 0.900 threshold.
Project: P06. Fleet node: BlackBoxV2. Wave: Wave 1.

Level map:

- Level 1, Learn: the core idea, built small and clean, with a teaching path.
- Level 2, Build: a real working system other people can run.
- Level 3, Deep: benchmarks, optimization, evaluation, hard cases.

Reading order then: the scope (now PROPOSAL.md), the dossier and
novelty (now sections of this report), then level-1-learn/README.md,
level-2-build and level-3-deep.

### Dossier: past, present and future (moved from DOSSIER.md, 2026-11-04 to 2026-11-05)

Written under the documentation and publishing standard (past, present, future). Updated at ship time.

#### Past

Prior art for this project is named in NOVELTY.md (public eval tools (Ragas class) and one-off notebook scoring). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in SPEC.md and will be expanded with dated sources at the project's wave, before Build opens.

#### Present

Current demand evidence: The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.
Update 2026-11-04 (loop cycle): Level 1 Learn is done. A dependency-free lexical evaluator (faithfulness, context recall, answer relevance) scores an 8-case synthetic golden set at 5 of 8 passed by design, with a seed failure taxonomy (hallucination, retrieval_miss, wrong_or_incomplete_answer) and 11 unit tests asserting hand-computed values. Limits are named in level-1-learn/README.md: lexical metrics miss paraphrase, and the agent scoring track waits for P07 to exist.
Update 2026-11-04 (Build cycle): Level 2 Build is done. An end-to-end pipeline (BM25 over a 12-document corpus, extractive answer) passed 19 of 20 synthetic Build cases at mean relevance 0.970, with one kept failure (b11, right document, wrong passage). The judge layer ships with a hard call cap, deterministic sampling, and cost accounting; the default judge is a local lexical proxy, not an LLM. Agent protocol scoring is proven on toy demo agents only, because P07 does not exist yet. Full method and limits: level-2-build/README.md.
Update 2026-11-04 (Deep cycle, v1.0): Level 3 Deep (compressed) is done. A stemmed-overlap reranker raised the pass rate on the 32-case synthetic Deep set from 23 of 32 (0.719) without reranking to 32 of 32 (1.000) with reranking, and the b11 class from 5 of 13 to 13 of 13. The regression gate passes at a 0.900 threshold. Tests: 15 Deep tests, 39 in total. The judge remains the local lexical proxy, the corpora remain synthetic, and the agent work remains toy demo agents. Full method and limits: level-3-deep/README.md. The written fan-out set for v1.0 is in fanout/ (blog post, tutorial, website page copy, LinkedIn draft, paper candidate brief), drafts only, nothing posted.

#### Future

The rest of the v2 Deep scope is the v1.1 backlog in ROADMAP.md (LLM judge, generative answer step, real P07 agent evaluation, larger real corpus, learned reranking, workshop paper submission on Jesun's tap). Open problems beyond that sit in SPEC.md. Any forecast about this field is [unverified] unless a dated primary source is added here at the wave update.

#### Update 2026-11-04 (v1.1 research upgrade, Jesun's order 23:23 EST)

Real data: the harness now runs on two public datasets, license
verified from Hugging Face metadata on 2026-11-04 (both CC BY-SA 4.0):
a 100-case SQuAD validation sample and a 60-case HotpotQA distractor
sample, fetched by real-data/fetch_samples.py and recorded in
real-data/DATASETS.md. Measured (real-data/results_real.json): SQuAD
lexical pass 1 of 100, context recall 0.830, embedding judge pass 49 of
100; HotpotQA lexical pass 0 of 60, recall 0.523, judge pass 18 of 60.
The reranker does not transfer (SQuAD relevance 0.116 to 0.111). The
weak half is the answer step: whole sentences against short span golds.
Full analysis: real-data/README.md.
Model inside: model-metrics/embedding_judge.py, an embedding judge over
minishlab/potion-base-8M (Model2Vec, CPU, no key), with tests that
inject a fake embedder so CI downloads nothing. Thresholds are fixed
calibration constants, documented in the module.
Dashboard: the single-page docs site Jesun rejected is replaced by a
React app (web/, Vite), deployed through a Pages Actions workflow to
the same URL. Sections: Overview, Results Lab, Simulation (the lexical
evaluator ported to JavaScript, verified identical to the Python
scores on 20 cases), Data, Research (8 verified references), Docs,
Prototypes. Every chart number is generated from repo result files by
web/build_data.py.
Weaknesses named at v1.1: the answer step was weak on real data and
span extraction was not built; the reranker did not transfer and was
not yet fixed; the real samples were small, 100 and 60 cases against
full sets of 10,570 and 7,405; the model judge was a static embedding
model, not an LLM judge, and no human agreement study existed; judge
thresholds were calibration constants, not fitted on labelled data;
the dashboard showed summaries, not per-case drill-down for the real
runs.
Jev claim_check on the five public claims (model jev-1.13.0, 1,607
input tokens, spec and results in the goal hidden_files): squad real
numbers 0.49, reranker no transfer 0.67, faithfulness by construction
0.56, JS port fidelity 0.66, dataset licenses 0.70. All REVIEW under
the claim_check bands, none blocked, none clear. Public copy states
the numbers with their sources, which is what REVIEW requires.
References added and verified 2026-11-04: Lewis et al. 2020 (RAG),
Es et al. 2023 (Ragas, arXiv page read this cycle), Liu et al. 2023
(Lost in the Middle, arXiv page read this cycle), Robertson and
Zaragoza 2009 (BM25), Karpukhin et al. 2020 (DPR), Reimers and
Gurevych 2019 (Sentence-BERT), Rajpurkar et al. 2016 (SQuAD),
Yang et al. 2018 (HotpotQA).

#### Update 2026-11-04 (v1.2 span and scale, Jesun's blanket improvement order 23:52 EST)

Span extraction (v1.2 backlog item 1): level-3-deep/span_extract.py,
a documented dependency-free heuristic (novelty, question type,
anchoring, subject prior, length pressure), behind
DeepRagPipeline answer_mode="span"; sentence mode stays the default,
so the synthetic Deep gate and every earlier number keep the
behaviour they were measured with. Measured on the v1.2 samples,
sentence against span inside the same runs: SQuAD lexical pass 24 to
113 of 500 without rerank and 22 to 108 with, relevance 0.160 to
0.198; HotpotQA pass 1 to 7 and 1 to 9 of 200, relevance 0.070 to
0.080 and 0.072 to 0.104. The wrong_or_incomplete_answer count on
SQuAD falls from 477 to 391 (reranked).
Reranker transfer (backlog item 4 prep): rerank_experiment.py tested
a hybrid BM25 plus coverage key (alpha 0.3, 0.5, 0.7) and pool depth
10 on both datasets. Hybrid alpha 0.5 raises SQuAD top-passage gold
containment 319 to 330 and relevance 0.157 to 0.163, and lowers
HotpotQA containment 47 to 39 and relevance 0.072 to 0.068. No
variant helps both datasets, so no reranker change shipped; the
negative result and the diagnostics (SQuAD top-1 changes: 26 helped,
22 hurt; promoted passages are longer, not shorter, 19.9 against
17.1 tokens) are recorded in real-data/README.md and
results_rerank_experiment.json. The Deep regression gate passes
untouched at 1.000.
Samples (backlog item 6, in part): SQuAD 100 to 500 cases, HotpotQA
60 to 200, same deterministic prefix method; the v1.1 cases are the
first 100 and 60 of the new samples. The retrieval corpus grew with
them (SQuAD 323 to 2,248 passages), which lowers subset recall
(SQuAD shared-subset recall 0.750 against 0.830 at v1.1); the
real-data README states this wherever versions are compared.
Judge calibration (backlog item 5, the part that needs no
credential): calibrate_judge.py measured the embedding judge against
a proxy label built from gold data. Agreement with the proxy: SQuAD
span mode 0.902 (Cohen's kappa 0.72), HotpotQA span mode 0.925
(kappa 0.73); sentence mode 0.790 and 0.820 (kappa 0.56 and 0.57).
The threshold sweep pulls opposite ways per mode, so the shipped
constants (similarity 0.30, support 0.25) stay, documented as
checked, not fitted. The human agreement study and the LLM judge
remain open; the LLM judge still needs Jesun's credential decision.
Dashboard: the Results Lab gains a per-case drill down for the real
runs (dataset, answer mode, verdict, and failure label filters over
the recorded per-case results), and its analysis copy is rewritten
from the v1.2 numbers. Site data is generated by web/build_data.py
from the result files, as before.
Tests: 65 in total (12 new span tests, real-data tests extended to
the new samples and variants), ruff clean, Deep regression gate PASS.

Weaknesses at v1.2, against the v1.1 list above:
- Answer step: span extraction shipped and measured; the residue is
  the extractor's named error classes (same-type distractors, yes or
  no golds, spans cut from the wrong sentence when retrieval errs).
- Reranker transfer: the transfer test is now run with candidate
  fixes and baselines a learned reranker must beat; the underlying
  weakness stands.
- Real samples: fivefold and threefold growth; still samples, not
  the full validation splits.
- Model judge: the proxy agreement check is done (kappa 0.72 to 0.73
  in span mode); the human study and the LLM judge remain open.
- Judge thresholds: checked with a sweep and an agreement study;
  still not fitted on labelled data, and the optimum differs by
  answer mode.
- Dashboard drill down: shipped.
- New at v1.2: retrieval is the binding ceiling and dense retrieval
  is not built (HotpotQA recall 0.518).
Jev claim_check on the five v1.2 public claims (model jev-1.13.0,
2,084 input tokens, spec and results in the goal hidden_files,
jev-p06-v12-claim-*.json): span_extraction_gain 0.72,
corpus_growth_caveat 0.48, reranker_experiment_negative 0.45,
judge_calibration 0.33, sample_method 0.19. All REVIEW under the
claim_check bands, none blocked, none clear. The weakest route,
sample_method at 0.19, rests on the verification run quoted in the
spec; the public check is fetch_samples.py itself, which any reader
can re-run. Public copy states each number with its source file,
which is what REVIEW requires.

### Roadmap history (moved from ROADMAP.md)

v1.0 (2026-11-04) closes Learn, Build, and compressed Deep. Compressed
Deep delivered the single hardest Deep capability (the reranking fix
for the b11 failure class, proven on the expanded Deep golden set),
plus the CI regression gate, the failure taxonomy, and the quality
dashboard. The items below are the rest of the v2 Deep scope, named
here as the v1.1 backlog. None of them is done, and none is claimed.

#### v1.1 backlog

1. LLM judge: replace or augment the local LexicalJudge proxy with a
   real LLM judge behind the existing BudgetedJudge interface, with
   the same cap, sampling, and cost accounting, and a measured
   agreement study against human labels. Needs a credential decision
   from Jesun; no credential is created by this project on its own.
2. Generative answer step: a non-extractive answerer, where
   faithfulness stops being 1.000 by construction and the harness
   must catch unsupported claims. The Deep taxonomy already carries
   the hallucination label for this.
3. Real agent evaluation: score the P07 agent-from-scratch agent on
   the Deep task protocol once P07 exists, replacing the five toy
   demo agents used at Deep level to prove the taxonomy.
4. Larger real corpus: move beyond the synthetic Northlight Library
   corpus (24 documents, 32 cases at v1.0) to a larger corpus with
   real documents and a golden set in the hundreds, and re-baseline
   the regression gate from that run.
5. Cross-encoder or learned reranking: compare the stemmed overlap
   reranker against a learned reranker on the same Deep set, with
   the same before and after reporting discipline.
6. Workshop paper submission: the Deep results are the paper track
   named in SPEC.md (MLSys, NeurIPS, or ICLR workshop). The numbers
   are reproducible from this repo at v1.0. Submission itself is
   Jesun's tap and is not part of any automated run.

#### v1.1 shipped (2026-11-04, research upgrade)

Done from the backlog above: item 4 in part (real public datasets,
SQuAD and HotpotQA samples, run and reported separately; the
hundreds-scale golden set is still open), and a first step on item 1
(a model judge exists, but it is an embedding judge, not an LLM judge;
the human agreement study is still open). Added in v1.1: the React
results lab on GitHub Pages replacing the single-page docs.

#### v1.2 backlog (status at the v1.2 ship, 2026-11-04)

1. Span extraction: DONE in v1.2 (level-3-deep/span_extract.py).
   SQuAD lexical passes 22 to 108 and HotpotQA 1 to 9, reranked runs,
   sentence against span on the same cases and corpora.
2. Generative answer step (was v1.1 item 2), behind the same metrics.
   Still open.
3. Dense retrieval next to BM25 (DPR class), compared on the same
   real samples. Still open; v1.2 names it the binding constraint
   for HotpotQA (context recall 0.518).
4. Learned reranking (was v1.1 item 5). Still open. v1.2 ran the
   transfer test (real-data/rerank_experiment.py): a hybrid BM25
   plus coverage key helped SQuAD and hurt HotpotQA, so no change
   shipped. A learned reranker must beat the shipped reranker on
   both datasets at once, on these samples.
5. LLM judge with a human agreement study (rest of v1.1 item 1).
   Still open; needs Jesun's credential decision. v1.2 did the part
   that needs no credential: an agreement check of the embedding
   judge against gold-derived proxy labels (kappa 0.72 to 0.73 in
   span mode; model-metrics/calibration.json). The human study
   itself is still not done and is not claimed.
6. Larger real samples: DONE in part in v1.2 (SQuAD 500, HotpotQA
   200, same deterministic prefix method; the full validation splits
   remain open).
7. Real agent evaluation (was v1.1 item 3), once P07 exists.
   Still open.
8. Workshop paper submission (was v1.1 item 6): Jesun's tap.

#### v1.2 shipped (2026-11-04, Jesun's blanket improvement order 23:52 EST)

Backlog items 1 and 6 (in part) above, plus: a per-case drill down
in the dashboard for the real runs (filterable by dataset, answer
mode, verdict, and failure label); the reranker transfer test with
its negative result recorded, not dressed up; and the judge
calibration check. Tests: 65. Weaknesses are recorded in the
dossier section above at ship time.

#### v1.3 backlog

1. Dense retrieval next to BM25, aimed at HotpotQA recall.
2. Generative answer step, behind the same metrics, where
   faithfulness stops being 1.000 by construction.
3. Learned reranking against the v1.2 experiment baselines.
4. A mode-specific judge threshold fitted on labelled data, then
   the human agreement study (needs labels; the LLM judge part
   needs Jesun's credential decision).
5. Full validation splits for the real samples, re-baselined.
6. Span extraction round 2: same-type distractor spans (two team
   names, two dates in one sentence) are the extractor's named
   error class; a verb-argument or entity-type signal is the
   candidate fix.
7. Real agent evaluation, once P07 exists.
8. Workshop paper submission: Jesun's tap.

#### Standing rules for v1.1 work

- The regression gate in level-3-deep stays green through every
  change, or the change does not land.
- baseline.json is updated only by a deliberate reviewed run, never
  automatically, and the new numbers are recorded with their date.
- Every new number in a README comes from a run executed in that
  cycle. Nothing is carried forward as if it were freshly measured.
