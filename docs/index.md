# rag-eval-harness

A dependency-free evaluation harness for retrieval-augmented generation, built in three levels with measured results at each level.

- Learn: a lexical evaluator over an 8-case golden set. Pass rate 0.625 by design (3 cases built to fail, each named correctly).
- Build: an end-to-end BM25 pipeline over a 12-document corpus, a budgeted judge layer, and agent task scoring. 19 of 20 cases passed.
- Deep (compressed): a stemmed query-passage overlap reranker over the top-5 BM25 passages. The Deep set went from 23 of 32 without rerank to 32 of 32 with rerank, with a regression gate that fails the build below a 0.900 pass rate.

Every number above is reproduced by the runners in this repo and checked in CI. The full write-ups are in the level folders: level-1-learn, level-2-build, level-3-deep. Tutorials and the blog post are in fanout/.

Releases: https://github.com/JesunAhmadUshno/rag-eval-harness/releases
