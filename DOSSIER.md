# DOSSIER: rag-eval-harness (P06) v1, 2026-11-04

Written under the documentation and publishing standard (past, present, future). Updated at ship time.

## Past

Prior art for this project is named in NOVELTY.md (public eval tools (Ragas class) and one-off notebook scoring). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in SPEC.md and will be expanded with dated sources at the project's wave, before Build opens.

## Present

Current demand evidence: hiring value 5 of 5 (evaluation in 22/56, v2 build rank 1) [confirmed, fleet and scoring pass 2026-11-04; for P23 to P29, the decision pack 2026-11-04]. The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.
Update 2026-11-04 (loop cycle): Level 1 Learn is done. A dependency-free lexical evaluator (faithfulness, context recall, answer relevance) scores an 8-case synthetic golden set at 5 of 8 passed by design, with a seed failure taxonomy (hallucination, retrieval_miss, wrong_or_incomplete_answer) and 11 unit tests asserting hand-computed values. Limits are named in level-1-learn/README.md: lexical metrics miss paraphrase, and the agent scoring track waits for P07 to exist.
Update 2026-11-04 (Build cycle): Level 2 Build is done. An end-to-end pipeline (BM25 over a 12-document corpus, extractive answer) passed 19 of 20 synthetic Build cases at mean relevance 0.970, with one kept failure (b11, right document, wrong passage). The judge layer ships with a hard call cap, deterministic sampling, and cost accounting; the default judge is a local lexical proxy, not an LLM. Agent protocol scoring is proven on toy demo agents only, because P07 does not exist yet. Full method and limits: level-2-build/README.md.

## Future

Open problems and the project's next steps sit in the Deep level scope in SPEC.md. Any forecast about this field is [unverified] unless a dated primary source is added here at the wave update.
