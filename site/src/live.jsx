import { useEffect, useMemo, useState, useId, useCallback } from 'react';
import corpusDeep from '../../level-3-deep/corpus_deep.json';
import goldenDeep from '../../level-3-deep/golden_set_deep.json';
import goldenLearn from '../../level-1-learn/golden_set.json';
import deep from '../../level-3-deep/results_deep.json';
import cal from '../../model-metrics/calibration.json';
import paired from '../../real-data/results_paired_stats.json';
import data from './generated/cases.json';
import {
  buildIndex, searchPassages, rerank, runAll, scoreCase, STEM_RULES, RERANK_KEYS,
  PASS_FAITHFULNESS, PASS_RECALL, PASS_RELEVANCE, proxyCorrect, agreement, judgeFlags,
} from './rag.js';
import { Range, Select, Seg, Kind, Live, Recorded, blob, f3 } from './ui.jsx';

const index = buildIndex(corpusDeep);
const KEY_LABELS = {
  coverage_f1_bm25: 'coverage, then F1, then BM25 (shipped)',
  coverage_bm25: 'coverage, then BM25',
  f1_bm25: 'F1, then BM25',
  f1_coverage_bm25: 'F1, then coverage, then BM25',
};
const DS = { squad: 'SQuAD', hotpotqa: 'HotpotQA' };
const VARIANT = { without_rerank: 'sentence, no rerank', with_rerank: 'sentence, rerank', span_without_rerank: 'span, no rerank', span_with_rerank: 'span, rerank' };
const LABEL_BITS = [[1, 'hallucination'], [2, 'retrieval_miss'], [4, 'wrong_or_incomplete_answer']];
const labelsOf = (bits) => LABEL_BITS.filter(([b]) => bits & b).map(([, l]) => l);

function Meter({ label, value, line }) {
  const ok = value >= line;
  return (
    <div className="bar-row">
      <div className="lab"><span>{label}</span><b className={ok ? 'ok' : 'no'}>{f3(value)}</b></div>
      <div className="track">
        <div className="fill" style={{ width: `${value * 100}%`, background: ok ? 'var(--good)' : 'var(--bad)' }} />
        <div className="alpha" style={{ left: `${line * 100}%` }} title={`pass line ${line}`} />
      </div>
    </div>
  );
}

function Verdict({ labels }) {
  return labels.length
    ? <span className="labels">{labels.map((l) => <span key={l} className="pill bad">{l}</span>)}</span>
    : <span className="pill good">● passed</span>;
}

// ---------------------------------------------------------------- BM25 playground
export function Playground() {
  const [caseId, setCaseId] = useState('b11-storytime-when');
  const [custom, setCustom] = useState('When does the chess club meet?');
  const [topK, setTopK] = useState(5);
  const [useRerank, setUseRerank] = useState(true);
  const [key, setKey] = useState('coverage_f1_bm25');
  const [rules, setRules] = useState(STEM_RULES);
  const [batch, setBatch] = useState(null);
  const kase = goldenDeep.find((c) => c.id === caseId);
  const question = kase ? kase.question : custom;
  const bm = useMemo(() => searchPassages(index, question, topK), [question, topK]);
  const rr = useMemo(() => rerank(question, bm, { rules, key }), [question, bm, rules, key]);
  const active = useRerank ? rr : bm;
  const contexts = active.map((h) => h.text);
  const scored = kase && scoreCase({ answer: contexts[0] || '', contexts, gold_facts: kase.gold_facts, gold_answer: kase.gold_answer });
  const isShipped = topK === 5 && key === 'coverage_f1_bm25' && rules.length === STEM_RULES.length;

  const runBatch = useCallback(() => {
    const t0 = performance.now();
    const off = runAll(index, goldenDeep, { useRerank: false, topK });
    const on = runAll(index, goldenDeep, { useRerank: true, topK, rules, key });
    setBatch({ off, on, ms: performance.now() - t0, shipped: isShipped });
  }, [topK, rules, key, isShipped]);
  useEffect(() => { runBatch(); }, [runBatch]);
  const toggleRule = (r) => setRules((rs) => (rs.includes(r) ? rs.filter((x) => x !== r) : STEM_RULES.filter((x) => x === r || rs.includes(x))));
  const qid = useId();

  const List = ({ hits, title, rer }) => (
    <div className="plist">
      <h3>{title}</h3>
      <ol>
        {hits.map((h, i) => (
          <li key={h.i} className={kase && h.text === kase.gold_answer ? 'gold' : ''}>
            <span className="rank">{i + 1}</span>
            <div>
              <p>{h.text}</p>
              <small>{h.title} · BM25 {h.score.toFixed(3)}{rer && <> · coverage {f3(h.coverage)} · F1 {f3(h.f1)}</>}{kase && h.text === kase.gold_answer && <b> · gold passage</b>}</small>
            </div>
          </li>
        ))}
        {!hits.length && <li className="empty">No passage shares a content word with the question.</li>}
      </ol>
    </div>
  );

  return (
    <section id="playground" className="card window reveal" data-title="bm25_playground — live">
      <div className="head">
        <div>
          <p className="eyebrow">Live in your browser · <Kind /></p>
          <h2>Watch the reranker <em>pick the right sentence</em>.</h2>
          <p className="sub">
            This is <a href={blob('level-2-build/pipeline.py')}>pipeline.py</a> (BM25 over {index.passages.length} sentences from {corpusDeep.length} documents) and{' '}
            <a href={blob('level-3-deep/reranker.py')}>reranker.py</a> ported to JavaScript. Pick one of the {goldenDeep.length} Deep golden cases or type a question.
            The answer is the top passage, scored by the Level 1 metrics. The build fails unless this port reproduces <a href={blob('level-3-deep/results_deep.json')}>results_deep.json</a>.
          </p>
        </div>
        <Live />
      </div>
      <div className="controls">
        <Select label="Golden case" value={caseId} onChange={setCaseId}
          options={[...goldenDeep.map((c) => [c.id, `${c.id}${c.case_class === 'b11' ? ' (b11 class)' : ''}`]), ['custom', 'Type your own question']]} />
        <div className="field">
          <label htmlFor={qid}>Question</label>
          <input id={qid} className="text" type="text" value={question} readOnly={!!kase} onChange={(e) => setCustom(e.target.value)} onFocus={() => { if (kase) { setCustom(question); setCaseId('custom'); } }} />
        </div>
        <Range label="Passages retrieved (top_k)" value={topK} min={1} max={10} step={1} onChange={setTopK} show={topK} />
        <Select label="Rerank sort key" value={key} onChange={setKey} options={Object.keys(RERANK_KEYS).map((k) => [k, KEY_LABELS[k]])} />
      </div>
      <div className="actions" style={{ marginTop: 0, marginBottom: 16 }}>
        <Seg label="Reranking" value={useRerank} onChange={setUseRerank} options={[[false, 'BM25 only'], [true, 'BM25 + rerank']]} />
        <fieldset className="checks">
          <legend>Stem rules</legend>
          {STEM_RULES.map((r) => <label key={r}><input type="checkbox" checked={rules.includes(r)} onChange={() => toggleRule(r)} /> -{r}</label>)}
        </fieldset>
      </div>
      <div className="grid2">
        <List hits={bm} title="1 · BM25 order" />
        <List hits={rr} title="2 · After rerank" rer />
      </div>
      <div className="answer">
        <div>
          <p className="eyebrow">Answer ({useRerank ? 'reranked' : 'BM25'} top passage)</p>
          <p className="said">{contexts[0] || '(no passage retrieved)'}</p>
          {kase && <p className="hint">Gold answer: {kase.gold_answer}</p>}
        </div>
        {scored ? (
          <div className="bars">
            <Meter label="Faithfulness" value={scored.faithfulness} line={PASS_FAITHFULNESS} />
            <Meter label="Context recall" value={scored.context_recall} line={PASS_RECALL} />
            <Meter label="Answer relevance" value={scored.answer_relevance} line={PASS_RELEVANCE} />
            <Verdict labels={scored.labels} />
          </div>
        ) : <p className="hint">A typed question has no gold answer, so only retrieval is shown. Pick a golden case to score it.</p>}
      </div>
      {batch && (
        <div className="batch">
          <div className="head" style={{ marginBottom: 8 }}>
            <h3>All {batch.on.n} Deep cases at these settings</h3>
            <button className="btn primary" type="button" onClick={runBatch}>Re-run all {goldenDeep.length} cases</button>
          </div>
          <div className="tiles t3" style={{ marginTop: 8 }}>
            <div className="tile"><div className="num">{batch.off.passed}/{batch.off.n}</div><div className="cap">passed, BM25 only (top_k {topK})</div></div>
            <div className="tile"><div className="num">{batch.on.passed}/{batch.on.n}</div><div className="cap">passed with rerank at these settings</div></div>
            <div className="tile"><div className="num">{batch.off.b11} → {batch.on.b11}</div><div className="cap">of {deep.b11.n} b11 cases (right document, wrong passage on top)</div></div>
          </div>
          <div className="strip" role="img" aria-label="Per-case pass or fail without and with rerank">
            {[['BM25', batch.off], ['rerank', batch.on]].map(([n, run]) => (
              <div key={n} className="strip-row"><span>{n}</span>{run.results.map((r) => <i key={r.id} className={`${r.passed ? 'p' : 'f'}${r.cls === 'b11' ? ' b' : ''}`} title={`${r.id}: ${r.passed ? 'pass' : r.labels.join(', ')}`} />)}</div>
            ))}
          </div>
          <p className="hint">
            {batch.ms.toFixed(1)} ms for {2 * batch.on.n} pipeline runs. Outlined squares are the b11 class. {batch.shipped
              ? (batch.off.passed === deep.without.passed && batch.on.passed === deep.with.passed ? `✓ Matches results_deep.json: ${deep.without.passed}/${deep.n} and ${deep.with.passed}/${deep.n}.` : '✗ Does not match results_deep.json.')
              : 'Settings differ from the shipped reranker, so this is your own ablation. The recorded ablation is in the Deep results window.'}
          </p>
        </div>
      )}
    </section>
  );
}

// ---------------------------------------------------------------- Lexical scorer
export function Scorer() {
  const [idx, setIdx] = useState(0);
  const [form, setForm] = useState(() => toForm(goldenLearn[0]));
  useEffect(() => { setForm(toForm(goldenLearn[idx])); }, [idx]);
  const lines = (s) => s.split('\n').map((x) => x.trim()).filter(Boolean);
  const s = scoreCase({ answer: form.answer, contexts: lines(form.contexts), gold_facts: lines(form.facts), gold_answer: form.gold });
  const all = useMemo(() => goldenLearn.map((c) => ({ id: c.id, ...scoreCase(c) })), []);
  const mean = (k) => all.reduce((t, r) => t + r[k], 0) / all.length;
  const ids = { a: useId(), c: useId(), f: useId(), g: useId() };
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  return (
    <section id="scorer" className="card window reveal" data-title="rag_eval.py — live scorer">
      <div className="head">
        <div>
          <p className="eyebrow">Live in your browser · <Kind /></p>
          <h2>Three metrics you can <em>check by hand</em>.</h2>
          <p className="sub">
            A port of <a href={blob('level-1-learn/rag_eval.py')}>rag_eval.py</a>: faithfulness (answer words found in the context), context recall (gold facts whose words the context mostly covers)
            and answer relevance (token F1 against the gold answer). A case passes at {PASS_FAITHFULNESS} / {PASS_RECALL} / {PASS_RELEVANCE}. Edit any field and the scores update.
          </p>
        </div>
        <Live />
      </div>
      <div className="controls" style={{ gridTemplateColumns: 'minmax(0, 1fr)' }}>
        <Select label="Learn golden case" value={idx} onChange={(v) => setIdx(+v)} options={goldenLearn.map((c, i) => [i, `${c.id}: ${c.question}`])} />
      </div>
      <div className="grid2">
        <div className="form">
          <div className="field"><label htmlFor={ids.a}>System answer</label><textarea id={ids.a} rows={2} value={form.answer} onChange={set('answer')} /></div>
          <div className="field"><label htmlFor={ids.c}>Retrieved contexts (one per line)</label><textarea id={ids.c} rows={3} value={form.contexts} onChange={set('contexts')} /></div>
          <div className="field"><label htmlFor={ids.f}>Gold facts (one per line)</label><textarea id={ids.f} rows={2} value={form.facts} onChange={set('facts')} /></div>
          <div className="field"><label htmlFor={ids.g}>Gold answer</label><textarea id={ids.g} rows={2} value={form.gold} onChange={set('gold')} /></div>
        </div>
        <div>
          <div className="bars">
            <Meter label="Faithfulness" value={s.faithfulness} line={PASS_FAITHFULNESS} />
            <Meter label="Context recall" value={s.context_recall} line={PASS_RECALL} />
            <Meter label="Answer relevance" value={s.answer_relevance} line={PASS_RELEVANCE} />
          </div>
          <p style={{ marginTop: 14 }}><Verdict labels={s.labels} /></p>
          <p className="hint">The dashed line on each bar is its pass line. Lexical metrics miss paraphrase: a correct answer in other words scores low on relevance.</p>
          <h3 style={{ marginTop: 18 }}>The {all.length} original cases, scored live</h3>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead><tr><th>Case</th><th>F</th><th>R</th><th>A</th><th>Verdict</th></tr></thead>
              <tbody>
                {all.map((r, i) => (
                  <tr key={r.id} className={i === idx ? 'sel' : ''}><td className="mono">{r.id}</td><td>{f3(r.faithfulness)}</td><td>{f3(r.context_recall)}</td><td>{f3(r.answer_relevance)}</td>
                    <td>{r.passed ? <span className="ok">pass</span> : <span className="no">{r.labels.join(', ')}</span>}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="hint">{all.filter((r) => r.passed).length} of {all.length} pass by design. Means: faithfulness {f3(mean('faithfulness'))}, recall {f3(mean('context_recall'))}, relevance {f3(mean('answer_relevance'))}.</p>
        </div>
      </div>
    </section>
  );
}
function toForm(c) { return { answer: c.answer, contexts: c.contexts.join('\n'), facts: c.gold_facts.join('\n'), gold: c.gold_answer }; }

// ---------------------------------------------------------------- Judge calibrator
const SIMS = paired.grid.similarity.map((x) => Math.round(x * 100));
const SUPS = paired.grid.support.map((x) => Math.round(x * 100));
const SHIP_SIM = Math.round(cal.shipped_thresholds.similarity * 100), SHIP_SUP = Math.round(cal.shipped_thresholds.support * 100);
const SHIP = `${cal.shipped_thresholds.similarity.toFixed(2)} / ${cal.shipped_thresholds.support.toFixed(2)}`;
const answerOf = (d, i, r) => r.x ?? d.cases[i].c[(r.o ?? [0])[0]];

export function Calibrator() {
  const [ds, setDs] = useState('squad');
  const [variant, setVariant] = useState('without_rerank');
  const [sim, setSim] = useState(SHIP_SIM);
  const [sup, setSup] = useState(SHIP_SUP);
  const [metric, setMetric] = useState('kappa');
  const d = data.datasets[ds];
  const rows = d.variants[variant].rows;
  const proxy = useMemo(() => rows.map((r, i) => proxyCorrect(d.cases[i].g, answerOf(d, i, r), r.a)), [d, rows]);
  const a = agreement(judgeFlags(rows, sim, sup), proxy);
  const grid = useMemo(() => SIMS.map((s) => SUPS.map((u) => agreement(judgeFlags(rows, s, u), proxy))), [rows, proxy]);
  const rec = cal.datasets[ds][variant].judge_vs_proxy;
  const ps = paired.datasets[ds].calibration[variant];
  const shipped = sim === SHIP_SIM && sup === SHIP_SUP;
  const W = 520, H = 344, pad = { l: 46, t: 22, r: 8, b: 36 };
  const cw = (W - pad.l - pad.r) / SUPS.length, ch = (H - pad.t - pad.b) / SIMS.length;
  const vals = grid.flat().map((g) => g[metric]);
  const lo = Math.min(...vals), hi = Math.max(...vals);
  return (
    <section id="calibration" className="card window reveal" data-title="judge_calibration — live">
      <div className="head">
        <div>
          <p className="eyebrow">Live recompute over recorded scores · <Kind real /></p>
          <h2>Where should the judge <em>draw the line</em>?</h2>
          <p className="sub">
            The embedding judge ({data.judgeModel}) passes a case when answer similarity and passage support clear two thresholds. Its per-case scores were recorded in a CPU run and are in{' '}
            <a href={blob('real-data/results_real.json')}>results_real.json</a>; the model does not run here. Move the thresholds and agreement with the proxy label is recomputed in your browser.
            Proxy label, as recorded in calibration.json: “{cal.proxy_label}” So this measures consistency, not truth.
          </p>
        </div>
        <Recorded>recorded scores, live math</Recorded>
      </div>
      <div className="controls">
        <Select label="Dataset" value={ds} onChange={setDs} options={Object.entries(DS)} />
        <Select label="Run" value={variant} onChange={setVariant} options={Object.entries(VARIANT)} />
        <Range label="Similarity threshold" value={sim} min={SIMS[0]} max={SIMS[SIMS.length - 1]} step={1} onChange={setSim} show={(sim / 100).toFixed(2)} />
        <Range label="Support threshold" value={sup} min={SUPS[0]} max={SUPS[SUPS.length - 1]} step={1} onChange={setSup} show={(sup / 100).toFixed(2)} />
      </div>
      <div className="grid2">
        <div>
          <div className="tiles" style={{ gridTemplateColumns: '1fr 1fr', marginTop: 0 }}>
            <div className="tile"><div className="num">{a.tp + a.fp}/{a.n}</div><div className="cap">judge passes</div></div>
            <div className="tile"><div className="num">{proxy.filter(Boolean).length}/{a.n}</div><div className="cap">proxy-correct cases</div></div>
            <div className="tile"><div className="num">{a.agreement.toFixed(3)}</div><div className="cap">agreement with the proxy</div></div>
            <div className="tile"><div className="num">{a.kappa.toFixed(4)}</div><div className="cap">Cohen’s kappa</div></div>
          </div>
          <table style={{ marginTop: 14 }} aria-label="Confusion matrix of judge against proxy">
            <thead><tr><th /><th>Proxy correct</th><th>Proxy wrong</th></tr></thead>
            <tbody>
              <tr><th>Judge pass</th><td className="ok">{a.tp}</td><td className="no">{a.fp}</td></tr>
              <tr><th>Judge fail</th><td className="no">{a.fn}</td><td className="ok">{a.tn}</td></tr>
            </tbody>
          </table>
          <p className="hint">
            {shipped
              ? `At the shipped ${SHIP} this matches calibration.json: agreement ${rec.agreement}, kappa ${rec.cohen_kappa} ${Math.abs(a.kappa - rec.cohen_kappa) < 5e-5 ? '✓' : '✗'}.`
              : `Shipped ${SHIP} gives agreement ${rec.agreement}, kappa ${rec.cohen_kappa} (calibration.json).`}
            {' '}Recorded by <a href={blob('real-data/paired_stats.py')}>paired_stats.py</a>: kappa 95% bootstrap interval {ps.kappa_bootstrap_ci95[0]} to {ps.kappa_bootstrap_ci95[1]} ({paired.bootstrap.runs.toLocaleString()} resamples).
          </p>
        </div>
        <div>
          <div className="head" style={{ marginBottom: 6 }}>
            <h3>2-D sweep: {metric === 'kappa' ? 'kappa' : 'agreement'} at every threshold pair</h3>
            <Seg label="Heatmap metric" value={metric} onChange={setMetric} options={[['kappa', 'Kappa'], ['agreement', 'Agreement']]} />
          </div>
          <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Heatmap of judge ${metric} against the proxy over similarity and support thresholds`}>
            {grid.map((row, i) => row.map((g, k) => {
              const v = (g[metric] - lo) / (hi - lo || 1);
              return <rect key={`${i}-${k}`} x={pad.l + k * cw} y={pad.t + (SIMS.length - 1 - i) * ch} width={cw - 1.5} height={ch - 1.5} rx="3" fill="var(--primary)" opacity={0.08 + 0.85 * v}><title>{`sim ${SIMS[i] / 100}, support ${SUPS[k] / 100}: ${metric} ${g[metric].toFixed(4)}`}</title></rect>;
            }))}
            {SIMS.map((s, i) => i % 2 === 0 && <text key={s} x={pad.l - 6} y={pad.t + (SIMS.length - 1 - i) * ch + ch / 2 + 4} textAnchor="end">{(s / 100).toFixed(2)}</text>)}
            {SUPS.map((u, k) => k % 2 === 0 && <text key={u} x={pad.l + k * cw + cw / 2} y={H - 20} textAnchor="middle">{(u / 100).toFixed(2)}</text>)}
            <text x={pad.l + (W - pad.l - pad.r) / 2} y={H - 4} textAnchor="middle">support threshold →</text>
            <text x={0} y={11}>similarity ↑</text>
            {SIMS.includes(sim) && SUPS.includes(sup) && <rect x={pad.l + SUPS.indexOf(sup) * cw - 1} y={pad.t + (SIMS.length - 1 - SIMS.indexOf(sim)) * ch - 1} width={cw + 0.5} height={ch + 0.5} rx="4" fill="none" stroke="var(--text)" strokeWidth="2" />}
            <rect x={pad.l + SUPS.indexOf(SHIP_SUP) * cw + cw / 2 - 3} y={pad.t + (SIMS.length - 1 - SIMS.indexOf(SHIP_SIM)) * ch + ch / 2 - 3} width="6" height="6" fill="var(--warn)" />
          </svg>
          <p className="hint">Stronger colour is higher ({metric} {lo.toFixed(3)} to {hi.toFixed(3)}). The outlined cell is your setting, the amber dot the shipped pair. In sentence mode the answer is a retrieved passage, so support is at its maximum for every case and only similarity matters there.</p>
          <p className="hint">
            Held-out check (recorded, paired_stats.py): fitting the pair on even-numbered cases picks {ps.two_fold.fit_even_test_odd.fitted_similarity} / {ps.two_fold.fit_even_test_odd.fitted_support} and scores kappa {ps.two_fold.fit_even_test_odd.test_kappa_fitted} on the odd cases,
            against {ps.two_fold.fit_even_test_odd.test_kappa_shipped} for the shipped pair.
          </p>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------- Case browser
const PAGE = 15;
export function CaseBrowser() {
  const [ds, setDs] = useState('squad');
  const [mode, setMode] = useState('sentence');
  const [rr, setRr] = useState('without');
  const [verdict, setVerdict] = useState('all');
  const [label, setLabel] = useState('all');
  const [q, setQ] = useState('');
  const [shown, setShown] = useState(PAGE);
  const [sel, setSel] = useState(null);
  const variant = `${mode === 'span' ? 'span_' : ''}${rr}_rerank`;
  const d = data.datasets[ds];
  const rows = d.variants[variant].rows;
  const qid = useId();
  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return rows.map((r, i) => ({ r, i })).filter(({ r, i }) => {
      if (verdict === 'lex_pass' && !r.p) return false;
      if (verdict === 'lex_fail' && r.p) return false;
      if (verdict === 'judge_pass' && !r.j) return false;
      if (verdict === 'judge_fail' && r.j) return false;
      if (label === 'none' && r.l) return false;
      if (label !== 'all' && label !== 'none' && !labelsOf(r.l).includes(label)) return false;
      return !needle || d.cases[i].q.toLowerCase().includes(needle) || d.cases[i].g.toLowerCase().includes(needle);
    });
  }, [rows, verdict, label, q, d]);
  useEffect(() => { setShown(PAGE); setSel(null); }, [ds, variant, verdict, label, q]);
  const totalRows = Object.values(data.datasets).reduce((s, x) => s + Object.values(x.variants).reduce((t, v) => t + v.rows.length, 0), 0);
  const totalCases = Object.values(data.datasets).reduce((s, x) => s + x.cases.length, 0);
  const pick = sel != null ? { r: rows[sel], c: d.cases[sel] } : null;
  return (
    <section id="cases" className="card window reveal" data-title={`case_browser — ${totalRows.toLocaleString()} recorded rows`}>
      <div className="head">
        <div>
          <p className="eyebrow">Replay of recorded runs · <Kind real /></p>
          <h2>Open any case and <em>see why it failed</em>.</h2>
          <p className="sub">
            {totalCases.toLocaleString()} real questions ({Object.entries(data.datasets).map(([k, x]) => `${x.cases.length} ${DS[k]}`).join(', ')}) × {Object.keys(d.variants).length} recorded variants. Rows are trimmed at build time from{' '}
            <a href={blob('real-data/results_real.json')}>results_real.json</a> (passages cut to {data.cut} characters); nothing here is re-run.
          </p>
        </div>
        <Recorded />
      </div>
      <div className="controls">
        <Select label="Dataset" value={ds} onChange={setDs} options={Object.entries(DS)} />
        <Select label="Answer mode" value={mode} onChange={setMode} options={[['sentence', 'Sentence (top passage)'], ['span', 'Span (extracted)']]} />
        <Select label="Reranker" value={rr} onChange={setRr} options={[['without', 'Without rerank'], ['with', 'With rerank']]} />
        <Select label="Verdict" value={verdict} onChange={setVerdict} options={[['all', 'All'], ['lex_pass', 'Lexical pass'], ['lex_fail', 'Lexical fail'], ['judge_pass', 'Judge pass'], ['judge_fail', 'Judge fail']]} />
        <Select label="Failure label" value={label} onChange={setLabel} options={[['all', 'Any'], ['none', 'No label'], ...LABEL_BITS.map(([, l]) => [l, l])]} />
        <div className="field"><label htmlFor={qid}>Search question or gold</label><input id={qid} className="text" type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="e.g. Broncos" /></div>
      </div>
      <p className="hint" aria-live="polite">{filtered.length} of {rows.length} cases match. Select a row to open it.</p>
      <div style={{ overflowX: 'auto' }}>
        <table className="cases">
          <thead><tr><th>Question</th><th>Gold</th><th>Lexical</th><th>Judge</th><th>Top-1 has gold</th></tr></thead>
          <tbody>
            {filtered.slice(0, shown).map(({ r, i }) => (
              <tr key={i} className={sel === i ? 'sel' : ''} onClick={() => setSel(i)} tabIndex={0} onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), setSel(i))} aria-selected={sel === i}>
                <td>{d.cases[i].q}</td><td>{d.cases[i].g}</td>
                <td className={r.p ? 'ok' : 'no'}>{r.p ? 'pass' : 'fail'}</td>
                <td className={`nw ${r.j ? 'ok' : 'no'}`}>{r.j ? 'pass' : 'fail'} <span className="hint">{r.s.toFixed(2)}</span></td>
                <td>{r.t ? 'yes' : 'no'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {shown < filtered.length && <div className="actions" style={{ marginTop: 12 }}><button className="btn ghost" type="button" onClick={() => setShown((s) => s + PAGE)}>Show {Math.min(PAGE, filtered.length - shown)} more</button></div>}
      {pick && (
        <div className="detail" aria-live="polite">
          <div className="head" style={{ marginBottom: 8 }}>
            <h3>{pick.c.q}</h3>
            <button className="btn ghost" type="button" onClick={() => setSel(null)}>Close</button>
          </div>
          <p className="mono">{pick.c.id} · {DS[ds]} · {VARIANT[variant]}</p>
          <div className="grid2">
            <div>
              <p><b>Gold answer:</b> {pick.c.g}</p>
              <p><b>System answer:</b> {answerOf(d, sel, pick.r)}</p>
              <p><Verdict labels={labelsOf(pick.r.l)} /></p>
              <table>
                <tbody>
                  <tr><td>Faithfulness</td><td>{f3(pick.r.f)}</td><td>Context recall</td><td>{f3(pick.r.r)}</td></tr>
                  <tr><td>Answer relevance</td><td>{f3(pick.r.a)}</td><td>Top-1 has gold</td><td>{pick.r.t ? 'yes' : 'no'}</td></tr>
                  <tr><td>Judge similarity</td><td>{pick.r.s.toFixed(4)}</td><td>Judge support</td><td>{pick.r.u.toFixed(4)}</td></tr>
                  <tr><td>Judge verdict</td><td className={pick.r.j ? 'ok' : 'no'}>{pick.r.j ? 'pass' : 'fail'}</td><td>Lexical verdict</td><td className={pick.r.p ? 'ok' : 'no'}>{pick.r.p ? 'pass' : 'fail'}</td></tr>
                </tbody>
              </table>
            </div>
            <div className="plist">
              <h3>Retrieved passages, in ranked order</h3>
              <ol>
                {(pick.r.o ?? pick.c.c.map((_, k) => k)).map((k, rank) => (
                  <li key={k}><span className="rank">{rank + 1}</span><div><p>{pick.c.c[k]}</p></div></li>
                ))}
              </ol>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

