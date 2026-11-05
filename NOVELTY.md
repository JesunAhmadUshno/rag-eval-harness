# NOVELTY: rag-eval-harness (P06)

Status: updated at v1.2, 2026-11-04. The five public claims in this
cycle went through the Jev claim_check gate (model jev-1.13.0, 2,084
input tokens): all routed REVIEW, none blocked. REVIEW means the claims
stand as measured and are stated with their evidence, not upgraded to
certainty.

## What is actually different here

| Prior art | What it does | What this project does differently | Measured difference |
| --- | --- | --- | --- |
| Public eval tools (Ragas class) | Reference-free LLM-judged metrics for RAG, strong and widely used | This harness is stdlib-first and fully inspectable: lexical metrics a reader can verify by hand, a budgeted judge layer with cost accounting, and a CPU embedding judge with the model name inside every verdict | On the 500-case real SQuAD sample at v1.2, sentence answers pass 22 of 500 lexically against 281 of 500 by the embedding judge; span answers pass 108 against 112. The pair measures the metric mismatch instead of hiding it behind one score, in both answer modes |
| One-off notebook scoring | Ad hoc runs, numbers without a regression gate | A CI regression gate at 0.900, a failure taxonomy with counts, and levels that each ship with tests | 65 tests; the gate has held through Learn, Build, Deep, and the v1.1 and v1.2 upgrades |
| Synthetic-only portfolio demos | Benchmarks on data the author wrote, reported as results | Real public datasets (SQuAD, HotpotQA, CC BY-SA 4.0) run through the same pipeline, reported separately, including where the project looks bad | The Deep reranker fix (synthetic pass 0.719 to 1.000) does not transfer to real data. At v1.2 the transfer was tested with candidate fixes at five times the sample size: a hybrid key helped SQuAD and hurt HotpotQA, so nothing shipped. That negative result is published in the README, not buried |

## Honest size

The novelty is modest and methodological, not algorithmic: no new
metric is claimed. The value is a small, open harness that measures
itself on real data and prints what it finds, including a flagship fix
failing to transfer. If a reader needs an LLM judge or reference-free
scoring at scale, Ragas is the stronger tool today; this project says
so in its own dossier.
