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
