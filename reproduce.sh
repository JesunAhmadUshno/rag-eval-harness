#!/bin/sh
# Regenerates every scored result from the committed evidence, then fails if any result file changed.
# real-data/results_real.json is recorded evidence (its embedding judge needs model2vec), so it is read, not rewritten.
set -e
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
$PY level-3-deep/run_deep.py
$PY level-3-deep/regression_gate.py
$PY level-3-deep/ablation.py
$PY real-data/rerank_experiment.py
$PY real-data/paired_stats.py
$PY model-metrics/calibrate_judge.py
git diff --exit-code -- level-3-deep/results_deep.json level-3-deep/dashboard.md level-3-deep/results_ablation.json \
  real-data/results_rerank_experiment.json real-data/results_paired_stats.json model-metrics/calibration.json
echo "reproduce: PASS, every result regenerated unchanged"
