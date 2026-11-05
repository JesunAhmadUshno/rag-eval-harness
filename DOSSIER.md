# DOSSIER: rag-eval-harness (P06) v1, 2026-11-04

Written under the documentation and publishing standard (past, present, future). Updated at ship time.

## Past

Prior art for this project is named in NOVELTY.md (public eval tools (Ragas class) and one-off notebook scoring). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in SPEC.md and will be expanded with dated sources at the project's wave, before Build opens.

## Present

Current demand evidence: hiring value 5 of 5 (evaluation in 22/56, v2 build rank 1) [confirmed, fleet and scoring pass 2026-11-04; for P23 to P29, the decision pack 2026-11-04]. The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.
Update 2026-11-04 (loop cycle): Level 1 Learn is done. A dependency-free lexical evaluator (faithfulness, context recall, answer relevance) scores an 8-case synthetic golden set at 5 of 8 passed by design, with a seed failure taxonomy (hallucination, retrieval_miss, wrong_or_incomplete_answer) and 11 unit tests asserting hand-computed values. Limits are named in level-1-learn/README.md: lexical metrics miss paraphrase, and the agent scoring track waits for P07 to exist.
Update 2026-11-04 (Build cycle): Level 2 Build is done. An end-to-end pipeline (BM25 over a 12-document corpus, extractive answer) passed 19 of 20 synthetic Build cases at mean relevance 0.970, with one kept failure (b11, right document, wrong passage). The judge layer ships with a hard call cap, deterministic sampling, and cost accounting; the default judge is a local lexical proxy, not an LLM. Agent protocol scoring is proven on toy demo agents only, because P07 does not exist yet. Full method and limits: level-2-build/README.md.
Update 2026-11-04 (Deep cycle, v1.0): Level 3 Deep (compressed) is done. A stemmed-overlap reranker raised the pass rate on the 32-case synthetic Deep set from 23 of 32 (0.719) without reranking to 32 of 32 (1.000) with reranking, and the b11 class from 5 of 13 to 13 of 13. The regression gate passes at a 0.900 threshold. Tests: 15 Deep tests, 39 in total. The judge remains the local lexical proxy, the corpora remain synthetic, and the agent work remains toy demo agents. Full method and limits: level-3-deep/README.md. The written fan-out set for v1.0 is in fanout/ (blog post, tutorial, website page copy, LinkedIn draft, paper candidate brief), drafts only, nothing posted.

## Future

The rest of the v2 Deep scope is the v1.1 backlog in ROADMAP.md (LLM judge, generative answer step, real P07 agent evaluation, larger real corpus, learned reranking, workshop paper submission on Jesun's tap). Open problems beyond that sit in SPEC.md. Any forecast about this field is [unverified] unless a dated primary source is added here at the wave update.

## Update 2026-11-04 (v1.1 research upgrade, Jesun's order 23:23 EST)

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
Grade, v1.1: 8,000 of 10,000. Deductions: answer step weak on real
data, span extraction not built (-600); reranker does not transfer and
is not yet fixed (-300); real samples are small, 100 and 60 cases
against full sets of 10,570 and 7,405 (-300); the model judge is a
static embedding model, not an LLM judge, and no human agreement study
exists (-400); judge thresholds are calibration constants, not fitted
on labelled data (-200); the dashboard shows summaries, not per-case
drill-down for the real runs (-200).
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

## Update 2026-11-04 (v1.2 span and scale, Jesun's blanket improvement order 23:52 EST)

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

Grade, v1.2: 9,050 of 10,000, against 8,000 at v1.1. What moved,
deduction by deduction (v1.1 deduction to v1.2 deduction):
- Answer step weak, span extraction not built: -600 to -150. Span
  extraction shipped and measured; the residue is the extractor's
  named error classes (same-type distractors, yes or no golds,
  spans cut from the wrong sentence when retrieval errs).
- Reranker does not transfer, not yet fixed: -300 to -200. The
  transfer test is now run with candidate fixes and baselines a
  learned reranker must beat; the underlying weakness stands.
- Real samples small: -300 to -100. Fivefold and threefold growth;
  still samples, not the full validation splits.
- Model judge is not an LLM judge, no human agreement study: -400
  to -250. The proxy agreement check is done (kappa 0.72 to 0.73 in
  span mode); the human study and the LLM judge remain open.
- Judge thresholds are calibration constants: -200 to -100. Checked
  with a sweep and an agreement study; still not fitted on labelled
  data, and the optimum differs by answer mode.
- Dashboard summaries only, no per-case drill down: -200 to 0.
  Shipped.
- New at v1.2: retrieval is the binding ceiling and dense retrieval
  is not built (HotpotQA recall 0.518): -150.
Total deductions -950.
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
