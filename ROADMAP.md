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

## Standing rules for v1.1 work

- The regression gate in level-3-deep stays green through every
  change, or the change does not land.
- baseline.json is updated only by a deliberate reviewed run, never
  automatically, and the new numbers are recorded with their date.
- Every new number in a README comes from a run executed in that
  cycle. Nothing is carried forward as if it were freshly measured.
