# Datasets used by the real-data runs

Every dataset below is public, free, and license-checked from its
source page on 2026-11-04. Samples are small on purpose: the repo stays
lean, and the fetch script can rebuild the exact same samples.

| Dataset | Source | License | Full size | Sample used here |
| --- | --- | --- | --- | --- |
| SQuAD v1.1 (rajpurkar/squad) | https://huggingface.co/datasets/rajpurkar/squad | CC BY-SA 4.0 (license tag in the Hugging Face dataset metadata, checked 2026-11-04) | 87,599 train and 10,570 validation questions | 500 validation cases (every 10th row of the first 5,000, because the split is ordered by article), 467 unique context documents, 2,248 passages |
| HotpotQA (hotpotqa/hotpot_qa, distractor config) | https://huggingface.co/datasets/hotpotqa/hotpot_qa | CC BY-SA 4.0 (license tag in the Hugging Face dataset metadata, checked 2026-11-04) | 90,447 train and 7,405 validation questions | 200 validation cases (first 200 rows), 1,991 context documents, 8,274 passages |

Sampling history and method: v1.1 used 100 SQuAD cases (every 10th of
the first 1,000 rows) and 60 HotpotQA cases (first 60 rows). The v1.2
samples extend the same deterministic prefix method, and the v1.1
cases are exactly the first 100 and first 60 of the v1.2 samples. One
consequence is stated wherever it matters: the retrieval corpus is
the union of the sample's documents, so the v1.2 corpus is larger and
retrieval over it is harder than it was over the v1.1 corpus.

Attribution: SQuAD was built by the Stanford NLP group from Wikipedia
articles. HotpotQA was built by Yang et al. from Wikipedia. Both samples
keep the original question, answer, and context text, so the CC BY-SA
share-alike terms apply to the sample files in samples/.

What the samples are for: the corpus files are the retrieval pool and
the case files carry the question, the gold answer, and the gold facts
(the SQuAD answer span; the HotpotQA supporting fact sentences). The
harness scores its own pipeline against them in run_real_eval.py.
Results live in results_real.json and are reported per dataset, always
separate from the synthetic sets.
