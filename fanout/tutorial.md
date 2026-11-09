# Tutorial: P06 rag-eval-harness, course module

Module: P06-rag-eval-harness
By Jesun Ahmad Ushno
Date: 2026-11-04
License for this tutorial: CC BY 4.0. Code in the repo: Apache-2.0.

## What you will do

You will clone the rag-eval-harness repo, run all three levels, run the
test suite for each level, run the Deep regression gate, and read your
own results against the recorded v1.0 numbers. Every command below
exists in the repo as shipped at v1.0. The harness needs Python 3.12
and uses the standard library only. No model, no API, and no credential
are needed.

All recorded numbers in this module come from synthetic corpora. They
prove the scoring logic, the pipeline, and the reranking mechanism.
They do not prove production quality.

## Step 0: Clone and enter the repo

```text
git clone https://github.com/JesunAhmadUshno/rag-eval-harness.git
cd rag-eval-harness
```

Optional smoke check, before the levels:

```text
python tests/test_smoke.py
```

Expected: a line that says the scaffold smoke test passed.

## Step 1: Level 1, Learn, the three metrics

Read level-1-learn/README.md first. It defines the three metrics
(context recall, faithfulness, answer relevance), the pass lines, and
the failure labels.

Run the golden set:

```text
python level-1-learn/run_eval.py
```

Run the Learn tests:

```text
python -m unittest discover -s tests -p "test_learn*.py" -v
```

Read your results:

- The run prints one line per case and a summary line.
- Expected summary on the shipped set: 5 of 8 passed (pass rate 0.625),
  mean faithfulness 0.953, mean context recall 0.938, mean answer
  relevance 0.808.
- Expected failure labels: hallucination 1, retrieval_miss 1,
  wrong_or_incomplete_answer 1.
- The 0.625 rate is by design. Three cases were built to fail, one per
  failure type, and the harness should name each one correctly.
- Expected tests: 11 tests, all passing.

If your summary differs, check the case lines first. The failing case
id and its label tell you which metric moved.

## Step 2: Level 2, Build, the end-to-end pipeline

Read level-2-build/README.md and level-2-build/BUILD-SPEC.md. The
pipeline retrieves the top 5 passages with BM25 over a 12-document
synthetic corpus and answers with the top passage. The judge layer
enforces a hard call cap.

Run the Build pipeline:

```text
python level-2-build/run_build.py
```

Run the Build tests:

```text
python -m unittest discover -s tests -p "test_build*.py" -v
```

Read your results:

- Expected summary: 19 of 20 passed (pass rate 0.950), mean
  faithfulness 1.000, mean context recall 1.000, mean answer relevance
  0.970.
- Expected one failure: b11-storytime-when, labelled
  wrong_or_incomplete_answer. Retrieval found the right document, but
  the top passage was the session length sentence, not the schedule
  sentence. Keep this case in mind. Deep fixes its class.
- Expected judge line: 10 calls, cap 10, 10 skipped as not judged, 10
  of 10 judged passed. Skipped means not judged, never passed.
- The judge in this level is a local lexical proxy, not an LLM judge.
- Expected tests: 13 Build tests, all passing.
- The agent demo lines at the end score toy demo agents only. They
  prove the scoring protocol, not a real agent.

## Step 3: Level 3, Deep, the reranking fix and the gate

Read level-3-deep/README.md and level-3-deep/DEEP-SPEC.md. This is a
compressed Deep: the reranking fix, the regression gate, the failure
taxonomy, and the quality dashboard. The rest of the v2 Deep scope is
the v1.1 backlog in REPORT.md at the repo root.

Run the Deep set, with and without reranking compared in one run:

```text
python level-3-deep/run_deep.py
```

This run also regenerates level-3-deep/dashboard.md and
level-3-deep/results_deep.json. No number in the dashboard is hand
typed.

Run the Deep tests:

```text
python -m unittest discover -s tests -p "test_deep*.py" -v
```

Run the regression gate on its own:

```text
python level-3-deep/regression_gate.py
```

Read your results:

- Expected without rerank: 23 of 32 passed (pass rate 0.719).
- Expected with rerank: 32 of 32 passed (pass rate 1.000).
- Expected b11 class: 5 of 13 passed without rerank, 13 of 13 with
  rerank.
- Expected judge line on the reranked run: 15 calls, 15 of 15 judged
  passed.
- Expected gate output: pass rate 1.000 (32 of 32), threshold 0.900,
  PASS, and exit code 0. The gate exits non-zero if the pass rate drops
  below the threshold in level-3-deep/baseline.json or a baseline case
  regresses.
- Expected tests: 15 Deep tests, all passing.

## Step 4: Run the full test suite

```text
python -m unittest discover -s tests -v
```

Expected: 39 tests in total (11 Learn, 13 Build, 15 Deep), all passing.

## Step 5: Check your understanding

1. A case has recall 1.000 and faithfulness 1.000, but relevance below
   the line. Which label should the harness give it, and which level
   first showed that pattern? (Answer: wrong_or_incomplete_answer in
   Learn; the Build version of the pattern is b11-storytime-when, and
   Deep names its passage-ranking form wrong_passage_on_top.)
2. The judge skipped 10 cases in Build. Were any of them counted as
   passed? (Answer: no. Skipped means not judged.)
3. The Deep pass rate is 1.000 on 32 synthetic cases. What does that
   prove, and what does it not prove? (Answer: it proves the reranking
   mechanism and the gate on this set. It does not prove production
   quality on a real corpus.)

## Limits to keep with the numbers

- Synthetic corpora only, at every level.
- The judge is a lexical proxy, not an LLM judge.
- The answer step is extractive, so faithfulness at 1.000 is partly by
  construction.
- Agent scoring is proven on toy demo agents only.
