"""Level 2, Build: an end-to-end RAG pipeline over a local corpus.

Retrieval is BM25 over individual sentences (passages). The answer is
extractive: the top-ranked passage is returned verbatim. That choice is
deliberate at Build level. The answer is grounded in the retrieved
context by construction, so the Learn metrics measure retrieval quality
honestly, and no generative model, API, or credential is needed.

BM25: score = sum over query terms of
  idf(term) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))
with idf = ln(1 + (N - df + 0.5) / (df + 0.5)), k1 = 1.5, b = 0.75.
"""

import json
import math
import os
import re
from collections import Counter

STOPWORDS = frozenset(
    "a an the is are was were be been of to in on for and or as at by "
    "it its this that these those from with without into over under "
    "do does did how what when where who can i you".split()
)
TOKEN_RE = re.compile(r"[a-z0-9]+")
K1 = 1.5
B = 0.75


def content_tokens(text):
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def load_corpus(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


class BM25Index:
    """BM25 over passages. Each passage is (doc_id, sentence)."""

    def __init__(self, corpus):
        self.passages = []
        for doc in corpus:
            for sentence in doc["sentences"]:
                self.passages.append((doc["id"], sentence))
        self.doc_tokens = [content_tokens(text) for _, text in self.passages]
        # Term counts per passage, computed once. _score used to rebuild
        # a Counter for every (query, passage) pair, which made large
        # corpora needlessly slow. The counts are identical either way,
        # so scores do not change; a unit test pins that.
        self.doc_tf = [Counter(tokens) for tokens in self.doc_tokens]
        self.avgdl = (
            sum(len(t) for t in self.doc_tokens) / len(self.doc_tokens)
            if self.doc_tokens
            else 0.0
        )
        df = Counter()
        for tokens in self.doc_tokens:
            for term in set(tokens):
                df[term] += 1
        n = len(self.passages)
        self.idf = {
            term: math.log(1 + (n - count + 0.5) / (count + 0.5))
            for term, count in df.items()
        }

    def _score(self, query_tokens, idx):
        tokens = self.doc_tokens[idx]
        if not tokens:
            return 0.0
        tf = self.doc_tf[idx]
        dl = len(tokens)
        score = 0.0
        for term in set(query_tokens):
            if term not in tf:
                continue
            freq = tf[term]
            denom = freq + K1 * (1 - B + B * dl / self.avgdl)
            score += self.idf.get(term, 0.0) * freq * (K1 + 1) / denom
        return score

    def search_passages(self, query, top_k=5):
        """Return [(passage_text, score), ...] sorted by score desc.

        Ties break on passage order, so results are deterministic.
        """
        query_tokens = content_tokens(query)
        scored = [
            (self._score(query_tokens, i), i) for i in range(len(self.passages))
        ]
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        return [
            (self.passages[i][1], score) for score, i in scored[:top_k] if score > 0
        ]

    def search(self, query, top_k=3):
        """Return [(doc_id, best_passage_score), ...] ranked documents."""
        query_tokens = content_tokens(query)
        best = {}
        for i, (doc_id, _) in enumerate(self.passages):
            score = self._score(query_tokens, i)
            if score > best.get(doc_id, -1.0):
                best[doc_id] = score
        ranked = sorted(best.items(), key=lambda kv: (-kv[1], kv[0]))
        return [(doc_id, s) for doc_id, s in ranked[:top_k] if s > 0]


class RagPipeline:
    def __init__(self, corpus, top_k=5):
        self.index = BM25Index(corpus)
        self.top_k = top_k

    def answer(self, question):
        hits = self.index.search_passages(question, top_k=self.top_k)
        contexts = [text for text, _ in hits]
        return {
            "answer": contexts[0] if contexts else "",
            "contexts": contexts,
            "scores": [score for _, score in hits],
        }


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    pipe = RagPipeline(load_corpus(os.path.join(here, "corpus.json")))
    print(pipe.answer("How long can I borrow a book for?"))
