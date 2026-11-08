# 0003: Result files stay beside the scripts that write them

Date: 2026-11-08. Status: accepted.

Context: the portfolio standard v2 layout names experiments/ and
results/. Here every result file is written next to its script
(level-3-deep/, real-data/, model-metrics/), and the dashboard imports,
the CI drift checks, the tests and the level READMEs all read them
there.

Decision: no experiments/ or results/ folder. The README layout table
maps each folder; reproduce.sh is the one command that regenerates
every scored result and fails on drift. Raw evidence is the committed
samples (real-data/samples/), the synthetic sets and the recorded run
real-data/results_real.json.

Consequences: moving the files would break the dashboard and the
history of every result file for no gain in checkability.
