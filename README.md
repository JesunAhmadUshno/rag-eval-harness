# rag-eval-harness

**Question.** Can a small, transparent, standard-library harness measure
RAG quality honestly, and does a targeted fix for one failure class
(right document, wrong passage on top) hold up outside the data it was
built on?

**Headline.** The stemmed reranker that took the synthetic Deep set from 23 to 32 of 32 did not transfer to real data: on 500 SQuAD questions the gold answer reached the top passage in 315 cases without it (Wilson 95% 0.587 to 0.671) and 319 with it (0.595 to 0.679), 26 helped against 22 hurt (exact sign test p 0.67), while span answers were the one significant gain (SQuAD lexical passes 24 to 113 of 500, McNemar p < 0.0001).

**Field.** ML and AI research (evaluation). **Job family.** ML and AI
evaluation engineering. This project judges a RAG system; P05 builds
one.

**Verdict.** Functional, not pre-registered. Tests pass in CI on Python
3.11 and 3.12, every scored result regenerates from the committed
evidence by one command, and the pipeline has run end to end on 700
real questions. No plan was locked before the results, so the
hypotheses in REPORT.md are post hoc and the repo is capped at
Functional; a confirmatory cycle under a newly locked PROPOSAL.md is
planned.

Live dashboard: https://jesunahmadushno.github.io/rag-eval-harness/

## Reproduce

```text
python -m unittest discover -s tests -p "test_*.py" -v
sh reproduce.sh
```

reproduce.sh reruns the Deep set, the regression gate, the ablation,
the reranker transfer test, the paired statistics and the judge
calibration from the committed evidence, then fails if any result file
changed by one byte. Python 3 standard library only, a few seconds on
CPU. The real-data runs themselves (real-data/run_real_eval.py) also
need `pip install model2vec` and a one-time model download; their
recorded output, real-data/results_real.json, is the evidence the rest
is computed from.

Evidence honesty: the origin claim (a private pipeline that went from a
72.7 percent pass rate to 95 percent or more) is self-reported and has
no evidence in this repo; see REPORT.md.

## Lifecycle

- Question: DONE 2026-11-04
- Proposal: OPEN
- Baseline: DONE 2026-11-04
- Build: DONE 2026-11-05
- Evaluate: PARTIAL 2026-11-07
- Report: PARTIAL 2026-11-08
- Review: OPEN
- Release: OPEN

Evaluate and Report are partial because they ran without a locked plan
and the ML profile's dense-retrieval baseline is missing. Tags v0.1 to
v1.2 are releases under the earlier scheme, not a v1.0 Released verdict
under this standard.

## Layout

| Path | What it holds |
| --- | --- |
| PROPOSAL.md | Question, system, prior work, post hoc hypotheses, candidates for the confirmatory cycle, original scope (draft, not locked) |
| REPORT.md | Background, method, hypotheses scored, every measured run, misses, threats, novelty, research review, history and roadmap |
| CHANGELOG.md | Releases v0.1 to v1.2 and this migration |
| level-1-learn/ | Lexical evaluator (faithfulness, context recall, answer relevance) and its 8-case golden set |
| level-2-build/ | BM25 pipeline, budgeted judge, agent protocol scoring, 20-case set |
| level-3-deep/ | Reranker, span extractor, taxonomy, regression gate, ablation; results_deep.json, results_ablation.json, baseline.json |
| real-data/ | SQuAD and HotpotQA samples (evidence), runners, transfer test, paired statistics; results_*.json |
| model-metrics/ | Embedding judge and its calibration (calibration.json) |
| reproduce.sh | Regenerates every scored result and fails on drift (run in CI) |
| tests/ | Unit tests, the layout check and the no-public-grade check |
| docs/decisions/ | Records of hard-to-reverse choices |
| docs/index.md | The superseded v1.0 docs page, kept as a record |
| site/ | The live dashboard, built from the result files |
| web/ | The earlier results lab, kept as source |
| fanout/ | Drafted posts, tutorial, paper brief, release notes, publicity log |

There is no experiments/ or results/ folder: each result file sits
beside the script that writes it, and the dashboard, the CI checks and
the level READMEs read them there (docs/decisions/0003).

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
