# 0002: No reranker change shipped in v1.2

Date: 2026-11-04. Status: accepted.

Context: the stemmed-overlap reranker fixed the synthetic b11 class but
did not transfer to real data. The v1.2 transfer test tried a hybrid
BM25 plus coverage key (alpha 0.3, 0.5, 0.7) and pool depth 10.

Decision: the rule set before the test was that a change must help on
real data without regressing the synthetic Deep gate. The hybrid helped
SQuAD (gold in top passage 319 to 330 of 500) and hurt HotpotQA (47 to
39 of 200), so the shipped reranker stays.

Consequences: a learned reranker must beat the shipped one on both
datasets at once. Evidence: real-data/results_rerank_experiment.json.
