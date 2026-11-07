// Code that runs live in the browser. Each part ports a Python module in this repo,
// and src/rag.check.mjs fails the build unless it reproduces the recorded results.
//   scorer   -> level-1-learn/rag_eval.py (re-exported from the verified web/src/metrics.js)
//   BM25     -> level-2-build/pipeline.py (BM25Index.search_passages)
//   reranker -> level-3-deep/reranker.py, with the switches level-3-deep/ablation.py uses
//   stats    -> real-data/paired_stats.py and model-metrics/calibrate_judge.py
import { scoreCase } from '../../web/src/metrics.js';
export { scoreCase, PASS_FAITHFULNESS, PASS_RECALL, PASS_RELEVANCE } from '../../web/src/metrics.js';

const TOKEN_RE = /[a-z0-9]+/g;
// Build/Deep stopwords: the Learn list plus question words (pipeline.py, reranker.py).
const STOP = new Set(('a an the is are was were be been of to in on for and or as at by ' +
  'it its this that these those from with without into over under ' +
  'do does did how what when where who can i you').split(' '));
const K1 = 1.5, B = 0.75;
export const tokens = (text) => (text.toLowerCase().match(TOKEN_RE) || []).filter((t) => !STOP.has(t));

export function buildIndex(corpus) {
  const passages = [];
  for (const doc of corpus) for (const s of doc.sentences) passages.push({ doc: doc.id, title: doc.title, text: s });
  const docTokens = passages.map((p) => tokens(p.text));
  const tf = docTokens.map((ts) => { const m = new Map(); for (const t of ts) m.set(t, (m.get(t) || 0) + 1); return m; });
  const avgdl = docTokens.reduce((s, t) => s + t.length, 0) / docTokens.length;
  const df = new Map();
  for (const ts of docTokens) for (const t of new Set(ts)) df.set(t, (df.get(t) || 0) + 1);
  const n = passages.length, idf = new Map();
  for (const [t, c] of df) idf.set(t, Math.log(1 + (n - c + 0.5) / (c + 0.5)));
  return { passages, docTokens, tf, avgdl, idf };
}

function bm25(index, qTerms, i) {
  const dl = index.docTokens[i].length;
  if (!dl) return 0;
  const tf = index.tf[i];
  let score = 0;
  for (const term of qTerms) {
    const f = tf.get(term);
    if (!f) continue;
    score += (index.idf.get(term) || 0) * f * (K1 + 1) / (f + K1 * (1 - B + B * dl / index.avgdl));
  }
  return score;
}

// Top-k passages by BM25, ties on passage order, zero scores dropped.
export function searchPassages(index, query, topK = 5) {
  const q = [...new Set(tokens(query))];
  const scored = index.passages.map((p, i) => ({ ...p, i, score: bm25(index, q, i) }));
  scored.sort((a, b) => b.score - a.score || a.i - b.i);
  return scored.slice(0, topK).filter((h) => h.score > 0);
}

export const STEM_RULES = ['ies', 'sses', 'ing', 'ed', 's'];
export function stem(t, rules = STEM_RULES) {
  if (rules.includes('ies') && t.length > 4 && t.endsWith('ies')) return t.slice(0, -3) + 'y';
  if (rules.includes('sses') && t.endsWith('sses')) return t.slice(0, -2);
  if (rules.includes('ing') && t.length > 5 && t.endsWith('ing')) return t.slice(0, -3);
  if (rules.includes('ed') && t.length > 4 && t.endsWith('ed')) return t.slice(0, -2);
  if (rules.includes('s') && t.length > 3 && t.endsWith('s') && !t.endsWith('ss')) return t.slice(0, -1);
  return t;
}

export function overlap(query, passage, rules = STEM_RULES) {
  const q = new Set(tokens(query).map((t) => stem(t, rules)));
  const p = new Set(tokens(passage).map((t) => stem(t, rules)));
  if (!q.size || !p.size) return { coverage: 0, f1: 0 };
  let shared = 0;
  for (const t of q) if (p.has(t)) shared++;
  const coverage = shared / q.size, precision = shared / p.size;
  return { coverage, f1: shared ? 2 * precision * coverage / (precision + coverage) : 0 };
}

export const RERANK_KEYS = {
  coverage_f1_bm25: ['coverage', 'f1', 'score'],
  coverage_bm25: ['coverage', 'score'],
  f1_bm25: ['f1', 'score'],
  f1_coverage_bm25: ['f1', 'coverage', 'score'],
};

// Reorder BM25 hits by the key, descending; ties keep BM25 order.
export function rerank(query, hits, { rules = STEM_RULES, key = 'coverage_f1_bm25' } = {}) {
  const fields = RERANK_KEYS[key];
  const dec = hits.map((h, idx) => ({ ...h, ...overlap(query, h.text, rules), idx }));
  dec.sort((a, b) => { for (const f of fields) if (b[f] !== a[f]) return b[f] - a[f]; return a.idx - b.idx; });
  return dec;
}

// Deep pipeline: BM25 top-k, optional rerank, extractive answer = top passage, Learn scorer.
export function runCase(index, kase, { useRerank, topK = 5, rules, key }) {
  const bm = searchPassages(index, kase.question, topK);
  const ranked = useRerank ? rerank(kase.question, bm, { rules, key }) : bm;
  const contexts = ranked.map((h) => h.text);
  const scored = scoreCase({ answer: contexts[0] || '', contexts, gold_facts: kase.gold_facts, gold_answer: kase.gold_answer });
  return { bm, ranked, answer: contexts[0] || '', ...scored };
}

export function runAll(index, cases, opts) {
  const results = cases.map((c) => ({ id: c.id, cls: c.case_class, ...runCase(index, c, opts) }));
  const n = results.length, mean = (k) => results.reduce((s, r) => s + r[k], 0) / n;
  return {
    results, n, passed: results.filter((r) => r.passed).length,
    b11: results.filter((r) => r.cls === 'b11' && r.passed).length,
    mean_faithfulness: mean('faithfulness'), mean_context_recall: mean('context_recall'), mean_answer_relevance: mean('answer_relevance'),
  };
}

// ---------- statistics ----------
export function wilson(passed, n, z = 1.959964) {
  if (!n) return [0, 0];
  const p = passed / n, den = 1 + z * z / n, c = (p + z * z / (2 * n)) / den;
  const h = (z / den) * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
  return [c - h, c + h];
}

// Exact two-sided binomial test at p = 0.5 (n up to ~1000 without underflow).
export function binomTwoSided(k, n) {
  if (!n) return 1;
  const lo = Math.min(k, n - k);
  let pmf = 0.5 ** n, tail = 0;
  for (let i = 0; i <= lo; i++) { tail += pmf; pmf *= (n - i) / (i + 1); }
  return Math.min(1, 2 * tail);
}

export function mcnemar(a, b) {
  let aOnly = 0, bOnly = 0;
  for (let i = 0; i < a.length; i++) { if (a[i] && !b[i]) aOnly++; else if (b[i] && !a[i]) bOnly++; }
  return { aOnly, bOnly, discordant: aOnly + bOnly, p: binomTwoSided(aOnly, aOnly + bOnly) };
}

const norm = (s) => ' ' + s.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim() + ' ';
// Proxy label from model-metrics/calibrate_judge.py: gold inside the answer, or relevance >= 0.50.
export const proxyCorrect = (gold, answer, relevance) => norm(answer).includes(norm(gold)) || relevance >= 0.5;

export function agreement(judge, proxy) {
  const n = judge.length;
  let tp = 0, fp = 0, fn = 0;
  for (let i = 0; i < n; i++) { if (judge[i] && proxy[i]) tp++; else if (judge[i]) fp++; else if (proxy[i]) fn++; }
  const tn = n - tp - fp - fn, observed = (tp + tn) / n;
  const pa = (tp + fp) / n, pb = (tp + fn) / n, expected = pa * pb + (1 - pa) * (1 - pb);
  return { n, tp, fp, fn, tn, agreement: observed, kappa: expected < 1 ? (observed - expected) / (1 - expected) : 1 };
}

// Thresholds in hundredths so 0.30 is exactly 30/100, as in paired_stats.py.
export const judgeFlags = (rows, sim, sup) => rows.map((r) => r.s >= sim / 100 && r.u >= sup / 100);
export const round4 = (x) => Math.round(x * 1e4) / 1e4;
