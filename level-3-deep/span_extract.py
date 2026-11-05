"""Level 3, Deep (v1.2): answer-span extraction from the top passage.

The Build and v1.0 Deep pipelines answer with the whole top sentence.
On real data that is the weak half (real-data/README.md, v1.1): gold
answers in SQuAD and HotpotQA are short spans, and token F1 against a
short span punishes a correct sentence. This module extracts the short
span from the top sentence, with no model and no dependency, so the
same scoring can measure the answer step fairly.

Method, stated plainly so it can be checked and argued with:
- Candidate spans are every contiguous token window of length 1 to 8
  in the top sentence that starts and ends on a content token.
- Each candidate is scored by these signals:
  1. Novelty: the share of its content tokens whose stems do not
     appear in the question. An answer adds information; a span that
     only repeats the question is usually the wrong span.
  2. Question type: a when question boosts spans holding a digit, a
     month, or a number word; how many and how much boost numeric
     spans; who and where boost capitalised spans.
  3. Anchoring: a bonus when a question content stem sits within four
     tokens of the span, because answers live near the terms they
     answer, inside the same sentence.
  4. Subject prior: a small bonus that decays with the span's
     position when the span starts on a span-like token (capitalised,
     numeric, or a month), plus a first mention bonus for a window
     made only of span-like tokens that starts on the sentence's
     first capitalised content token. Subjects and first mentions
     carry a large share of extractive answers.
  5. A small bonus for 2 to 4 token windows whose content tokens are
     all span-like, and a length penalty for every token past two,
     because gold spans in these datasets are short and a long window
     must earn each extra token.
- The best scoring window wins. Ties break on the shorter window,
  then the earlier position, so extraction is deterministic.

Known limits, named in advance: yes or no answers (some HotpotQA
golds) cannot be extracted from a sentence and still score zero; when
a sentence holds two spans of the same type (two team names, two
dates), the heuristics can pick the wrong one; a span can only be as
right as the sentence it is cut from, so retrieval misses stay
retrieval misses; and the type signals are English heuristics.
"""

import re

from reranker import STOPWORDS, stem

TOKEN_RE = re.compile(r"\$?[A-Za-z0-9]+(?:[.,'\u2019/-][A-Za-z0-9]+)*%?")

MONTHS = frozenset(
    "january february march april may june july august september "
    "october november december jan feb mar apr jun jul aug sep sept "
    "oct nov dec".split()
)
NUMBER_WORDS = frozenset(
    "one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen "
    "twenty thirty forty fifty sixty seventy eighty ninety hundred "
    "thousand million billion trillion first second third fourth "
    "fifth sixth seventh eighth ninth tenth".split()
)
MAX_SPAN_TOKENS = 8
ANCHOR_DISTANCE = 4
ANCHOR_NEAR = 0.2
ANCHOR_FAR = 0.05
POSITION_WEIGHT = 0.2
FIRST_MENTION_BONUS = 0.15
SPANLIKE_BONUS = 0.05
LENGTH_PENALTY = 0.12


def _tokens(sentence):
    """Return [(text, lower, start, end)] for each token in the sentence."""
    return [
        (m.group(0), m.group(0).lower(), m.start(), m.end())
        for m in TOKEN_RE.finditer(sentence)
    ]


def _question_type(question):
    q = " " + question.lower() + " "
    if " when " in q or "what year" in q or "in what year" in q:
        return "when"
    if "how many" in q or "how much" in q:
        return "how_many"
    if q.strip().startswith("who") or " who " in q:
        return "who"
    if q.strip().startswith("where"):
        return "where"
    return "other"


def _is_numeric(lower):
    return any(ch.isdigit() for ch in lower) or lower in NUMBER_WORDS


def _is_date_like(lower):
    return (
        any(ch.isdigit() for ch in lower)
        or lower in MONTHS
        or lower in NUMBER_WORDS
    )


def _is_span_like(text, lower):
    """Capitalised, numeric, or a month: the shapes gold spans take."""
    return text[:1].isupper() or _is_numeric(lower) or lower in MONTHS


def _score_window(window, start, q_stems, qtype, sentence_stems, first_cap_pos):
    """Score one candidate window. window is a list of token tuples."""
    content = [
        (text, lower)
        for text, lower, _, _ in window
        if lower not in STOPWORDS
    ]
    if not content:
        return None
    novel = sum(1 for _, lower in content if stem(lower) not in q_stems)
    score = novel / len(content)
    if qtype == "when":
        if any(_is_date_like(lower) for _, lower in content):
            score += 0.9
    elif qtype == "how_many":
        if any(_is_numeric(lower) for _, lower in content):
            score += 0.9
    elif qtype in ("who", "where"):
        cap_share = sum(1 for text, _ in content if text[:1].isupper())
        score += 0.5 * cap_share / len(content)
    # Anchoring: distance from the window to the nearest question stem
    # elsewhere in the sentence.
    window_positions = set(range(start, start + len(window)))
    nearest = None
    for pos, s in enumerate(sentence_stems):
        if pos in window_positions:
            continue
        if s in q_stems:
            dist = min(abs(pos - p) for p in window_positions)
            nearest = dist if nearest is None else min(nearest, dist)
    if nearest is not None and nearest <= ANCHOR_DISTANCE:
        score += ANCHOR_NEAR
    elif nearest is not None:
        score += ANCHOR_FAR
    # Subject prior, only for windows that start on a span-like token,
    # so an early verb is not mistaken for a subject.
    first_text, first_lower = window[0][0], window[0][1]
    if _is_span_like(first_text, first_lower):
        n_tokens = len(sentence_stems)
        score += POSITION_WEIGHT * (1 - start / max(1, n_tokens))
        if start == first_cap_pos and all(
            _is_span_like(text, lower) for text, lower, _, _ in window
        ):
            score += FIRST_MENTION_BONUS
    if 2 <= len(window) <= 4 and all(
        _is_span_like(text, lower) for text, lower in content
    ):
        score += SPANLIKE_BONUS
    score -= LENGTH_PENALTY * max(0, len(window) - 2)
    return score


def extract_span(question, sentence):
    """Return the best answer span inside sentence, or sentence itself.

    Falls back to the unchanged sentence when the sentence is empty or
    holds no content token, so the caller always gets an answer string.
    """
    if not sentence:
        return ""
    tokens = _tokens(sentence)
    if not tokens:
        return sentence
    q_stems = {stem(t) for t in re.findall(r"[a-z0-9]+", question.lower())}
    q_stems -= {stem(w) for w in STOPWORDS}
    qtype = _question_type(question)
    sentence_stems = [stem(lower) for _, lower, _, _ in tokens]
    first_cap_pos = next(
        (
            i
            for i, (text, lower, _, _) in enumerate(tokens)
            if lower not in STOPWORDS and text[:1].isupper()
        ),
        None,
    )
    best = None  # ((score, -length, -start), char_start, char_end)
    n = len(tokens)
    for start in range(n):
        if tokens[start][1] in STOPWORDS:
            continue
        for length in range(1, MAX_SPAN_TOKENS + 1):
            end = start + length
            if end > n:
                break
            if tokens[end - 1][1] in STOPWORDS:
                continue
            window = tokens[start:end]
            score = _score_window(
                window, start, q_stems, qtype, sentence_stems, first_cap_pos
            )
            if score is None:
                continue
            key = (score, -length, -start)
            if best is None or key > best[0]:
                best = (key, tokens[start][2], tokens[end - 1][3])
    if best is None:
        return sentence
    return sentence[best[1] : best[2]]
