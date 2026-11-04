# Level 1, Learn: rag-eval-harness

Status: DONE 2026-11-04 (ROADMAP-V3-BATCH loop cycle). Evidence: the code
in this folder, 11 unit tests in tests/test_learn_eval.py, and the measured
golden set run recorded below. Build and Deep are not started.

## The idea in one paragraph

A RAG system can fail in three different places, and each place needs its
own number. Retrieval can miss the facts (the answer never had a chance).
The generator can invent claims the context does not support (a fluent
lie). Or the system can retrieve well and stay grounded, yet still answer
the wrong question. One blended score hides which place broke. This level
builds one small metric per failure place, scores a fixed golden set with
them, and labels every failure so the fix goes to the right place.

## The three metrics (all lexical, all checkable by hand)

Content tokens means lowercase words and numbers with stopwords removed
(the, a, is, and similar). Every metric is a ratio of token sets, so a
reader can verify any score with pen and paper.

1. Context recall: the share of gold facts the retrieved context covers.
   A fact is covered when at least 80 percent of its content tokens appear
   in the context. Low recall means retrieval_miss: fix retrieval.
2. Faithfulness: the share of answer content tokens that appear in the
   context. Low faithfulness means hallucination: the answer said things
   its evidence does not support.
3. Answer relevance: the token F1 between the answer and the gold answer.
   Low relevance with good recall and faithfulness means
   wrong_or_incomplete_answer: grounded, retrieved, and still wrong.

A case passes when faithfulness is at least 0.80, context recall is at
least 0.80, and answer relevance is at least 0.50.

## Run it

```text
python level-1-learn/run_eval.py
python -m unittest discover -s tests -p "test_learn*.py" -v
```

No dependencies. Python 3.12 standard library only.

## Measured results (2026-11-04, Muse VM, Python 3.12.3)

The golden set (golden_set.json) holds 8 synthetic cases about a fictional
library, hand-built so each failure type appears once. Synthetic by
design: the point at Learn level is that every expected score can be
checked by hand, and the tests assert exactly those hand-computed values.

| Case | Faithfulness | Recall | Relevance | Verdict |
| --- | --- | --- | --- | --- |
| g01-hours | 1.000 | 1.000 | 1.000 | PASS |
| g02-printing | 1.000 | 1.000 | 1.000 | PASS |
| g03-room-hallucination | 0.625 | 1.000 | 0.714 | FAIL hallucination |
| g04-membership-retrieval-miss | 1.000 | 0.500 | 0.750 | FAIL retrieval_miss |
| g05-loan-wrong-answer | 1.000 | 1.000 | 0.000 | FAIL wrong_or_incomplete_answer |
| g06-story-time | 1.000 | 1.000 | 1.000 | PASS |
| g07-wifi | 1.000 | 1.000 | 1.000 | PASS |
| g08-renewal | 1.000 | 1.000 | 1.000 | PASS |

Summary: 5 of 8 passed (pass rate 0.625). Mean faithfulness 0.953, mean
context recall 0.938, mean answer relevance 0.808. Failure label counts:
hallucination 1, retrieval_miss 1, wrong_or_incomplete_answer 1.

Read the numbers honestly: a 0.625 pass rate on a designed teaching set
is the harness working, not the system failing. Three cases were built
to fail, and the harness named each failure correctly.

## Limits, stated plainly

- Lexical metrics miss paraphrase. A correct answer in different words
  scores low on relevance and can score low on faithfulness. The LLM
  judge that handles meaning is Build level work in SPEC.md, next to
  human labels.
- The golden set is 8 synthetic cases. It proves the scoring logic, not
  a real pipeline. Real question sets arrive at Build level.
- The agent scoring track in SPEC.md (score an agent on success rate,
  steps, and cost per task) waits for the P07 agent to exist, as SPEC.md
  itself states. Nothing about agents is claimed at this level.

## Next

Level 2, Build: run the harness end to end on a real RAG pipeline, add
the LLM judge beside these lexical metrics with a stated judge budget,
and grow the golden set from real questions.
