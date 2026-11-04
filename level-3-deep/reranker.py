"""Level 3, Deep: a dependency-free reranker for the b11 failure class.

The b11 failure (Build level, kept in the record): BM25 retrieved the
right document, but a shorter distractor passage from the same document
ranked first. BM25 length normalisation rewards the short passage when
both share the same exact query terms, and exact token matching misses
the one term that separates them when it is inflected (query "run" vs
passage "runs").

This reranker re-scores the top-k BM25 passages by stemmed query
coverage first, then stemmed token F1, then the original BM25 score.
Stemming is a small documented rule set (plural and verb endings), not
a linguistic stemmer. It is enough to let the answering passage win on
the term BM25 could not see, and the Deep golden set proves or
disproves that claim with before and after numbers.
"""

import re

STOPWORDS = frozenset(
    "a an the is are was were be been of to in on for and or as at by "
    "it its this that these those from with without into over under "
    "do does did how what when where who can i you".split()
)
TOKEN_RE = re.compile(r"[a-z0-9]+")


def stem(token):
    """Small rule stemmer. Rules, in order:

    - trailing "ies" becomes "y" (libraries to library), length over 4
    - trailing "sses" drops "es" (classes to class)
    - trailing "ing" drops (speaking to speak, borrowing to borrow),
      length over 5
    - trailing "ed" drops (booked to book, borrowed to borrow),
      length over 4
    - a single trailing "s" drops unless the token ends in "ss"
      (runs to run, opens to open, visitors to visitor)
    Anything else is returned unchanged.
    """
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith("sses"):
        return token[:-2]
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def stemmed_tokens(text):
    raw = [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]
    return [stem(t) for t in raw]


def overlap_scores(query, passage):
    """Return (coverage, f1) of stemmed query tokens in the passage."""
    q = set(stemmed_tokens(query))
    p = set(stemmed_tokens(passage))
    if not q or not p:
        return 0.0, 0.0
    shared = len(q & p)
    coverage = shared / len(q)
    precision = shared / len(p)
    f1 = 2 * precision * coverage / (precision + coverage) if shared else 0.0
    return coverage, f1


def rerank(query, hits):
    """Reorder [(passage_text, bm25_score), ...] by the rerank key.

    Key, descending: stemmed coverage, stemmed F1, BM25 score.
    Ties keep the original BM25 order, so reranking is deterministic.
    Returns a new list of the same (text, bm25_score) pairs.
    """
    decorated = []
    for idx, (text, score) in enumerate(hits):
        coverage, f1 = overlap_scores(query, text)
        decorated.append((text, score, coverage, f1, idx))
    decorated.sort(key=lambda item: (-item[2], -item[3], -item[1], item[4]))
    return [(text, score) for text, score, _, _, _ in decorated]
