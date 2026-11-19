"""Fetch the confirmatory slices locked in docs/decisions/0004.

New data only, disjoint from the exploratory samples, drawn by the
same deterministic methods as real-data/fetch_samples.py:

- SQuAD: every 10th row of validation rows 5,000 to 9,999 (the
  exploratory sample was every 10th row of rows 0 to 4,999).
- HotpotQA (distractor): validation rows 200 to 699 (the exploratory
  sample was the first 200 rows).

Corpora are built from the new rows only, with the same build_squad
and build_hotpot normalization as fetch_samples.py. Disjointness from
the committed exploratory case ids is asserted before anything is
written. Stdlib only.

Run: python real-data/confirmatory/fetch_confirmatory.py
Writes: real-data/confirmatory/samples/*.json (new files)
"""

import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REAL = os.path.dirname(HERE)
sys.path.insert(0, REAL)

from fetch_samples import build_hotpot, build_squad, write_json  # noqa: E402

PAGE = 100  # the datasets server caps one rows request at 100 rows


def fetch_rows_from(dataset, config, start, count):
    """Fetch validation rows [start, start + count), paginating by 100."""
    rows = []
    offset = start
    while len(rows) < count:
        length = min(PAGE, count - len(rows))
        url = (
            "https://datasets-server.huggingface.co/rows"
            "?dataset={}&config={}&split=validation"
            "&offset={}&length={}"
        ).format(dataset.replace("/", "%2F"), config, offset, length)
        payload = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=60) as fh:
                    payload = json.load(fh)
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
        batch = [entry["row"] for entry in payload["rows"]]
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
    return rows


def committed_ids(name):
    path = os.path.join(REAL, "samples", name)
    with open(path, encoding="utf-8") as fh:
        return {case["id"] for case in json.load(fh)}


def main():
    out_dir = os.path.join(HERE, "samples")
    os.makedirs(out_dir, exist_ok=True)

    squad_rows = fetch_rows_from("rajpurkar/squad", "plain_text", 5000, 5000)[::10]
    assert len(squad_rows) == 500, len(squad_rows)
    squad_cases, squad_corpus = build_squad(squad_rows)
    old = committed_ids("squad_cases.json")
    overlap = old & {c["id"] for c in squad_cases}
    assert not overlap, f"squad overlap with exploratory sample: {sorted(overlap)[:5]}"
    write_json(os.path.join(out_dir, "squad_cases.json"), squad_cases)
    write_json(os.path.join(out_dir, "squad_corpus.json"), squad_corpus)
    n_passages = sum(len(d["sentences"]) for d in squad_corpus)
    print(
        f"squad confirmatory: {len(squad_cases)} cases, "
        f"{len(squad_corpus)} documents, {n_passages} passages, "
        f"0 overlapping case ids"
    )

    hotpot_rows = fetch_rows_from("hotpotqa/hotpot_qa", "distractor", 200, 500)
    assert len(hotpot_rows) == 500, len(hotpot_rows)
    hotpot_cases, hotpot_corpus = build_hotpot(hotpot_rows)
    old = committed_ids("hotpot_cases.json")
    overlap = old & {c["id"] for c in hotpot_cases}
    assert not overlap, f"hotpot overlap with exploratory sample: {sorted(overlap)[:5]}"
    write_json(os.path.join(out_dir, "hotpot_cases.json"), hotpot_cases)
    write_json(os.path.join(out_dir, "hotpot_corpus.json"), hotpot_corpus)
    n_passages = sum(len(d["sentences"]) for d in hotpot_corpus)
    print(
        f"hotpotqa confirmatory: {len(hotpot_cases)} cases, "
        f"{len(hotpot_corpus)} documents, {n_passages} passages, "
        f"0 overlapping case ids"
    )


if __name__ == "__main__":
    main()
