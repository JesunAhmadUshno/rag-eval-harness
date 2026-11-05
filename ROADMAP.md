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

## v1.2 backlog

1. Span extraction: answer with the short span instead of the whole
   sentence. The real-data runs name this as the weak half (lexical
   pass 1 of 100 on SQuAD while the embedding judge passes 49 of 100).
2. Generative answer step (was v1.1 item 2), behind the same metrics.
3. Dense retrieval next to BM25 (DPR class), compared on the same
   real samples.
4. Learned reranking (was v1.1 item 5). The stemmed-overlap reranker
   does not transfer to real data; a learned one must prove itself on
   the real samples, not only on the synthetic Deep set.
5. LLM judge with a human agreement study (rest of v1.1 item 1).
   Needs Jesun's credential decision.
6. Larger real samples: raise the SQuAD and HotpotQA samples toward
   the full validation splits and re-baseline.
7. Real agent evaluation (was v1.1 item 3), once P07 exists.
8. Workshop paper submission (was v1.1 item 6): Jesun's tap.

## Standing rules for v1.1 work

- The regression gate in level-3-deep stays green through every
  change, or the change does not land.
- baseline.json is updated only by a deliberate reviewed run, never
  automatically, and the new numbers are recorded with their date.
- Every new number in a README comes from a run executed in that
  cycle. Nothing is carried forward as if it were freshly measured.
