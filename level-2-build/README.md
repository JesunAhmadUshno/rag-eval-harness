# Level 2, Build: rag-eval-harness

Status: DONE 2026-11-04 (ROADMAP-V3-BATCH loop cycle). Evidence: the
code in this folder, 13 Build unit tests (24 tests total with Learn),
and the measured end-to-end run recorded below. Deep is not started.
Spec for this level: BUILD-SPEC.md in this folder.

## What was built

1. An end-to-end RAG pipeline (pipeline.py): BM25 retrieval over a
   12-document local corpus (corpus.json, 36 passages), then an
   extractive answer, the top-ranked passage returned verbatim. The
   pipeline runs with no model, no API, and no credential, so the
   Learn metrics measure retrieval quality directly.
2. A judge layer with cost control (judge.py): any judge callable can
   be wrapped in BudgetedJudge, which enforces a hard max_calls cap,
   deterministic sampling by case id hash, and public accounting in
   cost units (calls made, calls skipped, total cost). The default
   judge is LexicalJudge, a deterministic local proxy. It is not an
   LLM, and nothing here claims it is. This is the cost control
   written up for register item 702: judge spend is a budget line with
   a cap and a sampling rule, never an unbounded loop.
3. Agent protocol scoring (agent_scoring.py): any agent callable that
   takes a task and returns an answer, a step count, and a cost is
   scored for success rate, mean steps, and mean cost per task, with
   failed_task and excess_steps labels. The same pass discipline as
   the RAG cases.

## Run it

```text
python level-2-build/run_build.py
python -m unittest discover -s tests -p "test_build*.py" -v
```

No dependencies. Python 3.12 standard library only.

## Measured results (2026-11-04, Muse VM, Python 3.12.3)

Method: each of the 20 Build golden cases (golden_set_build.json, the
fictional Northlight Library, expanded from the Learn set) asks a
question; the pipeline retrieves the top 5 passages and answers with
the top passage; the Learn scorer grades answer, contexts, gold facts,
and gold answer with the same pass lines as Level 1. A corpus integrity
test asserts every gold fact is covered by the corpus, so every case
is answerable in principle.

Summary: the pipeline passed 19 of 20 cases (pass rate 0.950), with
mean faithfulness 1.000, mean context recall 1.000, and mean answer
relevance 0.970. The one failure is b11-storytime-when: retrieval
found the right document and stayed grounded (faithfulness 1.000,
recall 1.000), but the top passage was the session length sentence,
not the schedule sentence, so relevance scored 0.400 and the case was
labelled wrong_or_incomplete_answer. That is a real ranking defect,
kept in the record, and it is the first Deep level fix target.

Judge pass: BudgetedJudge with max_calls 10, sample_rate 1.0, cost 1
unit per call judged the first 10 cases, skipped 10, total cost 10
units, and all 10 judged cases passed the judge line. The cap held
exactly; skipped cases are counted as not judged, never as passed.

Agent demo: on 4 toy tasks, the careful demo agent scored success
rate 1.000, mean steps 2.0, mean cost 3.0; the sloppy demo agent
scored success rate 0.000, mean steps 8.0, mean cost 9.0, with
failed_task and excess_steps labels. These are toy agents that prove
the protocol, not a real agent. The P07 agent does not exist yet.

## Limits, stated plainly

- The judge is a local lexical proxy, not an LLM judge. The budget
  and sampling machinery is real and tested; the semantic judgment an
  LLM would add is not present, and paraphrase still scores low.
- The corpus and golden set are synthetic and fictional, 20 cases.
  They prove the system end to end, not a production pipeline.
- The answer step is extractive. A generative answer step is Deep
  level scope, where faithfulness stops being 1.000 by construction.
- The run executed on the Muse VM, not the assigned BlackBoxV2 node.

## Next

Level 3, Deep: CI regression tests over this golden set, the full
failure taxonomy with counts from real runs, a quality dashboard, and
the ranking fix for the b11 class of failure (right document, wrong
passage).
