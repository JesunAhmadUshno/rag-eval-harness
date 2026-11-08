# Changelog

All notable changes to this project. Format: Keep a Changelog 1.1.
Versions follow Semantic Versioning from the next release; tags v0.1 to
v1.2 were cut under the earlier Learn / Build / Deep scheme.

## [Unreleased]

### Changed
- 2026-11-08: Adopted the portfolio standard v2. README opens with the
  question, headline, field, job family and verdict (Functional, not
  pre-registered). SPEC.md became PROPOSAL.md (draft, not locked);
  DOSSIER.md, NOVELTY.md, ROADMAP.md and docs/research-review.md were
  folded into REPORT.md; PUBLICITY.md moved to fanout/. Grades and
  rubric scores left the public repo (grades are internal). The old
  README's benchmark, statistics, dashboard and fan-out sections moved
  to REPORT.md.

### Added
- 2026-11-08: reproduce.sh regenerates every scored result from the
  committed evidence and fails on drift; CI runs it on Python 3.11 and
  3.12 with read-only permissions. tests/test_layout.py checks the
  required files and that no public file carries a grade. CodeQL now
  covers the dashboard's JavaScript; Dependabot watches site/ npm.
  CITATION.cff, SECURITY.md, docs/decisions/0001 to 0003.

## [1.2] - 2026-11-05

### Added
- Wilson intervals, exact McNemar and sign tests, a 2-D judge threshold
  sweep (real-data/paired_stats.py), and a reranker ablation
  (level-3-deep/ablation.py), both checked for drift in CI (2026-11-07).
- The site/ live dashboard with browser ports checked against the
  Python results at build time (2026-11-07).
- Span extraction behind answer_mode="span"; real samples raised to 500
  SQuAD and 200 HotpotQA cases; the reranker transfer test, negative
  result recorded; judge calibration against a gold-derived proxy; a
  per-case drill down on the dashboard.

## [1.1] - 2026-11-05

### Added
- SQuAD (100) and HotpotQA (60) samples, CC BY-SA 4.0, run separately
  from the synthetic sets; the Model2Vec embedding judge; the React
  results lab in web/ on GitHub Pages.

## [1.0] - 2026-11-04

### Added
- Compressed Deep: the stemmed-overlap reranker (Deep set 23 to 32 of
  32), the regression gate at 0.900, the failure taxonomy, the quality
  dashboard, the fan-out drafts. CI matrix, CodeQL, Dependabot.

## [0.5] - 2026-11-04

### Added
- Build: BM25 pipeline over a 12-document corpus (19 of 20), budgeted
  judge with a hard call cap, agent protocol scoring.

## [0.1] - 2026-11-04

### Added
- Learn: dependency-free lexical evaluator, 8-case golden set (5 of 8
  by design), 11 unit tests.
