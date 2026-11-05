"""Fetch small real-data samples from the Hugging Face datasets server.

Stdlib only. Downloads at most a few hundred rows per dataset and writes
normalized case and corpus files under samples/. The committed samples
in this repo were produced by this script on 2026-11-04; re-running it
re-fetches the same deterministic first rows of each validation split.

Datasets (license verified from the Hugging Face dataset metadata on
2026-11-04, see DATASETS.md):
- SQuAD (rajpurkar/squad), CC BY-SA 4.0, validation split. The split is
  ordered by article, so the sample takes every 10th row of the first
  1,000 rows: 100 cases spread across about 25 articles.
- HotpotQA (hotpotqa/hotpot_qa, distractor config), CC BY-SA 4.0,
  validation split, first 60 rows.

Normalization: a corpus is a list of documents {id, sentences}. A case is
{id, dataset, question, gold_answer, gold_facts}. For SQuAD the gold fact
is the gold answer span. For HotpotQA the gold facts are the supporting
fact sentences named by the dataset.
"""

import json
import os
import re
import urllib.request

ROWS_URL = (
    "https://datasets-server.huggingface.co/rows"
    "?dataset={dataset}&config={config}&split=validation&offset=0&length={n}"
)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")


def split_sentences(text):
    parts = [p.strip() for p in SENTENCE_SPLIT.split(text.strip())]
    return [p for p in parts if p]


def fetch_rows(dataset, config, n):
    url = ROWS_URL.format(dataset=dataset.replace("/", "%2F"), config=config, n=n)
    with urllib.request.urlopen(url, timeout=60) as fh:
        payload = json.load(fh)
    return [entry["row"] for entry in payload["rows"]]


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

    squad_rows = []
    for offset in range(0, 1000, 100):
        url = (
            "https://datasets-server.huggingface.co/rows"
            "?dataset=rajpurkar%2Fsquad&config=plain_text&split=validation"
            f"&offset={offset}&length=100"
        )
        with urllib.request.urlopen(url, timeout=60) as fh:
            payload = json.load(fh)
        squad_rows.extend(entry["row"] for entry in payload["rows"])
    squad_rows = squad_rows[::10]
    assert len(squad_rows) == 100, len(squad_rows)
    squad_cases, squad_corpus = build_squad(squad_rows)
    write_json(os.path.join(samples, "squad_cases.json"), squad_cases)
    write_json(os.path.join(samples, "squad_corpus.json"), squad_corpus)
    print(f"squad: {len(squad_cases)} cases, {len(squad_corpus)} documents")

    hotpot_rows = fetch_rows("hotpotqa/hotpot_qa", "distractor", 60)
    hotpot_cases, hotpot_corpus = build_hotpot(hotpot_rows)
    write_json(os.path.join(samples, "hotpot_cases.json"), hotpot_cases)
    write_json(os.path.join(samples, "hotpot_corpus.json"), hotpot_corpus)
    print(f"hotpotqa: {len(hotpot_cases)} cases, {len(hotpot_corpus)} documents")


if __name__ == "__main__":
    main()
