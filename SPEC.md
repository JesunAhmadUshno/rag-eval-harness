# SPEC: rag-eval-harness (P06)

Phase skill: spec-driven-development (house engineering pipeline).
Status: Wave 0 scaffold spec, from Roadmap v2 text and the v3 decision pack. Scope and acceptance criteria below are the v2 section text, kept as the source of truth until the project's wave opens its own spec pass.

Fleet node: BlackBoxV2. Wave: Wave 1.
Hiring evidence: 5 of 5 (evaluation in 22/56, v2 build rank 1) [confirmed, fleet and scoring pass 2026-11-04, or the decision pack for P23 to P29].

## Project section text (Roadmap v2, or the v3 candidate text for P23 to P29)

rag-eval-harness: EXPAND

Subject: evaluation systems. This project carries his strongest seed asset: the public version of the work that took a real RAG pipeline from a 72.7 percent pass rate to 95 percent or more [self-reported, his roadmap and the career documentation; the public repo is where the numbers become checkable].
v1 core [confirmed, v1]: golden question set with hand-checked rules; automated pipeline (faithfulness, answer relevance, context recall; LLM judge plus human labels); Deep adds CI regression tests, a failure taxonomy, and a quality dashboard.
Added track, agent evaluation:
- Learn: score one agent (the P07 agent, once it exists) on a fixed task set: success rate, steps used, cost per task.
- Build: the harness takes any agent that speaks a simple task protocol and scores it the same way it scores a RAG pipeline; judge calls budgeted and sampled, with the cost control written up (register item 702).
- Deep: an agent failure taxonomy beside the RAG one (tool misuse, loop traps, silent wrong answers), with counts from real runs.
Paper track (not a level, a duty of this project) [confirmed, career documentation Section D]: the Deep results become a workshop paper aimed at an MLSys, NeurIPS, or ICLR workshop. The numbers must be reproducible from this public repo before any submission. Submission is Jesun's tap [confirmed, board plan decision 3].
Fan-out: Book chapter "Proof, Not Claims". Paper angle: the workshop paper itself. Course module: P06-rag-eval-harness.

## Acceptance criteria (scaffold level)

- Learn closes when the level-1-learn code runs, its README teaches the idea, and a fresh-eyes reader can follow it.
- Build closes when the system runs end to end, tests pass, and one benchmark or result table with method is in the README.
- Deep closes when the Deep scope in the section text is done, the failure modes are written, and the dossier is updated to ship state.
- No level closes on a claim. Evidence only: code, tests, numbers, links.
