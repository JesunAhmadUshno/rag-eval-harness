"""Level 2, Build: the judge layer, with cost control (register 702).

A judge is any callable judge(case, answer, contexts) -> dict or None.
LexicalJudge is the deterministic local proxy: it scores with the same
token definitions as Learn level and costs nothing. It is NOT an LLM,
and no file in this project claims it is. A real LLM judge plugs into
the same interface later.

BudgetedJudge wraps any judge with the cost control:
- max_calls: a hard cap. The cap is never exceeded, for any input.
- sample_rate: deterministic sampling. A case is sampled when the
  first byte of sha256(case id) divided by 256 is below sample_rate.
  Same ids, same sample, every run, on every machine.
- cost_per_call: abstract cost units charged per judge call.
Accounting is public: calls_made, calls_skipped, total_cost, and the
sampled ids are attributes a caller can record next to the results.
When a case is not judged (not sampled, or budget spent), its verdict
is None, and summaries must count it as not judged, never as passed.
"""

import hashlib


class LexicalJudge:
    """Deterministic local judge proxy. Stdlib only, zero cost."""

    def __call__(self, case, answer, contexts):
        import os
        import sys

        sys.path.insert(
            0,
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "level-1-learn"
            ),
        )
        from rag_eval import answer_relevance, faithfulness

        faith = faithfulness(answer, contexts)
        rel = answer_relevance(answer, case.get("gold_answer", ""))
        return {
            "faithfulness": round(faith, 3),
            "answer_relevance": round(rel, 3),
            "judge_pass": faith >= 0.80 and rel >= 0.50,
        }


class BudgetedJudge:
    def __init__(self, judge, max_calls, sample_rate=1.0, cost_per_call=1):
        if max_calls < 0:
            raise ValueError("max_calls must be at least 0")
        if not 0.0 <= sample_rate <= 1.0:
            raise ValueError("sample_rate must be between 0 and 1")
        self.judge = judge
        self.max_calls = max_calls
        self.sample_rate = sample_rate
        self.cost_per_call = cost_per_call
        self.calls_made = 0
        self.calls_skipped = 0
        self.total_cost = 0
        self.sampled_ids = []

    def _sampled(self, case_id):
        digest = hashlib.sha256(case_id.encode("utf-8")).digest()
        return digest[0] / 256 < self.sample_rate

    def judge_all(self, cases, answers, contexts_list):
        """Judge a batch. Returns one verdict or None per case."""
        verdicts = []
        for case, answer, contexts in zip(cases, answers, contexts_list):
            if not self._sampled(case["id"]):
                self.calls_skipped += 1
                verdicts.append(None)
                continue
            self.sampled_ids.append(case["id"])
            if self.calls_made >= self.max_calls:
                self.calls_skipped += 1
                verdicts.append(None)
                continue
            verdict = self.judge(case, answer, contexts)
            self.calls_made += 1
            self.total_cost += self.cost_per_call
            verdicts.append(verdict)
        return verdicts
