# Website project page copy: rag-eval-harness

Site: jesunahmadushno.com
Status: COPY ONLY, draft for the project page. Dated 2026-11-04.
Nothing on any website was changed by this file.

## Headline

rag-eval-harness: one score hides the failure, so this harness names it

## Summary

rag-eval-harness is an open evaluation harness for retrieval-augmented
generation (RAG) systems, built by Jesun Ahmad Ushno as project P06 in
Roadmap v3. It scores three failure places separately (retrieval,
grounding, and answering the right question), labels every failure,
runs an end-to-end BM25 pipeline under a budgeted judge layer, and
fixes the wrong-passage-on-top failure class with a stemmed-overlap
reranker guarded by a CI regression gate. It runs on the Python 3.12
standard library only, with no model, no API, and no credential.

Status: v1.0, 2026-11-04. Learn, Build, and compressed Deep are done.
Grades on the house 10,000 scale: Learn 8,700, Build 8,700, Deep
(compressed) 7,900. Total tests: 39, all passing at v1.0.

## Results

All results below are measured runs on synthetic corpora, recorded in
the level READMEs in the GitHub repo. They prove the scoring logic, the
pipeline, and the reranking mechanism, not production quality.

| Level | Cases | Passed | Key means | Notes |
| --- | --- | --- | --- | --- |
| Learn | 8 synthetic | 5 of 8 (0.625, by design) | Faithfulness 0.953, recall 0.938, relevance 0.808 | 11 tests; three cases built to fail, each labelled correctly |
| Build | 20 synthetic | 19 of 20 (0.950) | Faithfulness 1.000, recall 1.000, relevance 0.970 | One failure: b11-storytime-when; judge 10 calls, cap 10, 10 of 10 judged passed; 13 tests |
| Deep (compressed) | 32 synthetic | 23 of 32 (0.719) without rerank, 32 of 32 (1.000) with rerank | b11 class 5 of 13 to 13 of 13 | Judge 15 calls, 15 of 15 passed; regression gate threshold 0.900, PASS; 15 tests, 39 total |

## Honest limits

- Synthetic corpora only, at every level.
- The judge is a lexical proxy, not an LLM judge. The budget machinery
  is real; the semantic judgment is not.
- Agent scoring is proven on toy demo agents only.
- Compressed Deep is not the full v2 Deep scope. The remainder is the
  v1.1 backlog in the repo ROADMAP.md.

## Links

- GitHub repo: https://github.com/JesunAhmadUshno/rag-eval-harness
- Release v0.1 (Learn): https://github.com/JesunAhmadUshno/rag-eval-harness/releases/tag/v0.1
- Release v0.5 (Build): https://github.com/JesunAhmadUshno/rag-eval-harness/releases/tag/v0.5
- Release v1.0 (Learn, Build, compressed Deep): https://github.com/JesunAhmadUshno/rag-eval-harness/releases/tag/v1.0
- Tutorial: fanout/tutorial.md in the GitHub repo
- Blog post draft: fanout/blog-post.md in the GitHub repo

## License note

Code: Apache-2.0. Tutorials: CC BY 4.0.
