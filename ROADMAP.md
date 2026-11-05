# ROADMAP: rag-eval-harness v1.1 backlog

v1.0 (2026-11-04) closes Learn, Build, and compressed Deep. Compressed
Deep delivered the single hardest Deep capability (the reranking fix
for the b11 failure class, proven on the expanded Deep golden set),
plus the CI regression gate, the failure taxonomy, and the quality
dashboard. The items below are the rest of the v2 Deep scope, named
here as the v1.1 backlog. None of them is done, and none is claimed.

## v1.1 backlog

1. LLM judge: replace or augment the local LexicalJudge proxy with a
   real LLM judge behind the existing BudgetedJudge interface, with
   the same cap, sampling, and cost accounting, and a measured
   agreement study against human labels. Needs a credential decision
   from Jesun; no credential is created by this project on its own.
2. Generative answer step: a non-extractive answerer, where
   faithfulness stops being 1.000 by construction and the harness
   must catch unsupported claims. The Deep taxonomy already carries
   the hallucination label for this.
3. Real agent evaluation: score the P07 agent-from-scratch agent on
   the Deep task protocol once P07 exists, replacing the five toy
   demo agents used at Deep level to prove the taxonomy.
4. Larger real corpus: move beyond the synthetic Northlight Library
   corpus (24 documents, 32 cases at v1.0) to a larger corpus with
   real documents and a golden set in the hundreds, and re-baseline
   the regression gate from that run.
5. Cross-encoder or learned reranking: compare the stemmed overlap
   reranker against a learned reranker on the same Deep set, with
   the same before and after reporting discipline.
6. Workshop paper submission: the Deep results are the paper track
   named in SPEC.md (MLSys, NeurIPS, or ICLR workshop). The numbers
   are reproducible from this repo at v1.0. Submission itself is
   Jesun's tap and is not part of any automated run.

## v1.1 shipped (2026-11-04, research upgrade)

Done from the backlog above: item 4 in part (real public datasets,
SQuAD and HotpotQA samples, run and reported separately; the
hundreds-scale golden set is still open), and a first step on item 1
(a model judge exists, but it is an embedding judge, not an LLM judge;
the human agreement study is still open). Added in v1.1: the React
results lab on GitHub Pages replacing the single-page docs. Grade
8,000 of 10,000, deductions in DOSSIER.md.

## v1.2 backlog (status at the v1.2 ship, 2026-11-04)

1. Span extraction: DONE in v1.2 (level-3-deep/span_extract.py).
   SQuAD lexical passes 22 to 108 and HotpotQA 1 to 9, reranked runs,
   sentence against span on the same cases and corpora.
2. Generative answer step (was v1.1 item 2), behind the same metrics.
   Still open.
3. Dense retrieval next to BM25 (DPR class), compared on the same
   real samples. Still open; v1.2 names it the binding constraint
   for HotpotQA (context recall 0.518).
4. Learned reranking (was v1.1 item 5). Still open. v1.2 ran the
   transfer test (real-data/rerank_experiment.py): a hybrid BM25
   plus coverage key helped SQuAD and hurt HotpotQA, so no change
   shipped. A learned reranker must beat the shipped reranker on
   both datasets at once, on these samples.
5. LLM judge with a human agreement study (rest of v1.1 item 1).
   Still open; needs Jesun's credential decision. v1.2 did the part
   that needs no credential: an agreement check of the embedding
   judge against gold-derived proxy labels (kappa 0.72 to 0.73 in
   span mode; model-metrics/calibration.json). The human study
   itself is still not done and is not claimed.
6. Larger real samples: DONE in part in v1.2 (SQuAD 500, HotpotQA
   200, same deterministic prefix method; the full validation splits
   remain open).
7. Real agent evaluation (was v1.1 item 3), once P07 exists.
   Still open.
8. Workshop paper submission (was v1.1 item 6): Jesun's tap.

## v1.2 shipped (2026-11-04, Jesun's blanket improvement order 23:52 EST)

Backlog items 1 and 6 (in part) above, plus: a per-case drill down
in the dashboard for the real runs (filterable by dataset, answer
mode, verdict, and failure label); the reranker transfer test with
its negative result recorded, not dressed up; and the judge
calibration check. Tests: 65. Grade and deductions are recorded in
DOSSIER.md at ship time.

## v1.3 backlog

1. Dense retrieval next to BM25, aimed at HotpotQA recall.
2. Generative answer step, behind the same metrics, where
   faithfulness stops being 1.000 by construction.
3. Learned reranking against the v1.2 experiment baselines.
4. A mode-specific judge threshold fitted on labelled data, then
   the human agreement study (needs labels; the LLM judge part
   needs Jesun's credential decision).
5. Full validation splits for the real samples, re-baselined.
6. Span extraction round 2: same-type distractor spans (two team
   names, two dates in one sentence) are the extractor's named
   error class; a verb-argument or entity-type signal is the
   candidate fix.
7. Real agent evaluation, once P07 exists.
8. Workshop paper submission: Jesun's tap.

## Standing rules for v1.1 work

- The regression gate in level-3-deep stays green through every
  change, or the change does not land.
- baseline.json is updated only by a deliberate reviewed run, never
  automatically, and the new numbers are recorded with their date.
- Every new number in a README comes from a run executed in that
  cycle. Nothing is carried forward as if it were freshly measured.
