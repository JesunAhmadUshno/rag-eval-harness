"""Judge calibration check (v1.2): how the embedding judge was set,
and how far its verdicts agree with labels the gold data already has.

What this script does, with no new labels and no model run:
- It reads real-data/results_real.json, which already carries the
  embedding judge's per-case similarity, support, and pass verdict.
- It builds a proxy correctness label from the gold data: a case is
  proxy-correct when the normalized gold answer appears inside the
  system answer, or the lexical token F1 against the gold answer is
  at least 0.50 (the harness's own relevance pass line). A proxy is
  not a human label, and this file never calls it one.
- It reports agreement between the judge verdict and the proxy, and
  between the judge verdict and the lexical pass rule: raw agreement,
  Cohen's kappa, and the confusion counts.
- It sweeps the similarity threshold (support held at the shipped
  0.25) and reports pass counts and proxy agreement at each step, so
  the shipped 0.30 constant can be judged against its neighbours.

Output: calibration.json next to this file. The findings are written
up in model-metrics/README.md.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from rag_eval import PASS_RELEVANCE  # noqa: E402

NORM_RE = re.compile(r"[^a-z0-9]+")
SHIPPED_SUPPORT = 0.25
SWEEP = [0.20, 0.25, 0.30, 0.35, 0.40]


def _norm(text):
    return " " + NORM_RE.sub(" ", text.lower()).strip() + " "


def proxy_correct(result):
    return (
        _norm(result["gold_answer"]) in _norm(result["system_answer"])
        or result["answer_relevance"] >= PASS_RELEVANCE
    )


def agreement(pairs):
    """pairs: list of (a, b) booleans. Returns agreement stats."""
    n = len(pairs)
    if not n:
        return {"n": 0}
    agree = sum(1 for a, b in pairs if a == b)
    tp = sum(1 for a, b in pairs if a and b)
    fp = sum(1 for a, b in pairs if a and not b)
    fn = sum(1 for a, b in pairs if not a and b)
    tn = sum(1 for a, b in pairs if not a and not b)
    pa = (tp + fp) / n
    pb = (tp + fn) / n
    expected = pa * pb + (1 - pa) * (1 - pb)
    observed = agree / n
    kappa = (observed - expected) / (1 - expected) if expected < 1 else 1.0
    return {
        "n": n,
        "agreement": round(observed, 4),
        "cohen_kappa": round(kappa, 4),
        "both_pass": tp,
        "judge_only": fp,
        "other_only": fn,
        "both_fail": tn,
    }


def main():
    with open(
        os.path.join(ROOT, "real-data", "results_real.json"), encoding="utf-8"
    ) as fh:
        real = json.load(fh)
    payload = {
        "generated": "2026-11-04",
        "source": "real-data/results_real.json (v1.2 run)",
        "proxy_label": (
            "gold answer text contained in the system answer, or "
            "lexical answer relevance >= 0.50. A proxy built from gold "
            "labels, not human annotation."
        ),
        "shipped_thresholds": {"similarity": 0.30, "support": SHIPPED_SUPPORT},
        "datasets": {},
    }
    for dataset, variants in real["datasets"].items():
        payload["datasets"][dataset] = {}
        for variant, run in variants.items():
            results = run["results"]
            if "model_judge_pass" not in results[0]:
                continue
            proxy = [proxy_correct(r) for r in results]
            judge = [bool(r["model_judge_pass"]) for r in results]
            lexical = [bool(r["passed"]) for r in results]
            sweep = {}
            for threshold in SWEEP:
                swept = [
                    r["semantic_answer_similarity"] >= threshold
                    and r["semantic_support"] >= SHIPPED_SUPPORT
                    for r in results
                ]
                sweep[str(threshold)] = {
                    "judge_passed": sum(swept),
                    "agreement_with_proxy": agreement(
                        list(zip(swept, proxy))
                    )["agreement"],
                }
            entry = {
                "n": len(results),
                "proxy_correct": sum(proxy),
                "judge_vs_proxy": agreement(list(zip(judge, proxy))),
                "judge_vs_lexical": agreement(list(zip(judge, lexical))),
                "threshold_sweep": sweep,
            }
            payload["datasets"][dataset][variant] = entry
            jvp = entry["judge_vs_proxy"]
            print(
                f"{dataset} {variant}: proxy-correct {entry['proxy_correct']}/"
                f"{entry['n']}, judge agreement {jvp['agreement']} "
                f"(kappa {jvp['cohen_kappa']}), judge vs lexical "
                f"{entry['judge_vs_lexical']['agreement']}"
            )
    out_path = os.path.join(HERE, "calibration.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
