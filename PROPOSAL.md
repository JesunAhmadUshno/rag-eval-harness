# Proposal: rag-eval-harness (P06)

Status: DRAFT, not locked, 2026-11-08. This project was built without a
locked plan. Git history shows the first commit (3b9e4bd, 2026-11-04) is
a scope scaffold with no hypotheses or pass lines, and code and results
followed the same day; the hypotheses below were written after the data
was seen (research review, 2026-11-07). The repo is therefore "not
pre-registered" under the portfolio standard v2 (docs/METHOD.md section
7 of the portfolio index), and no lock tag is placed on any past commit.

A confirmatory cycle is planned: this file will be rewritten with its
hypotheses, pass lines and analysis plan, committed, and tagged
`proposal-v1` before any confirmatory run. From that tag on it is never
edited, and a test pins its SHA-256. Choosing the hypotheses and pass
lines and running anything that needs a model download, a GPU or a paid
API is the Owner's decision.

## Question

Can a small, transparent, standard-library harness measure RAG quality
honestly, and does a targeted fix for one failure class (right document,
wrong passage on top, "b11") hold up outside the data it was built on?

Boundary: this project judges a RAG system; P05 builds one.

## System under study

A BM25 retriever over sentences (k1 1.5, b 0.75) with an extractive
answer step (whole sentence, or a span cut from it), optionally
reranked by a stemmed query-passage overlap reranker over the top 5
passages, scored by three lexical metrics (faithfulness, context
recall, answer relevance; pass lines 0.8 / 0.8 / 0.5), a budgeted judge
layer, and a CPU embedding judge (minishlab/potion-base-8M).

## Prior work

Public evaluation tools of the Ragas class give reference-free,
LLM-judged RAG metrics (Es et al. 2023). BM25 (Robertson and Zaragoza
2009) is the sparse baseline; dense passage retrieval (Karpukhin et al.
2020) is the reviewer-expected stronger retriever. Long-context models
use the top of the context best (Liu et al., Lost in the Middle), which
is why passage order matters. SQuAD (Rajpurkar et al. 2016) and
HotpotQA (Yang et al. 2018) supply human gold answers. The full
comparison with prior art is in REPORT.md (Novelty).

## Hypotheses of the exploratory cycle (post hoc, not pre-registered)

Stated in the research review on 2026-11-07, after every result below
existed. They are scored in REPORT.md and carry no confirmatory weight.

- H1 (synthetic): the stemmed-overlap reranker raises the Deep pass rate.
- H2 (transfer): the reranker raises gold-in-top-passage on real data.
- H3 (answer step): span answers beat sentence answers on lexical pass.

## Candidates for the confirmatory cycle (for the Owner to choose)

Drawn from the open gaps in REPORT.md. None is chosen, none has a pass
line yet, and nothing has run.

- A dense retrieval baseline next to BM25 on the committed samples,
  aimed at HotpotQA context recall (needs the model2vec package and a
  one-time model download).
- The reranker on a held-out synthetic set written by someone who has
  not seen reranker.py or the b11 cases (needs a second author).
- Human correctness labels for a stratified sample as the reference
  for the lexical rule and the judge (needs annotator time).
- A generative answer step, so faithfulness stops being 1.000 by
  construction (needs a GPU or a paid API).

## Original scope (moved from SPEC.md, Wave 0 scaffold spec, 2026-11-04)

Phase skill: spec-driven-development (house engineering pipeline).
Status: Wave 0 scaffold spec, from Roadmap v2 text and the v3 decision pack. Scope and acceptance criteria below are the v2 section text, kept as the source of truth until the project's wave opens its own spec pass.

Fleet node: BlackBoxV2. Wave: Wave 1.

### Project section text (Roadmap v2, or the v3 candidate text for P23 to P29)

rag-eval-harness: EXPAND

Subject: evaluation systems. This project carries his strongest seed asset: the public version of the work that took a real RAG pipeline from a 72.7 percent pass rate to 95 percent or more [self-reported, his roadmap and the career documentation; the public repo is where the numbers become checkable].
v1 core [confirmed, v1]: golden question set with hand-checked rules; automated pipeline (faithfulness, answer relevance, context recall; LLM judge plus human labels); Deep adds CI regression tests, a failure taxonomy, and a quality dashboard.
Added track, agent evaluation:
- Learn: score one agent (the P07 agent, once it exists) on a fixed task set: success rate, steps used, cost per task.
- Build: the harness takes any agent that speaks a simple task protocol and scores it the same way it scores a RAG pipeline; judge calls budgeted and sampled, with the cost control written up (register item 702).
- Deep: an agent failure taxonomy beside the RAG one (tool misuse, loop traps, silent wrong answers), with counts from real runs.
Paper track (not a level, a duty of this project) [confirmed, career documentation Section D]: the Deep results become a workshop paper aimed at an MLSys, NeurIPS, or ICLR workshop. The numbers must be reproducible from this public repo before any submission. Submission is Jesun's tap [confirmed, board plan decision 3].
Fan-out: Book chapter "Proof, Not Claims". Paper angle: the workshop paper itself. Course module: P06-rag-eval-harness.

### Acceptance criteria (scaffold level)

- Learn closes when the level-1-learn code runs, its README teaches the idea, and a fresh-eyes reader can follow it.
- Build closes when the system runs end to end, tests pass, and one benchmark or result table with method is in the README.
- Deep closes when the Deep scope in the section text is done, the failure modes are written, and the dossier is updated to ship state.
- No level closes on a claim. Evidence only: code, tests, numbers, links.
