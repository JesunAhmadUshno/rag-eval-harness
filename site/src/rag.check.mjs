// Known-answer check, run by "npm run build" before vite. Every computation the page runs
// in the browser must reproduce the numbers this repo recorded with its Python code.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildIndex, runAll, scoreCase, wilson, binomTwoSided, mcnemar, proxyCorrect, agreement, judgeFlags, STEM_RULES } from './rag.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const read = (...p) => JSON.parse(fs.readFileSync(path.join(here, '..', '..', ...p), 'utf8'));
const close = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b}`);

// 1. Learn scorer over the 8 golden cases (level-1-learn README: 5/8, 0.953 / 0.938 / 0.808).
const learn = read('level-1-learn', 'golden_set.json').map(scoreCase);
assert.equal(learn.filter((r) => r.passed).length, 5, 'learn passed');
const lm = (k) => learn.reduce((s, r) => s + r[k], 0) / learn.length;
close(lm('faithfulness'), 0.953, 5e-4, 'learn faithfulness');
close(lm('context_recall'), 0.938, 5e-4, 'learn recall');
close(lm('answer_relevance'), 0.808, 5e-4, 'learn relevance');

// 2. BM25 + reranker port over the Deep set against results_deep.json.
const deep = read('level-3-deep', 'results_deep.json');
const index = buildIndex(read('level-3-deep', 'corpus_deep.json'));
const golden = read('level-3-deep', 'golden_set_deep.json');
const without = runAll(index, golden, { useRerank: false });
const withR = runAll(index, golden, { useRerank: true });
assert.equal(without.passed, deep.without.passed, 'deep without');
assert.equal(withR.passed, deep.with.passed, 'deep with');
assert.equal(without.b11, deep.b11.passed_without, 'b11 without');
assert.equal(withR.b11, deep.b11.passed_with, 'b11 with');
close(without.mean_answer_relevance, deep.without.mean_answer_relevance, 1e-9, 'deep relevance without');
close(withR.mean_answer_relevance, deep.with.mean_answer_relevance, 1e-9, 'deep relevance with');
assert.deepEqual(withR.results.filter((r) => r.passed).map((r) => r.id), deep.with_passed_ids, 'with passed ids');

// 3. Live ablation switches against level-3-deep/results_ablation.json (synthetic block).
const abl = read('level-3-deep', 'results_ablation.json');
for (const [name, spec] of Object.entries(abl.variants)) {
  const opts = spec === 'no rerank' ? { useRerank: false } : { useRerank: true, rules: spec.rules, key: spec.key };
  const r = runAll(index, golden, opts);
  assert.equal(r.passed, abl.synthetic_deep[name].passed, `ablation ${name}`);
  assert.equal(r.b11, abl.synthetic_deep[name].b11_passed, `ablation b11 ${name}`);
}
assert.deepEqual(abl.variants.shipped.rules, STEM_RULES);

// 4. Judge calibration recompute on the trimmed rows against calibration.json and the 2-D sweep.
const trimmed = JSON.parse(fs.readFileSync(path.join(here, 'generated', 'cases.json'), 'utf8'));
const cal = read('model-metrics', 'calibration.json');
const paired = read('real-data', 'results_paired_stats.json');
const full = read('real-data', 'results_real.json');
for (const [ds, d] of Object.entries(trimmed.datasets)) {
  for (const [v, run] of Object.entries(d.variants)) {
    const rows = run.rows;
    const proxy = rows.map((r, i) => proxyCorrect(d.cases[i].g, r.x ?? d.cases[i].c[(r.o ?? [0])[0]], r.a));
    const want = cal.datasets[ds][v];
    assert.equal(proxy.filter(Boolean).length, want.proxy_correct, `${ds}/${v} proxy`);
    const a = agreement(judgeFlags(rows, 30, 25), proxy);
    close(a.agreement, want.judge_vs_proxy.agreement, 5e-5, `${ds}/${v} agreement`);
    close(a.kappa, want.judge_vs_proxy.cohen_kappa, 5e-5, `${ds}/${v} kappa`);
    assert.deepEqual([a.tp, a.fp, a.fn, a.tn], [want.judge_vs_proxy.both_pass, want.judge_vs_proxy.judge_only, want.judge_vs_proxy.other_only, want.judge_vs_proxy.both_fail]);
    assert.equal(judgeFlags(rows, 30, 25).filter(Boolean).length, rows.filter((r) => r.j).length, `${ds}/${v} judge verdicts`);
    const sweep = paired.datasets[ds].calibration[v].sweep;
    paired.grid.similarity.forEach((s, i) => paired.grid.support.forEach((u, k) => {
      const f = judgeFlags(rows, Math.round(s * 100), Math.round(u * 100));
      const g = agreement(f, proxy);
      assert.equal(f.filter(Boolean).length, sweep[i][k][0], `${ds}/${v} sweep count ${s},${u}`);
      close(g.kappa, sweep[i][k][2], 5e-5, `${ds}/${v} sweep kappa ${s},${u}`);
    }));
    // Wilson intervals and counts against paired_stats.py
    const pv = paired.datasets[ds].variants[v];
    for (const [key, field] of [['lexical', 'p'], ['judge', 'j'], ['top1_contains_gold', 't']]) {
      const k = rows.filter((r) => r[field]).length;
      assert.equal(k, pv[`${key}_passed`], `${ds}/${v} ${key} count`);
      assert.equal(k, full.datasets[ds][v].results.filter((r) => (field === 'p' ? r.passed : field === 'j' ? r.model_judge_pass : r.top1_contains_gold)).length);
      const [lo, hi] = wilson(k, rows.length);
      close(lo, pv[`${key}_ci95`][0], 5e-5, `${ds}/${v} ${key} wilson lo`);
      close(hi, pv[`${key}_ci95`][1], 5e-5, `${ds}/${v} ${key} wilson hi`);
    }
    assert.equal(rows.filter((r) => r.p).length, full.datasets[ds][v].passed);
    assert.equal(rows.filter((r) => r.j).length, full.datasets[ds][v].model_summary.model_judge_passed);
  }
  // 5. Paired McNemar tests and the reranker sign test.
  const flags = (v, f) => d.variants[v].rows.map((r) => !!r[f]);
  const pairs = { sentence: ['without_rerank', 'with_rerank'], span: ['span_without_rerank', 'span_with_rerank'] };
  for (const [mode, [a, b]] of Object.entries(pairs)) {
    for (const [key, f] of [['passed', 'p'], ['model_judge_pass', 'j'], ['top1_contains_gold', 't']]) {
      const m = mcnemar(flags(a, f), flags(b, f)), want = paired.datasets[ds].rerank_effect[mode][key];
      assert.deepEqual([m.aOnly, m.bOnly], [want.a_only, want.b_only], `${ds} ${mode} ${key}`);
      close(m.p, want.p_exact, 5e-5, `${ds} ${mode} ${key} p`);
    }
  }
  const st = paired.datasets[ds].reranker_sign_test;
  close(binomTwoSided(st.helped, st.helped + st.hurt), st.p_exact, 5e-5, `${ds} sign test`);
}
close(binomTwoSided(1, 4), 0.625, 1e-12, 'binomial 1 of 4');
assert.ok(trimmed.testCount > 0, 'test count');
console.log('rag ok', { deepWithout: without.passed, deepWith: withR.passed, b11: [without.b11, withR.b11], learnPassed: 5, calibrationVariants: 8 });
