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
