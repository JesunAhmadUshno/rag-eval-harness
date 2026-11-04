"""Level 2 Build tests: pipeline, judge budget, agent protocol.
Expected values are computed from the fixtures by hand or by the
definitions in BUILD-SPEC.md. Run:
python -m unittest discover -s tests -p "test_build*.py" -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from pipeline import BM25Index, RagPipeline, load_corpus  # noqa: E402
from judge import BudgetedJudge, LexicalJudge  # noqa: E402
from agent_scoring import score_agent  # noqa: E402
from rag_eval import context_recall  # noqa: E402


def load_json(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


class TestCorpusIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = load_corpus(os.path.join(ROOT, "level-2-build", "corpus.json"))
        cls.cases = load_json("level-2-build/golden_set_build.json")

    def test_corpus_has_twelve_documents(self):
        self.assertEqual(len(self.corpus), 12)

    def test_golden_has_twenty_cases(self):
        self.assertEqual(len(self.cases), 20)

    def test_every_golden_fact_is_answerable_from_corpus(self):
        all_text = [" ".join(doc["sentences"]) for doc in self.corpus]
        for case in self.cases:
            recall = context_recall(all_text, case["gold_facts"])
            self.assertEqual(recall, 1.0, case["id"])


class TestRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = load_corpus(os.path.join(ROOT, "level-2-build", "corpus.json"))
        cls.index = BM25Index(corpus)

    def test_wifi_query_ranks_wifi_document_first(self):
        hits = self.index.search("How do I connect to the library wifi network?", top_k=3)
        self.assertEqual(hits[0][0], "wifi")

    def test_loan_query_ranks_loans_document_first(self):
        hits = self.index.search("How long can I borrow a book for?", top_k=3)
        self.assertEqual(hits[0][0], "loans")

    def test_scores_are_descending(self):
        hits = self.index.search("library opening hours weekdays", top_k=5)
        scores = [s for _, s in hits]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestPipelineEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = load_corpus(os.path.join(ROOT, "level-2-build", "corpus.json"))
        cls.pipe = RagPipeline(corpus)
        cls.cases = load_json("level-2-build/golden_set_build.json")

    def test_answer_is_grounded_in_retrieved_context(self):
        out = self.pipe.answer("What time does the library open on weekdays?")
        self.assertTrue(out["contexts"])
        self.assertIn(out["answer"], out["contexts"])

    def test_end_to_end_pass_rate_at_least_three_quarters(self):
        from run_build import evaluate_pipeline

        summary = evaluate_pipeline(self.pipe, self.cases)
        self.assertGreaterEqual(summary["pass_rate"], 0.75)
        self.assertEqual(summary["n"], 20)


class TestJudgeBudget(unittest.TestCase):
    def setUp(self):
        self.cases = [{"id": f"c{i:02d}"} for i in range(10)]

    def test_budget_never_exceeded(self):
        judge = BudgetedJudge(LexicalJudge(), max_calls=3, sample_rate=1.0, cost_per_call=2)
        verdicts = judge.judge_all(self.cases, ["answer"] * 10, [["ctx"]] * 10)
        self.assertEqual(judge.calls_made, 3)
        self.assertEqual(judge.total_cost, 6)
        self.assertEqual(len([v for v in verdicts if v is not None]), 3)

    def test_sampling_is_deterministic(self):
        first = BudgetedJudge(LexicalJudge(), max_calls=100, sample_rate=0.5, cost_per_call=1)
        second = BudgetedJudge(LexicalJudge(), max_calls=100, sample_rate=0.5, cost_per_call=1)
        first.judge_all(self.cases, ["a"] * 10, [["c"]] * 10)
        second.judge_all(self.cases, ["a"] * 10, [["c"]] * 10)
        self.assertEqual(first.sampled_ids, second.sampled_ids)
        self.assertLess(first.calls_made, 10)

    def test_zero_budget_judges_nothing(self):
        judge = BudgetedJudge(LexicalJudge(), max_calls=0, sample_rate=1.0, cost_per_call=1)
        verdicts = judge.judge_all(self.cases, ["a"] * 10, [["c"]] * 10)
        self.assertTrue(all(v is None for v in verdicts))
        self.assertEqual(judge.total_cost, 0)


class TestAgentScoring(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            {"id": "t1", "prompt": "hours", "gold_answer": "opens at 8 am", "step_budget": 5},
            {"id": "t2", "prompt": "wifi", "gold_answer": "northlight guest network", "step_budget": 5},
        ]

    def test_perfect_agent_scores(self):
        answers = {"hours": "opens at 8 am", "wifi": "northlight guest network"}

        def agent(task):
            return {"answer": answers[task["prompt"]], "steps": 2, "cost_units": 3}

        summary = score_agent(agent, self.tasks)
        self.assertEqual(summary["success_rate"], 1.0)
        self.assertEqual(summary["mean_steps"], 2.0)
        self.assertEqual(summary["mean_cost"], 3.0)

    def test_failing_agent_gets_labels(self):
        def agent(task):
            return {"answer": "no idea at all", "steps": 9, "cost_units": 1}

        summary = score_agent(agent, self.tasks)
        self.assertEqual(summary["success_rate"], 0.0)
        labels = summary["results"][0]["labels"]
        self.assertIn("failed_task", labels)
        self.assertIn("excess_steps", labels)


if __name__ == "__main__":
    unittest.main()
