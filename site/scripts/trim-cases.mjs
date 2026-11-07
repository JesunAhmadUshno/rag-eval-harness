// Build-time trim of ../real-data/results_real.json (4.6 MB) into src/generated/cases.json.
// Keeps, per case: id, question, gold answer, the five retrieved passages (cut to 300 chars),
// and per variant the recorded scores, labels, judge similarity/support/verdict and top-1 flag.
// Reranked variants store the passage order instead of repeating the passages.
// Also counts the test functions in ../tests so the page never types that number by hand.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const real = JSON.parse(fs.readFileSync(path.join(root, 'real-data', 'results_real.json'), 'utf8'));
const CUT = 300;
const LABELS = { hallucination: 1, retrieval_miss: 2, wrong_or_incomplete_answer: 4 };
const r4 = (x) => Math.round(x * 1e4) / 1e4;

const out = { source: 'real-data/results_real.json', generated: real.generated, judgeModel: real.model_judge.model, method: real.method, cut: CUT, dataKind: real.data_kind, datasets: {} };
for (const [ds, variants] of Object.entries(real.datasets)) {
  const base = variants.without_rerank.results;
  const cases = base.map((r) => ({ id: r.id, q: r.question, g: r.gold_answer, c: r.contexts.map((t) => (t.length > CUT ? t.slice(0, CUT) + '…' : t)) }));
  const vs = {};
  for (const [name, run] of Object.entries(variants)) {
    const rows = run.results.map((r, i) => {
      if (r.id !== base[i].id) throw new Error(`id order differs in ${ds}/${name} at ${i}`);
      const used = new Set();
      const order = r.contexts.map((t) => { const k = base[i].contexts.findIndex((b, j) => b === t && !used.has(j)); if (k < 0) throw new Error(`context not in base set: ${r.id}`); used.add(k); return k; });
      const row = {
        p: r.passed ? 1 : 0, f: r4(r.faithfulness), r: r4(r.context_recall), a: r4(r.answer_relevance),
        l: r.labels.reduce((m, l) => m | LABELS[l], 0), s: r.semantic_answer_similarity, u: r.semantic_support,
        j: r.model_judge_pass ? 1 : 0, t: r.top1_contains_gold ? 1 : 0,
      };
      if (order.some((k, j) => k !== j)) row.o = order;
      const top = cases[i].c[order[0]];
      if (r.system_answer !== top) row.x = r.system_answer;
      // Relevance is kept unrounded where the proxy rule (>= 0.50) sits on the line.
      if (Math.abs(r.answer_relevance - 0.5) < 1e-3) row.a = r.answer_relevance;
      return row;
    });
    const { results, ...summary } = run;
    vs[name] = { mode: run.answer_mode, rerank: run.use_rerank, n: run.n, summary, rows };
  }
  out.datasets[ds] = { cases, variants: vs };
}
const testDir = path.join(root, 'tests');
out.testCount = fs.readdirSync(testDir).filter((f) => /^test_.*\.py$/.test(f))
  .reduce((s, f) => s + (fs.readFileSync(path.join(testDir, f), 'utf8').match(/^\s*def test_/gm) || []).length, 0);
fs.mkdirSync(path.join(here, '..', 'src', 'generated'), { recursive: true });
const dest = path.join(here, '..', 'src', 'generated', 'cases.json');
fs.writeFileSync(dest, JSON.stringify(out));
console.log(`trimmed ${(fs.statSync(path.join(root, 'real-data', 'results_real.json')).size / 1e6).toFixed(1)} MB -> ${(fs.statSync(dest).size / 1e6).toFixed(2)} MB, ${out.testCount} tests counted`);
