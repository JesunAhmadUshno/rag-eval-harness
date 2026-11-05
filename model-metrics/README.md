# Model metrics (v1.1)

The model inside the evaluation path. embedding_judge.py adds a
semantic score to the harness: an EmbeddingJudge that compares the
system answer with the gold answer and with the retrieved passages
using cosine similarity over embeddings from a real model,
minishlab/potion-base-8M through Model2Vec. The model runs on CPU,
needs no API key, and costs nothing. Its name is written into every
verdict it produces.

Why it exists: the Level 1 lexical metrics cannot see paraphrase. On
the real SQuAD sample the lexical pass rate is 1 of 100 while the
embedding judge passes 49 of 100, because the pipeline answers in full
sentences and the gold answers are short spans. Neither number alone is
the truth; the pair shows both the wording gap and the semantic gap.
The full analysis is in real-data/README.md.

Use:

    pip install model2vec
    python real-data/run_real_eval.py

Without model2vec installed, the lexical run still completes and the
model section of results_real.json records status not_run with the
reason. A missing model is never reported as a zero score.

Tests (tests/test_model_judge.py) inject a fake embedder, so CI never
downloads a model. Thresholds are fixed constants in embedding_judge.py
with their calibration stated in the module docstring.
