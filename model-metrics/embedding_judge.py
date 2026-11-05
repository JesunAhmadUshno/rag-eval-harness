"""Model-based metric for the harness: an embedding similarity judge.

v1.0 scored answers with lexical token overlap only. Lexical scores miss
paraphrases: a correct answer in different words scores low. This module
adds a semantic score from a real embedding model, behind the same judge
shape as level-2-build/judge.py: judge(case, answer, contexts) -> dict.

The default embedder is Model2Vec with minishlab/potion-base-8M, a small
static embedding model that runs on CPU with no API key and no cost. The
model name is recorded in every result this judge produces, so a score
can always be traced to the model that made it.

Scores:
- semantic_answer_similarity: cosine similarity between the system
  answer and the gold answer. 1.0 is identical text. Unrelated text
  scores near 0 with this model.
- semantic_support: the highest cosine similarity between the system
  answer and any single retrieved context passage. A grounded answer
  should be close to at least one passage it was built from.
- judge_pass: similarity >= 0.30 and support >= 0.25. The thresholds are
  fixed constants in this file, set below the level a short paraphrase
  reaches with this model and above the level unrelated text reaches.
  They are calibration choices, documented here, not learned parameters.
  The v1.2 agreement check against gold-derived proxy labels is in
  calibrate_judge.py and calibration.json (write-up in this folder's
  README); it checked the constants and left them unchanged.

The embedder is injected, so tests run with a fake embedder and never
download a model. If Model2Vec or the model is unavailable,
Model2VecEmbedder raises ModelUnavailable with the reason, and callers
must record the model run as not run, never as a zero score.
"""

import math

MODEL_NAME = "minishlab/potion-base-8M"
PASS_SIMILARITY = 0.30
PASS_SUPPORT = 0.25


class ModelUnavailable(Exception):
    """The embedding model could not be loaded. Carries the reason."""


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class Model2VecEmbedder:
    """Lazy Model2Vec embedder. Loads the model on first use."""

    def __init__(self, model_name=MODEL_NAME):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from model2vec import StaticModel
            except ImportError as exc:
                raise ModelUnavailable(
                    "model2vec is not installed (pip install model2vec)"
                ) from exc
            try:
                self._model = StaticModel.from_pretrained(self.model_name)
            except Exception as exc:  # download or load failure
                raise ModelUnavailable(
                    f"could not load {self.model_name}: {exc}"
                ) from exc
        return self._model

    def __call__(self, texts):
        model = self._load()
        vectors = model.encode(list(texts))
        return [[float(x) for x in vector] for vector in vectors]


class EmbeddingJudge:
    """Judge that scores with embedding similarity. Embedder injected."""

    def __init__(self, embedder, model_name=MODEL_NAME):
        self.embedder = embedder
        self.model_name = model_name

    def __call__(self, case, answer, contexts):
        gold = case.get("gold_answer", "")
        if not answer or not gold:
            return {
                "semantic_answer_similarity": 0.0,
                "semantic_support": 0.0,
                "judge_pass": False,
                "model": self.model_name,
            }
        texts = [answer, gold] + [c for c in contexts if c]
        vectors = self.embedder(texts)
        answer_vec = vectors[0]
        similarity = cosine(answer_vec, vectors[1])
        support = 0.0
        for context_vec in vectors[2:]:
            support = max(support, cosine(answer_vec, context_vec))
        return {
            "semantic_answer_similarity": round(similarity, 4),
            "semantic_support": round(support, 4),
            "judge_pass": similarity >= PASS_SIMILARITY
            and support >= PASS_SUPPORT,
            "model": self.model_name,
        }
