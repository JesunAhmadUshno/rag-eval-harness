import { useState } from 'react';
import deep from '../../level-3-deep/results_deep.json';
import baseline from '../../level-3-deep/baseline.json';
import goldenDeep from '../../level-3-deep/golden_set_deep.json';
import corpusDeep from '../../level-3-deep/corpus_deep.json';
import ablation from '../../level-3-deep/results_ablation.json';
import rerankExp from '../../real-data/results_rerank_experiment.json';
import readme from '../../README.md?raw';
import data from './generated/cases.json';
import { mcnemar, wilson, binomTwoSided } from './rag.js';
import { MenuBar, Dock, useReveal, Seg, Kind, Live, Recorded, REPO, blob, pct, f3, pfmt } from './ui.jsx';
import { Playground, Scorer, Calibrator, CaseBrowser } from './live.jsx';

const DS = { squad: 'SQuAD', hotpotqa: 'HotpotQA' };
const VARIANTS = [['without_rerank', 'sentence'], ['with_rerank', 'sentence + rerank'], ['span_without_rerank', 'span'], ['span_with_rerank', 'span + rerank']];
const sum = (ds, v) => data.datasets[ds].variants[v].summary;
const flags = (ds, v, f) => data.datasets[ds].variants[v].rows.map((r) => !!r[f]);
// The origin claim and self-grade are quoted from README.md so the page never retypes them.
const origin = readme.match(/from a ([\d.]+) percent pass rate to ([\d.]+) percent/);
const grade = readme.match(/Project grade at v[\d.]+: ([\d,]*\d) of ([\d,]*\d)/);
const version = (readme.match(/Status: (v[\d.]+)/) || [])[1];
const dCases = goldenDeep.filter((c) => c.id.startsWith('d')).length;

export default function App() {
  useReveal();
  return (
    <div className="wrap">
      <MenuBar />
      <div className="glow" aria-hidden="true" />
      <Hero />
      <Playground />
      <Scorer />
      <DeepResults />
      <RealRuns />
      <Calibrator />
      <RerankExperiment />
      <CaseBrowser />
      <Taxonomy />
      <Limits />
      <Reproduce />
      <Dock />
      <footer>
        Data: SQuAD and HotpotQA samples (CC BY-SA 4.0) and synthetic sets written for this project. Code: Apache-2.0. Every number on this page is read from the repo’s result files at build time
        or computed in your browser from them; <code>npm run build</code> fails if the browser code stops reproducing the Python results.
      </footer>
    </div>
  );
}

function Hero() {
  const sq = sum('squad', 'without_rerank'), sqR = sum('squad', 'with_rerank');
  const judge = mcnemar(flags('squad', 'without_rerank', 'j'), flags('squad', 'with_rerank', 'j'));
  const diag = rerankExp.datasets.squad.reranker_diagnostics;
  const sign = binomTwoSided(diag.top1_helped_gold, diag.top1_helped_gold + diag.top1_hurt_gold);
  const tiles = [
    [`${deep.without.passed}/${deep.n} → ${deep.with.passed}/${deep.n}`, 'Deep golden set, without → with the stemmed reranker (in-distribution)', false],
    [`${deep.b11.passed_without}/${deep.b11.n} → ${deep.b11.passed_with}/${deep.b11.n}`, 'b11 class: right document, wrong passage on top', false],
    [`${baseline.threshold.toFixed(3)}`, 'Regression gate: CI fails below this Deep pass rate (baseline.json)', false],
    [`${sq.model_summary.model_judge_passed} → ${sqR.model_summary.model_judge_passed}`, `SQuAD n=${sq.n}, embedding-judge passes without → with rerank. Exact McNemar p = ${pfmt(judge.p)}`, true],
    [`${diag.top1_helped_gold} vs ${diag.top1_hurt_gold}`, `SQuAD cases where the rerank helped vs hurt the top passage. Sign test p = ${pfmt(sign)}`, true],
    [`${f3(sum('hotpotqa', 'without_rerank').mean_context_recall)}`, 'HotpotQA context recall: retrieval is the ceiling', true],
  ];
  return (
    <header className="card hero window" id="top" data-title="rag-eval-harness — README">
      <div className="head">
        <p className="eyebrow">Research lab · stdlib Python{version ? ` · ${version}` : ''}</p>
        <span className="pill info">● {data.testCount} tests · gate {baseline.threshold.toFixed(3)}</span>
      </div>
      <h1>A reranker fixed every synthetic failure, then <em>barely moved real data</em>.</h1>
      <p className="sub">
        This harness scores retrieval-augmented answers with metrics you can check by hand. A stemmed reranker took the synthetic Deep set from {deep.without.passed} to {deep.with.passed} of {deep.n},
        then changed almost nothing on {sq.n} real SQuAD and {sum('hotpotqa', 'without_rerank').n} HotpotQA questions. The page measures both, puts uncertainty on every comparison, and lets you rerun the pipeline and the scorer in your browser.
      </p>
      <div className="actions">
        <a className="btn primary" href="#playground">Open the BM25 playground</a>
        <a className="btn ghost" href="#limits">Read the limits first</a>
        <span className="hint">Reproduce with <code>python -m pytest</code></span>
      </div>
      <div className="tiles t3">
        {tiles.map(([num, cap, real]) => (
          <div className="tile" key={cap}><Kind real={real} /><div className="num">{num}</div><div className="cap">{cap}</div></div>
        ))}
      </div>
      <p className="hint claim">
        Self-reported, unverified: the README says the project is the public version of a private pipeline that went from {origin ? `${origin[1]}% to ${origin[2]}%` : 'a lower to a higher pass rate'}.
        Nothing in this repo proves that. The project self-grade{grade ? ` (${grade[1]} of ${grade[2]})` : ''} is self-assessed too. The {deep.with.passed}/{deep.n} is synthetic and in-distribution: {dCases} of the b11 cases were written after the failure was seen.
      </p>
    </header>
  );
}

function DeepResults() {
  const metrics = [['Pass rate', 'pass_rate'], ['Faithfulness', 'mean_faithfulness'], ['Context recall', 'mean_context_recall'], ['Answer relevance', 'mean_answer_relevance']];
  const W = 560, rowH = 54, H = metrics.length * rowH + 26, l = 130, r = 52;
  const x = (v) => l + v * (W - l - r);
  const j = deep.judge;
  const abl = Object.entries(ablation.synthetic_deep);
  return (
    <section id="deep" className="card window reveal" data-title="deep_results.svg — synthetic">
      <div className="head">
        <div>
          <p className="eyebrow">Recorded run · <Kind /></p>
          <h2>On its own test set, the reranker <em>clears every case</em>.</h2>
          <p className="sub">
            {deep.n} synthetic questions over a {corpusDeep.length}-document library corpus, scored with and without the reranker (<a href={blob('level-3-deep/results_deep.json')}>results_deep.json</a>).
            Read it as a confirmation, not a generalisation: the {dCases} d-cases in the b11 class were written to target the failure after it was seen.
          </p>
        </div>
        <Recorded />
      </div>
      <div className="grid2">
        <div>
          <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Deep set metrics without and with rerank, paired bars">
            {[0, 0.5, 1].map((t) => <g key={t}><line className="axis" x1={x(t)} x2={x(t)} y1={0} y2={H - 20} /><text x={x(t)} y={H - 6} textAnchor="middle">{t}</text></g>)}
            {metrics.map(([lab, k], i) => (
              <g key={k} transform={`translate(0 ${i * rowH + 8})`}>
                <text x={0} y={22} style={{ fill: 'var(--text)', fontSize: 13 }}>{lab}</text>
                <rect x={l} y={4} width={x(deep.without[k]) - l} height={16} rx="4" fill="var(--muted)" opacity="0.55" />
                <text x={x(deep.without[k]) + 6} y={16}>{f3(deep.without[k])}</text>
                <rect x={l} y={24} width={x(deep.with[k]) - l} height={16} rx="4" fill="var(--primary)" />
                <text x={x(deep.with[k]) + 6} y={36}>{f3(deep.with[k])}</text>
              </g>
            ))}
          </svg>
          <div className="legend"><span><i style={{ background: 'var(--muted)', opacity: 0.55 }} />BM25 only</span><span><i style={{ background: 'var(--primary)' }} />BM25 + rerank</span></div>
          <h3 style={{ marginTop: 18 }}>Judge budget accounting</h3>
          <p className="hint">The budgeted judge (a local lexical proxy, not an LLM) made {j.calls_made} calls under its cap, skipped {j.calls_skipped}, spent {j.total_cost} cost units, and passed {j.judged_passed} of {j.judged} judged cases.</p>
        </div>
        <div>
          <h3>Ablation: which part does the work? <Recorded /></h3>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead><tr><th>Variant (<a href={blob('level-3-deep/ablation.py')}>ablation.py</a>)</th><th>Passed / {deep.n}</th><th>b11 / {deep.b11.n}</th></tr></thead>
              <tbody>
                {abl.map(([name, s]) => (
                  <tr key={name} className={name === 'shipped' ? 'sel' : ''}><td className="mono">{name}</td><td className={s.passed === deep.n ? 'ok' : ''}>{s.passed}</td><td className={s.b11_passed === deep.b11.n ? 'ok' : ''}>{s.b11_passed}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="hint">
            Dropping the plural -s rule alone takes the set back to {ablation.synthetic_deep.drop_rule_s.passed}/{deep.n}; no stemming gives {ablation.synthetic_deep.no_stemming.passed}. The F1 key is not needed:
            coverage then BM25 also reaches {ablation.synthetic_deep.key_coverage_bm25.passed}/{deep.n}. Try any of these in the playground; the build checks the port against this table.
          </p>
        </div>
      </div>
    </section>
  );
}

function RealRuns() {
  const [metric, setMetric] = useState('j');
  const M = { p: ['Lexical pass', 'passed'], j: ['Judge pass', null], t: ['Top-1 contains gold', 'top1_contains_gold'], r: ['Context recall', 'mean_context_recall'] };
  const value = (ds, v) => {
    const s = sum(ds, v);
    if (metric === 'r') return { rate: s.mean_context_recall, k: null };
    const k = metric === 'j' ? s.model_summary.model_judge_passed : s[M[metric][1]];
    return { rate: k / s.n, k, ci: wilson(k, s.n) };
  };
  const W = 440, H = 250, pad = { l: 36, r: 8, t: 22, b: 44 };
  const tests = [];
  for (const ds of Object.keys(DS)) for (const [mode, a, b] of [['sentence', 'without_rerank', 'with_rerank'], ['span', 'span_without_rerank', 'span_with_rerank']])
    for (const [key, f] of [['Lexical pass', 'p'], ['Judge pass', 'j'], ['Top-1 contains gold', 't']]) tests.push({ ds, mode, key, ...mcnemar(flags(ds, a, f), flags(ds, b, f)) });
  const bonf = 0.05 / tests.length;
  const nominal = tests.filter((t) => t.p < 0.05);
  const modeTests = Object.keys(DS).map((ds) => ({ ds, ...mcnemar(flags(ds, 'without_rerank', 'p'), flags(ds, 'span_without_rerank', 'p')) }));
  return (
    <section id="real" className="card window reveal" data-title="real_runs.svg — SQuAD and HotpotQA">
      <div className="head">
        <div>
          <p className="eyebrow">Recorded runs, live statistics · <Kind real /></p>
          <h2>On real questions the rerank effect is <em>inside the noise</em>.</h2>
          <p className="sub">
            Same pipeline, two public datasets, two answer modes, with and without the reranker. Bars are recorded counts from <a href={blob('real-data/results_real.json')}>results_real.json</a>;
            the 95% Wilson intervals and the paired tests are computed in your browser from the per-case flags, and checked at build time against <a href={blob('real-data/results_paired_stats.json')}>results_paired_stats.json</a>.
          </p>
        </div>
        <Seg label="Metric" value={metric} onChange={setMetric} options={Object.entries(M).map(([k, [l]]) => [k, l])} />
      </div>
      <div className="grid2">
        {Object.entries(DS).map(([ds, name]) => {
          const bw = (W - pad.l - pad.r) / 4;
          const y = (v) => pad.t + (1 - v) * (H - pad.t - pad.b);
          return (
            <div key={ds}>
              <h3>{name} · n = {sum(ds, 'without_rerank').n}</h3>
              <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${name}: ${M[metric][0]} for four variants with 95% intervals`}>
                {[0, 0.25, 0.5, 0.75, 1].map((t) => <g key={t}><line className="axis" x1={pad.l} x2={W - pad.r} y1={y(t)} y2={y(t)} /><text x={pad.l - 6} y={y(t) + 4} textAnchor="end">{t}</text></g>)}
                {VARIANTS.map(([v, lab], i) => {
                  const { rate, k, ci } = value(ds, v);
                  const cx = pad.l + i * bw + bw / 2;
                  return (
                    <g key={v}>
                      <rect x={cx - bw * 0.32} y={y(rate)} width={bw * 0.64} height={y(0) - y(rate)} rx="5" fill={v.includes('with_') ? 'var(--primary)' : 'var(--muted)'} opacity={v.includes('with_') ? 1 : 0.55} />
                      {ci && <><line x1={cx} x2={cx} y1={y(ci[1])} y2={y(ci[0])} stroke="var(--text)" strokeWidth="1.5" /><line x1={cx - 6} x2={cx + 6} y1={y(ci[1])} y2={y(ci[1])} stroke="var(--text)" /><line x1={cx - 6} x2={cx + 6} y1={y(ci[0])} y2={y(ci[0])} stroke="var(--text)" /></>}
                      <text x={cx} y={Math.min(y(ci ? ci[1] : rate), y(rate)) - 6} textAnchor="middle" style={{ fill: 'var(--text)' }}>{k != null ? k : f3(rate)}</text>
                      <text x={cx} y={H - 26} textAnchor="middle">{lab.split(' + ')[0]}</text>
                      <text x={cx} y={H - 12} textAnchor="middle">{lab.includes('+') ? '+ rerank' : 'no rerank'}</text>
                    </g>
                  );
                })}
              </svg>
            </div>
          );
        })}
      </div>
      <p className="hint">{metric === 'r' ? 'Context recall is a mean over cases, so no interval is drawn; it is the same in both answer modes because retrieval does not change.' : 'Whiskers: Wilson 95% interval. Labels: cases passed.'}</p>
      <h3 style={{ marginTop: 18 }}>Paired tests: with vs without rerank <Live /></h3>
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead><tr><th>Dataset</th><th>Mode</th><th>Outcome</th><th>Only without</th><th>Only with</th><th>Exact McNemar p</th></tr></thead>
          <tbody>
            {tests.map((t) => (
              <tr key={`${t.ds}${t.mode}${t.key}`}><td>{DS[t.ds]}</td><td>{t.mode}</td><td>{t.key}</td><td>{t.aOnly}</td><td>{t.bOnly}</td><td className={t.p < bonf ? 'ok' : ''}>{pfmt(t.p)}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="hint">
        {tests.length} tests. {nominal.length ? `${nominal.length} ${nominal.length === 1 ? 'falls' : 'fall'} under p = 0.05 (${nominal.map((t) => `${DS[t.ds]} ${t.mode} ${t.key.toLowerCase()}, p = ${pfmt(t.p)}`).join('; ')}), ` : 'None falls under p = 0.05, '}
        {tests.filter((t) => t.p < bonf).length === 0 ? `and none survives a Bonferroni correction (p < ${bonf.toFixed(4)}).` : `and ${tests.filter((t) => t.p < bonf).length} survive a Bonferroni correction (p < ${bonf.toFixed(4)}).`}
        {' '}By contrast, span answers beat sentence answers on lexical pass with p {modeTests.map((t) => `${pfmt(t.p)} (${DS[t.ds]}, ${t.aOnly} vs ${t.bOnly})`).join(' and ')}: that change is real, the rerank change is not distinguishable from zero.
      </p>
    </section>
  );
}

function RerankExperiment() {
  const [ds, setDs] = useState('squad');
  const vs = Object.entries(rerankExp.datasets[ds].variants);
  const diag = rerankExp.datasets[ds].reranker_diagnostics;
  const p = binomTwoSided(diag.top1_helped_gold, diag.top1_helped_gold + diag.top1_hurt_gold);
  const W = 460, rowH = 26, H = vs.length * rowH + 24, l = 128, r = 56;
  const x = (v) => l + v * (W - l - r);
  const real = ablation.real_top1_contains_gold;
  return (
    <section id="rerank" className="card window reveal" data-title="rerank_experiment.json — negative result">
      <div className="head">
        <div>
          <p className="eyebrow">Recorded experiment · <Kind real /></p>
          <h2>Candidate fixes were tried. <em>None helped both datasets.</em></h2>
          <p className="sub">
            The v1.2 transfer test (<a href={blob('real-data/rerank_experiment.py')}>rerank_experiment.py</a>) tried larger candidate pools and hybrid BM25 plus coverage keys (variant names below). Only the top passage feeds the answer,
            so the share of cases whose top passage contains the gold answer is the direct measure.
          </p>
        </div>
        <Seg label="Dataset" value={ds} onChange={setDs} options={Object.entries(DS)} />
      </div>
      <div className="grid2">
        <div>
          <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${DS[ds]}: top-1 contains gold rate by rerank variant`}>
            {[0, 0.25, 0.5, 0.75].map((t) => <g key={t}><line className="axis" x1={x(t)} x2={x(t)} y1={0} y2={H - 20} /><text x={x(t)} y={H - 6} textAnchor="middle">{t}</text></g>)}
            {vs.map(([name, m], i) => (
              <g key={name} transform={`translate(0 ${i * rowH})`}>
                <text x={0} y={16} style={{ fill: 'var(--text)', fontSize: 12 }}>{name}</text>
                <rect x={l} y={5} width={x(m.top1_contains_gold_rate) - l} height={14} rx="4" fill={name === 'bm25' ? 'var(--muted)' : name === 'current' ? 'var(--primary)' : 'var(--warn)'} opacity={name === 'bm25' ? 0.55 : 0.9} />
                <text x={x(m.top1_contains_gold_rate) + 6} y={16}>{m.top1_contains_gold}/{m.n}</text>
              </g>
            ))}
          </svg>
          <div style={{ overflowX: 'auto', marginTop: 10 }}>
            <table>
              <thead><tr><th>Variant</th><th>Recall</th><th>Lexical pass</th><th>Relevance</th></tr></thead>
              <tbody>{vs.map(([name, m]) => <tr key={name}><td className="mono">{name}</td><td>{f3(m.mean_context_recall)}</td><td>{m.passed}/{m.n}</td><td>{f3(m.mean_answer_relevance)}</td></tr>)}</tbody>
            </table>
          </div>
        </div>
        <div>
          <h3>Did the shipped reranker help? <Live>sign test, live</Live></h3>
          <div className="tiles" style={{ gridTemplateColumns: '1fr 1fr', marginTop: 10 }}>
            <div className="tile"><div className="num">{diag.top1_changed}</div><div className="cap">cases where it changed the top passage</div></div>
            <div className="tile"><div className="num">{diag.top1_helped_gold} / {diag.top1_hurt_gold}</div><div className="cap">helped / hurt gold containment</div></div>
            <div className="tile"><div className="num">{pfmt(p)}</div><div className="cap">exact two-sided sign test p</div></div>
            <div className="tile"><div className="num">{diag.mean_promoted_passage_tokens} / {diag.mean_demoted_passage_tokens}</div><div className="cap">mean tokens, promoted / demoted passage</div></div>
          </div>
          <p className="hint">
            {p >= 0.05
              ? `With ${diag.top1_helped_gold} helped and ${diag.top1_hurt_gold} hurt, a fair coin would split at least this unevenly ${pct(p, 0)} of the time. “No transfer” is the honest reading: the effect cannot be told apart from zero.`
              : `p < 0.05 here, but the effect is small in absolute terms and this is one of several tests.`}
          </p>
          <h3 style={{ marginTop: 16 }}>Ablation on real samples <Recorded /></h3>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead><tr><th>Variant</th><th>SQuAD top-1 / {real.squad.n}</th><th>HotpotQA top-1 / {real.hotpotqa.n}</th></tr></thead>
              <tbody>{Object.keys(ablation.variants).map((k) => <tr key={k} className={k === 'shipped' ? 'sel' : ''}><td className="mono">{k}</td><td>{real.squad[k]}</td><td>{real.hotpotqa[k]}</td></tr>)}</tbody>
            </table>
          </div>
          <p className="hint">Coverage then BM25 (no F1) puts gold on top in {real.squad.key_coverage_bm25} SQuAD cases against {real.squad.shipped} for the shipped key; F1-first keys fall to {real.squad.key_f1_bm25}. A future reranker should start without the F1 key and be tested on held-out data.</p>
        </div>
      </div>
    </section>
  );
}

function Taxonomy() {
  const t = deep.taxonomy;
  const bars = [...Object.entries(t.rag_counts).map(([k, v]) => [k, v, 'RAG']), ...Object.entries(t.agent_counts).map(([k, v]) => [k, v, 'agent'])];
  const max = Math.max(...bars.map((b) => b[1]));
  return (
    <section id="taxonomy" className="card window reveal" data-title="failure_taxonomy">
      <div className="head">
        <div>
          <p className="eyebrow">Recorded · <Kind /></p>
          <h2>One primary label per failure, so <em>counts add up</em>.</h2>
          <p className="sub">
            RAG labels come from the without-rerank Deep run ({t.rag_failed} failures). Agent labels come from {deep.agent_tasks} tasks run by {Object.keys(deep.agent_summaries).length} scripted toy agents: they show the scorer catching each failure class, not real agent behaviour.
          </p>
        </div>
        <Recorded />
      </div>
      <div className="grid2">
        <div className="bars">
          {bars.map(([k, v, kind]) => (
            <div className="bar-row" key={k}>
              <div className="lab"><span><span className="mono">{k}</span> <span className="hint">({kind})</span></span><b>{v}</b></div>
              <div className="track"><div className="fill" style={{ width: `${(v / max) * 100}%`, background: kind === 'RAG' ? 'var(--primary)' : 'var(--warn)' }} /></div>
            </div>
          ))}
          <p className="hint">{t.total_labelled} labels for {t.total_failed} failures.</p>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead><tr><th>Toy demo agent</th><th>Success</th><th>Mean steps</th><th>Mean cost</th></tr></thead>
            <tbody>{Object.entries(deep.agent_summaries).map(([k, a]) => <tr key={k}><td className="mono">{k}</td><td className={a.success_rate === 1 ? 'ok' : 'no'}>{pct(a.success_rate, 0)}</td><td>{a.mean_steps.toFixed(1)}</td><td>{a.mean_cost.toFixed(1)}</td></tr>)}</tbody>
          </table>
        </div>
      </div>
      <ul className="refs" style={{ marginTop: 16 }}>
        <li><span className="mono">hallucination</span>: faithfulness below its pass line; the answer says things the context does not support.</li>
        <li><span className="mono">retrieval_miss</span>: context recall below its pass line; the needed fact was not retrieved.</li>
        <li><span className="mono">wrong_passage_on_top</span>: recall and faithfulness pass but relevance fails; the right document came back with the wrong sentence first (the b11 class).</li>
        <li><span className="mono">wrong_or_incomplete_answer</span>: relevance fails for any other reason.</li>
        <li>Agent classes: <span className="mono">loop_trap</span>, <span className="mono">tool_misuse</span>, <span className="mono">excess_steps</span>, <span className="mono">silent_wrong_answer</span>. Definitions in <a href={blob('level-3-deep/taxonomy.py')}>taxonomy.py</a>.</li>
      </ul>
      <h3 style={{ marginTop: 18 }}>Real-data label counts (lexical labels, several per case allowed) <Kind real /></h3>
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead><tr><th>Dataset</th><th>Run</th><th>retrieval_miss</th><th>wrong_or_incomplete_answer</th><th>n</th></tr></thead>
          <tbody>{Object.keys(DS).flatMap((ds) => VARIANTS.map(([v, lab]) => <tr key={ds + v}><td>{DS[ds]}</td><td>{lab}</td><td>{sum(ds, v).label_counts.retrieval_miss ?? 0}</td><td>{sum(ds, v).label_counts.wrong_or_incomplete_answer ?? 0}</td><td>{sum(ds, v).n}</td></tr>))}</tbody>
        </table>
      </div>
    </section>
  );
}

function Limits() {
  const sq = sum('squad', 'without_rerank'), hp = sum('hotpotqa', 'without_rerank');
  const items = [
    ['Synthetic sets confirm, they do not generalise', `The ${deep.n}-case Deep set and its b11 class were written by the author; ${dCases} cases were added after the failure was seen. Real data shows no transfer.`],
    ['The lexical metric is not valid on real data', `SQuAD sentence answers pass lexically in ${sq.passed} of ${sq.n} cases, yet the top passage holds the gold answer in ${sq.top1_contains_gold}. Token F1 against short gold spans measures verbosity, not correctness. No human-label validity study exists.`],
    ['The embedding judge is not an LLM judge', `It is ${data.judgeModel}, a small static embedding model, run once on CPU and recorded. Its calibration uses a proxy built from gold strings and the same lexical metric, so it is partly circular. No human agreement study.`],
    [`Faithfulness is ${f3(sq.mean_faithfulness)} by construction`, 'Answers are extracted from retrieved passages, so the hallucination check is never exercised on real data. A generative answer step is needed to test it.'],
    ['Samples, not full splits', `${sq.n} SQuAD and ${hp.n} HotpotQA validation questions (sampling rule in DATASETS.md). Intervals on this page are for these samples.`],
    ['Retrieval is the ceiling, and no dense baseline exists', `HotpotQA context recall is ${f3(hp.mean_context_recall)} on a two-fact dataset. BM25 is the only retriever; no dense or hybrid-embedding baseline has been run.`],
    ['No external reference point', 'No comparison against Ragas or a reference BM25 implementation on the same samples.'],
    ['Many tests, small effects', 'The paired tests on this page are uncorrected for multiplicity except where Bonferroni is stated. Treat single p-values near 0.05 as leads, not findings.'],
  ];
  return (
    <section id="limits" className="card window reveal" data-title="LIMITS.md">
      <p className="eyebrow">Threats to validity</p>
      <h2>What this harness <em>cannot</em> tell you yet.</h2>
      <p className="sub">Drawn from the deductions in <a href={blob('DOSSIER.md')}>DOSSIER.md</a> and the gaps graded in <a href={blob('docs/research-review.md')}>docs/research-review.md</a>, which also names the compute or data each open gap needs.</p>
      <div className="grid2" style={{ marginTop: 16 }}>
        {items.map(([t, d]) => (
          <div className="tile" key={t}>
            <h3>{t}</h3>
            <p className="hint" style={{ margin: '6px 0 0', fontSize: 13 }}>{d}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

const REFERENCES = [
  ['Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks, NeurIPS 2020', 'https://arxiv.org/abs/2005.11401'],
  ['Es et al., Ragas: Automated Evaluation of Retrieval Augmented Generation, 2023', 'https://arxiv.org/abs/2309.15217'],
  ['Robertson and Zaragoza, The Probabilistic Relevance Framework: BM25 and Beyond, 2009', 'https://doi.org/10.1561/1500000019'],
  ['Liu et al., Lost in the Middle: How Language Models Use Long Contexts, TACL 2024', 'https://arxiv.org/abs/2307.03172'],
  ['Karpukhin et al., Dense Passage Retrieval for Open-Domain Question Answering, EMNLP 2020', 'https://arxiv.org/abs/2004.04906'],
  ['Reimers and Gurevych, Sentence-BERT, EMNLP 2019', 'https://arxiv.org/abs/1908.10084'],
  ['Rajpurkar et al., SQuAD: 100,000+ Questions for Machine Comprehension of Text, EMNLP 2016', 'https://arxiv.org/abs/1606.05250'],
  ['Yang et al., HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering, EMNLP 2018', 'https://arxiv.org/abs/1809.09600'],
  ['McNemar, Note on the sampling error of the difference between correlated proportions, Psychometrika 1947', 'https://doi.org/10.1007/BF02295996'],
  ['Wilson, Probable inference, the law of succession, and statistical inference, JASA 1927', 'https://doi.org/10.1080/01621459.1927.10502953'],
];

function Reproduce() {
  const cmds = [
    ['Deep run, before and after rerank', 'python level-3-deep/run_deep.py'],
    ['Regression gate (fails below the baseline)', 'python level-3-deep/regression_gate.py'],
    ['Reranker ablation (new)', 'python level-3-deep/ablation.py'],
    ['Paired statistics and 2-D judge sweep (new)', 'python real-data/paired_stats.py'],
    ['Real runs (needs the optional model2vec judge)', 'python real-data/run_real_eval.py'],
    [`All ${data.testCount} tests`, 'python -m pytest'],
  ];
  const docs = [
    ['SPEC.md', 'Spec', 'Scope and acceptance criteria'], ['DOSSIER.md', 'Dossier', 'History, grade and deductions'], ['docs/research-review.md', 'Research review', 'Rubric grade, fixed and open gaps'],
    ['real-data/DATASETS.md', 'Datasets', 'Sources, licences, sampling'], ['model-metrics/README.md', 'Model judge', 'Embedding judge and calibration'], ['NOVELTY.md', 'Novelty', 'Claims and their status'],
  ];
  return (
    <section id="reproduce" className="card window reveal" data-title="Terminal — reproduce">
      <p className="eyebrow">Reproduce it</p>
      <h2>Standard-library Python. <em>No keys, no GPU.</em></h2>
      <ol className="steps" style={{ marginTop: 16 }}>
        <li><span className="n">1</span><div><b>Clone</b><div className="hint"><code>git clone {REPO}.git && cd rag-eval-harness</code></div></div></li>
        {cmds.map(([t, c], i) => <li key={c}><span className="n">{i + 2}</span><div><b>{t}</b><div className="hint"><code>{c}</code></div></div></li>)}
      </ol>
      <p className="hint" style={{ marginTop: 14 }}>Sampling rule for the real runs: {data.method.split('Samples: ')[1] || data.method}</p>
      <div className="docs" style={{ marginTop: 20 }}>
        {docs.map(([p, t, d]) => <a key={p} href={blob(p)}><b>{t}</b><small>{d}</small></a>)}
      </div>
      <h3 style={{ marginTop: 22 }}>References</h3>
      <ul className="refs">{REFERENCES.map(([t, u]) => <li key={u}><a href={u}>{t}</a></li>)}</ul>
      <p className="hint">The previous React results lab is kept as source in <a href={`${REPO}/tree/main/web`}>web/</a>; every feature it had (per-case drill down, live evaluator, references, docs) is on this page.</p>
    </section>
  );
}
