"""Tests for v1.2 span extraction and the span answer mode.

The extractor is a documented heuristic (level-3-deep/span_extract.py).
These tests pin the behaviour classes it was built for: entity, date,
and numeric answers; the fallback paths; determinism; and the rule
that a span is always a substring of the sentence it was cut from.
"""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))

from pipeline_deep import DeepRagPipeline  # noqa: E402
from span_extract import extract_span  # noqa: E402


class TestExtractSpan(unittest.TestCase):
    def test_entity_answer_beats_same_type_distractor(self):
        span = extract_span(
            "What team won Super Bowl 50?",
            "The Denver Broncos defeated the Carolina Panthers "
            "in Super Bowl 50.",
        )
        self.assertEqual(span, "Denver Broncos")

    def test_date_answer_for_when_question(self):
        span = extract_span(
            "When was the treaty signed?",
            "The treaty was signed in Paris in 1919 after long negotiations.",
        )
        self.assertEqual(span, "1919")

    def test_numeric_answer_for_how_many_question(self):
        span = extract_span(
            "How many visitors came in 2019?",
            "The museum welcomed 250,000 visitors in 2019 alone.",
        )
        self.assertEqual(span, "250,000")

    def test_person_answer_for_who_question(self):
        span = extract_span(
            "Who wrote the novel Frankenstein?",
            "The novel was written by Mary Shelley in 1818.",
        )
        self.assertEqual(span, "Mary Shelley")

    def test_place_answer_for_where_question(self):
        span = extract_span(
            "Where is the Amazon rainforest located?",
            "The Amazon rainforest covers much of South America.",
        )
        self.assertEqual(span, "South America")

    def test_span_is_always_a_substring(self):
        sentence = (
            "The city of Denver, Colorado hosted the 1976 convention "
            "at the fairgrounds."
        )
        span = extract_span("Where was the 1976 convention hosted?", sentence)
        self.assertIn(span, sentence)
        self.assertLess(len(span), len(sentence))

    def test_empty_sentence_returns_empty(self):
        self.assertEqual(extract_span("Anything?", ""), "")

    def test_stopword_only_sentence_falls_back_unchanged(self):
        sentence = "It is what it is."
        self.assertEqual(extract_span("What is it?", sentence), sentence)

    def test_deterministic(self):
        question = "When did the war end?"
        sentence = "World War II ended in 1945 in Europe."
        self.assertEqual(
            extract_span(question, sentence), extract_span(question, sentence)
        )


class TestSpanAnswerMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(
            os.path.join(ROOT, "level-2-build", "corpus.json"), encoding="utf-8"
        ) as fh:
            cls.corpus = json.load(fh)

    def test_span_answer_is_shorter_than_sentence_answer(self):
        question = "How long can I borrow a book for?"
        sentence_pipe = DeepRagPipeline(
            self.corpus, use_rerank=True, answer_mode="sentence"
        )
        span_pipe = DeepRagPipeline(
            self.corpus, use_rerank=True, answer_mode="span"
        )
        sentence_out = sentence_pipe.answer(question)
        span_out = span_pipe.answer(question)
        self.assertEqual(span_out["contexts"], sentence_out["contexts"])
        self.assertIn(span_out["answer"], span_out["source_sentence"])
        self.assertLess(len(span_out["answer"]), len(sentence_out["answer"]))

    def test_sentence_mode_is_the_default(self):
        pipe = DeepRagPipeline(self.corpus)
        self.assertEqual(pipe.answer_mode, "sentence")

    def test_unknown_mode_rejected(self):
        with self.assertRaises(ValueError):
            DeepRagPipeline(self.corpus, answer_mode="paragraph")


if __name__ == "__main__":
    unittest.main()
