"""Level 3 Deep tests: reranker, regression gate, dashboard, taxonomy.
Run: python -m unittest discover -s tests -p "test_deep*.py" -v
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from dashboard import build_dashboard  # noqa: E402
from pipeline import load_corpus  # noqa: E402
from pipeline_deep import DeepRagPipeline, evaluate_cases  # noqa: E402
from rag_eval import context_recall  # noqa: E402
from regression_gate import check_regression, load_baseline  # noqa: E402
from reranker import rerank, stem  # noqa: E402
from taxonomy import build_taxonomy  # noqa: E402


def load_json(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


class TestStemmer(unittest.TestCase):
    def test_inflected_terms_match_base_forms(self):
        pairs = [("runs", "run"), ("opens", "open"), ("classes", "class"),
                 ("visitors", "visitor"), ("speaking", "speak"),
                 ("booked", "book"), ("borrowed", "borrow"),
                 ("gardeners", "gardener"), ("tours", "tour")]
        for inflected, base in pairs:
            self.assertEqual(stem(inflected), base, inflected)


class TestDeepGoldenSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = load_corpus(os.path.join(ROOT, "level-3-deep", "corpus_deep.json"))
        cls.cases = load_json("level-3-deep/golden_set_deep.json")

    def test_at_least_thirty_cases(self):
        self.assertGreaterEqual(len(self.cases), 30)

    def test_multiple_b11_cases(self):
        b11 = [c for c in self.cases if c.get("case_class") == "b11"]
        self.assertGreaterEqual(len(b11), 6)

    def test_build_cases_present_as_regression(self):
        ids = {c["id"] for c in self.cases}
        for i in range(1, 21):
            self.assertTrue(any(cid.startswith(f"b{i:02d}-") for cid in ids), i)

    def test_every_golden_fact_answerable_from_deep_corpus(self):
        all_text = [" ".join(doc["sentences"]) for doc in self.corpus]
        for case in self.cases:
            recall = context_recall(all_text, case["gold_facts"])
            self.assertEqual(recall, 1.0, case["id"])


class TestRerankerFixesB11(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = load_corpus(os.path.join(ROOT, "level-3-deep", "corpus_deep.json"))
        cls.cases = load_json("level-3-deep/golden_set_deep.json")
        cls.without = evaluate_cases(cls.corpus, cls.cases, use_rerank=False)
        cls.with_rerank = evaluate_cases(cls.corpus, cls.cases, use_rerank=True)

    def test_reranker_puts_answering_passage_on_top_for_b11(self):
        case_by_id = {c["id"]: c for c in self.cases}
        results = {r["id"]: r for r in self.with_rerank["results"]}
        for case in self.cases:
            if case.get("case_class") != "b11":
                continue
            top = results[case["id"]]["top_context"]
            recall = context_recall([top], case["gold_facts"])
            self.assertEqual(recall, 1.0, case["id"])
            self.assertTrue(results[case["id"]]["passed"], case["id"])
            self.assertIsNotNone(case_by_id[case["id"]])

    def test_original_b11_case_fixed(self):
        pipe = DeepRagPipeline(self.corpus, use_rerank=True)
        out = pipe.answer("When does story time for children run?")
        self.assertIn("Saturday morning at ten", out["answer"])

    def test_rerank_never_lowers_pass_rate(self):
        self.assertGreaterEqual(self.with_rerank["pass_rate"], self.without["pass_rate"])
        self.assertGreater(self.with_rerank["pass_rate"], self.without["pass_rate"])

    def test_rerank_is_deterministic(self):
        pipe = DeepRagPipeline(self.corpus, use_rerank=True)
        first = pipe.answer("When does the yoga class start for beginners?")
        second = pipe.answer("When does the yoga class start for beginners?")
        self.assertEqual(first, second)

    def test_rerank_returns_same_passages(self):
        hits = [("alpha beta gamma", 3.0), ("beta gamma", 2.0), ("gamma", 1.0)]
        out = rerank("alpha beta", hits)
        self.assertEqual(sorted(out), sorted(hits))


class TestRegressionGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline(
            os.path.join(ROOT, "level-3-deep", "baseline.json"))
        corpus = load_corpus(os.path.join(ROOT, "level-3-deep", "corpus_deep.json"))
        cases = load_json("level-3-deep/golden_set_deep.json")
        cls.current = evaluate_cases(corpus, cases, use_rerank=True)["results"]

    def test_gate_passes_on_current_results(self):
        ok, problems = check_regression(self.current, self.baseline)
        self.assertTrue(ok, problems)

    def test_gate_fails_on_deliberately_regressed_fixture(self):
        regressed = [dict(r) for r in self.current]
        target = self.baseline["passed_ids"][0]
        for r in regressed:
            if r["id"] == target:
                r["passed"] = False
        ok, problems = check_regression(regressed, self.baseline)
        self.assertFalse(ok)
        self.assertTrue(any(target in p for p in problems))

    def test_gate_fails_below_threshold(self):
        baseline = {"threshold": 0.90, "passed_ids": []}
        failing = [{"id": f"x{i}", "passed": i < 5} for i in range(10)]
        ok, problems = check_regression(failing, baseline)
        self.assertFalse(ok)
        self.assertTrue(any("threshold" in p for p in problems))


class TestTaxonomy(unittest.TestCase):
    def test_counts_sum_to_total_failures(self):
        rag_results = [
            {"id": "r1", "passed": False, "faithfulness": 0.5,
             "context_recall": 1.0, "answer_relevance": 0.9},
            {"id": "r2", "passed": False, "faithfulness": 1.0,
             "context_recall": 0.0, "answer_relevance": 0.9},
            {"id": "r3", "passed": False, "faithfulness": 1.0,
             "context_recall": 1.0, "answer_relevance": 0.4},
            {"id": "r4", "passed": True, "faithfulness": 1.0,
             "context_recall": 1.0, "answer_relevance": 1.0},
        ]
        agent_results = [
            {"id": "a1", "relevance": 1.0, "steps": 12, "step_budget": 5,
             "tool_used": "catalog", "expected_tool": "catalog",
             "repeated_actions": True},
            {"id": "a2", "relevance": 0.1, "steps": 2, "step_budget": 5,
             "tool_used": "catalog", "expected_tool": "catalog",
             "repeated_actions": False},
            {"id": "a3", "relevance": 1.0, "steps": 2, "step_budget": 5,
             "tool_used": "catalog", "expected_tool": "catalog",
             "repeated_actions": False},
        ]
        tax = build_taxonomy(rag_results, agent_results)
        self.assertEqual(tax["rag_counts"],
                         {"hallucination": 1, "retrieval_miss": 1,
                          "wrong_passage_on_top": 1})
        self.assertEqual(tax["agent_counts"],
                         {"loop_trap": 1, "silent_wrong_answer": 1})
        total = sum(tax["rag_counts"].values()) + sum(tax["agent_counts"].values())
        self.assertEqual(total, tax["total_labelled"])
        self.assertEqual(tax["total_labelled"], tax["rag_failed"] + tax["agent_failed"])
        self.assertEqual(tax["rag_failed"] + tax["agent_failed"], 5)


class TestDashboard(unittest.TestCase):
    def test_dashboard_generation(self):
        from run_deep import run_all

        summary, _ = run_all()
        text = build_dashboard(summary)
        self.assertIn("Pass rates", text)
        self.assertIn(f"{summary['with']['pass_rate']:.3f}", text)
        self.assertIn("wrong_passage_on_top", text)
        self.assertIn("loop_trap", text)
        with tempfile.NamedTemporaryFile(
                "w", suffix=".md", delete=False) as fh:
            path = fh.name
        try:
            from dashboard import write_dashboard

            write_dashboard(summary, path)
            with open(path, encoding="utf-8") as fh:
                self.assertEqual(fh.read(), build_dashboard(summary))
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
