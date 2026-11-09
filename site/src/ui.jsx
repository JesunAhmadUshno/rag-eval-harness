import { useEffect, useId, useState } from 'react';

export const REPO = 'https://github.com/JesunAhmadUshno/rag-eval-harness';
export const blob = (p) => `${REPO}/blob/main/${p}`;
export const pct = (x, d = 1) => `${(x * 100).toFixed(d)}%`;
export const f3 = (x) => x.toFixed(3);
export const pfmt = (p) => (p < 0.0001 ? '< 0.0001' : p.toFixed(4));

export const SECTIONS = [
  ['top', 'Overview', '◎'], ['playground', 'BM25 playground', '⌕'], ['scorer', 'Live scorer', '✎'], ['deep', 'Deep results', '▥'],
  ['real', 'Real runs', '▤'], ['calibration', 'Judge calibration', '◐'], ['rerank', 'Rerank experiment', '⇅'],
  ['cases', 'Case browser', '☰'], ['taxonomy', 'Failure taxonomy', '⚑'], ['limits', 'Limits', '⚠'], ['reproduce', 'Reproduce', '❯_'],
];

export function useReveal() {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.08 });
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  }, []);
}

export function MenuBar() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 30000); return () => clearInterval(t); }, []);
  return (
    <div className="menubar" role="banner">
      <span className="apple" aria-hidden="true">◆</span>
      <a className="app" href="#top">RAG Eval Harness</a>
      <a className="m" href={blob('PROPOSAL.md')}>Proposal</a>
      <a className="m" href={blob('REPORT.md')}>Report</a>
      <a className="m" href={blob('CHANGELOG.md')}>Changelog</a>
      <span className="spacer" />
      <span className="status"><i /> Regression gate in CI</span>
      <a href={REPO}>GitHub ↗</a>
      <span className="clock">{now.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })}</span>
    </div>
  );
}

export function Dock() {
  const [active, setActive] = useState('top');
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setActive(e.target.id)), { rootMargin: '-45% 0px -50% 0px' });
    SECTIONS.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  }, []);
  return (
    <nav className="dock" aria-label="Sections">
      {SECTIONS.map(([id, label, icon]) => (
        <a key={id} href={`#${id}`} className={active === id ? 'on' : ''} aria-current={active === id ? 'true' : undefined} aria-label={label}>
          <span className="ico" aria-hidden="true">{icon}</span><span className="lbl">{label}</span>
        </a>
      ))}
    </nav>
  );
}

export function Range({ label, value, min, max, step, onChange, show }) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label} <span>{show}</span></label>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} />
    </div>
  );
}

export function Select({ label, value, onChange, options }) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
      </select>
    </div>
  );
}

export function Seg({ label, value, onChange, options }) {
  return (
    <div className="seg" role="group" aria-label={label}>
      {options.map(([k, l]) => <button key={String(k)} type="button" aria-pressed={value === k} onClick={() => onChange(k)}>{l}</button>)}
    </div>
  );
}

// Every tile and chart says which kind of data it shows; the two are never mixed in one chart.
export const Kind = ({ real }) => <span className={`kind ${real ? 'real' : 'syn'}`}>{real ? 'real data' : 'synthetic'}</span>;
export const Recorded = ({ children = 'recorded' }) => <span className="pill warn">● {children}</span>;
export const Live = ({ children = 'computed live' }) => <span className="pill good">● {children}</span>;
