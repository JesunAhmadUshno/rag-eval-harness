# Model metrics (v1.1, calibration checked in v1.2)

The model inside the evaluation path. embedding_judge.py adds a
semantic score to the harness: an EmbeddingJudge that compares the
system answer with the gold answer and with the retrieved passages
using cosine similarity over embeddings from a real model,
minishlab/potion-base-8M through Model2Vec. The model runs on CPU,
needs no API key, and costs nothing. Its name is written into every
verdict it produces.

Why it exists: the Level 1 lexical metrics cannot see paraphrase. On
the v1.1 real SQuAD sample the lexical pass rate was 1 of 100 while
the embedding judge passed 49 of 100, because the pipeline answered in
full sentences and the gold answers are short spans. In v1.2 span mode
the two judges nearly agree in count (112 judge passes against 108
lexical passes on the 500-case SQuAD sample), for the opposite reason:
a short span's static embedding is a weaker signal than a sentence's.
Neither number alone is the truth; the pair shows both the wording
gap and the semantic gap. The full analysis is in
real-data/README.md.

Use:

    pip install model2vec
    python real-data/run_real_eval.py

Without model2vec installed, the lexical run still completes and the
model section of results_real.json records status not_run with the
reason. A missing model is never reported as a zero score.

Tests (tests/test_model_judge.py) inject a fake embedder, so CI never
downloads a model.

## How the thresholds were chosen

The judge passes a case at semantic similarity 0.30 or more and
semantic support 0.25 or more (PASS_SIMILARITY and PASS_SUPPORT in
embedding_judge.py). Provenance, stated honestly: they are fixed
calibration constants chosen by hand in v1.1, set below the level a
short paraphrase reaches with this model and above the level
unrelated text reaches (a paraphrase scored 0.415 against an
unrelated pair at 0.055 in the v1.1 verification run). They were not
fitted on labelled data in v1.1. v1.2 checked them, below; it did not
refit them.

## Calibration check (v1.2, calibrate_judge.py)

Method: a proxy correctness label built from the gold data already in
the repo (the gold answer text appears inside the system answer, or
lexical answer relevance is at least 0.50). A proxy is not a human
label, and the human agreement study remains open (ROADMAP backlog;
it needs labelled judgements this project does not have). Agreement
between the judge verdict and the proxy, on the v1.2 real runs:

| Dataset and variant | Proxy-correct | Agreement | Cohen's kappa | Judge vs lexical agreement |
| --- | --- | --- | --- | --- |
| SQuAD, sentence, rerank | 320 of 500 | 0.790 | 0.56 | 0.482 |
| SQuAD, span, rerank | 109 of 500 | 0.902 | 0.72 | 0.900 |
| HotpotQA, sentence, rerank | 48 of 200 | 0.820 | 0.57 | 0.655 |
| HotpotQA, span, rerank | 26 of 200 | 0.925 | 0.73 | 0.840 |

Readings: agreement is moderate in sentence mode (kappa 0.56 to 0.57)
and substantial in span mode (kappa 0.72 to 0.73). The threshold sweep
(similarity 0.20 to 0.40, support held at 0.25, full table in
calibration.json) pulls in opposite directions per mode: sentence
mode agreement peaks at lower thresholds (0.850 at 0.20 on SQuAD),
span mode at higher ones (0.922 at 0.40 on SQuAD). No single
threshold is best for both modes, so the shipped constants stay for
v1.2 and the sweep is recorded as the evidence. A mode-specific
threshold, fitted on labelled data, is the honest next step and is
named as such in REPORT.md.
