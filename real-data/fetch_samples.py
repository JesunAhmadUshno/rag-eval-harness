"""Fetch real-data samples from the Hugging Face datasets server.

Stdlib only. Downloads at most a few thousand rows per dataset and
writes normalized case and corpus files under samples/. The committed
samples in this repo were produced by this script; re-running it
re-fetches the same deterministic rows of each validation split.

Datasets (license verified from the Hugging Face dataset metadata on
2026-11-04, see DATASETS.md):
- SQuAD (rajpurkar/squad), CC BY-SA 4.0, validation split. The split
  is ordered by article, so the sample takes every 10th row of the
  first 5,000 rows: 500 cases spread across the articles in that
  range. (v1.1 took every 10th row of the first 1,000; those 100 cases
  are the first 100 of this sample, so v1.1 and v1.2 numbers stay
  comparable on the shared subset.)
- HotpotQA (hotpotqa/hotpot_qa, distractor config), CC BY-SA 4.0,
  validation split, first 200 rows. (v1.1 took the first 60; they are
  the first 60 of this sample.)

Sampling method, recorded per the v1.2 sample-size step: deterministic
prefix sampling of the validation split as served by the datasets
server, with the stride above for SQuAD. No shuffling, no filtering by
outcome; every selected row becomes a case.

Normalization: a corpus is a list of documents {id, sentences}. A case
is {id, dataset, question, gold_answer, gold_facts}. For SQuAD the gold
fact is the gold answer span. For HotpotQA the gold facts are the
supporting fact sentences named by the dataset.
"""

import json
import os
import re
import urllib.request

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")

PAGE = 100  # the datasets server caps one rows request at 100 rows


def split_sentences(text):
    parts = [p.strip() for p in SENTENCE_SPLIT.split(text.strip())]
    return [p for p in parts if p]


def fetch_rows(dataset, config, n):
    """Fetch the first n validation rows, paginating by 100."""
    rows = []
    offset = 0
    while len(rows) < n:
        length = min(PAGE, n - len(rows))
        url = (
            "https://datasets-server.huggingface.co/rows"
            "?dataset={}&config={}&split=validation"
            "&offset={}&length={}"
        ).format(dataset.replace("/", "%2F"), config, offset, length)
        with urllib.request.urlopen(url, timeout=60) as fh:
            payload = json.load(fh)
        batch = [entry["row"] for entry in payload["rows"]]
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
    return rows


def build_squad(rows):
    docs = {}
    cases = []
    for row in rows:
        context = row["context"]
        if context not in docs:
            doc_id = "squad-{}-{}".format(
                row["title"].replace(" ", "_"), len(docs)
            )
            docs[context] = {"id": doc_id, "sentences": split_sentences(context)}
        gold = row["answers"]["text"][0]
        cases.append(
            {
                "id": "squad-" + row["id"],
                "dataset": "squad",
                "question": row["question"],
                "gold_answer": gold,
                "gold_facts": [gold],
            }
        )
    return cases, list(docs.values())


def build_hotpot(rows):
    docs = {}
    cases = []
    for row in rows:
        titles = row["context"]["title"]
        sentence_groups = row["context"]["sentences"]
        fact_text = {}
        for title, sentences in zip(titles, sentence_groups):
            doc_id = "hotpot-" + title.replace(" ", "_")
            if doc_id not in docs:
                docs[doc_id] = {"id": doc_id, "sentences": list(sentences)}
            for idx, sentence in enumerate(sentences):
                fact_text[(title, idx)] = sentence
        gold_facts = []
        for title, sent_id in zip(
            row["supporting_facts"]["title"], row["supporting_facts"]["sent_id"]
        ):
            text = fact_text.get((title, sent_id))
            if text:
                gold_facts.append(text)
        cases.append(
            {
                "id": "hotpot-" + row["id"],
                "dataset": "hotpotqa",
                "question": row["question"],
                "gold_answer": row["answer"],
                "gold_facts": gold_facts,
            }
        )
    return cases, list(docs.values())


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    samples = os.path.join(here, "samples")
    os.makedirs(samples, exist_ok=True)

    squad_rows = fetch_rows("rajpurkar/squad", "plain_text", 5000)[::10]
    assert len(squad_rows) == 500, len(squad_rows)
    squad_cases, squad_corpus = build_squad(squad_rows)
    write_json(os.path.join(samples, "squad_cases.json"), squad_cases)
    write_json(os.path.join(samples, "squad_corpus.json"), squad_corpus)
    n_passages = sum(len(d["sentences"]) for d in squad_corpus)
    print(
        f"squad: {len(squad_cases)} cases, {len(squad_corpus)} documents, "
        f"{n_passages} passages"
    )

    hotpot_rows = fetch_rows("hotpotqa/hotpot_qa", "distractor", 200)
    assert len(hotpot_rows) == 200, len(hotpot_rows)
    hotpot_cases, hotpot_corpus = build_hotpot(hotpot_rows)
    write_json(os.path.join(samples, "hotpot_cases.json"), hotpot_cases)
    write_json(os.path.join(samples, "hotpot_corpus.json"), hotpot_corpus)
    n_passages = sum(len(d["sentences"]) for d in hotpot_corpus)
    print(
        f"hotpotqa: {len(hotpot_cases)} cases, {len(hotpot_corpus)} documents, "
        f"{n_passages} passages"
    )


if __name__ == "__main__":
    main()
