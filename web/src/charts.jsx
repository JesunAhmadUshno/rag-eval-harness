// Small hand-rolled SVG bar charts. No chart library: the bundle stays
// light and every bar is traceable to one recorded number.

export function Bar({ label, value, max = 1, color = '#4cc2ff', note }) {
  const pct = Math.max(0, Math.min(1, value / max))
  return (
    <div className="bar-row">
      <div className="bar-label">{label}</div>
      <div className="bar-track">
        <div
          className="bar-fill"
          style={{ width: `${pct * 100}%`, background: color }}
        />
      </div>
      <div className="bar-value">
        {max === 1 ? value.toFixed(3) : value}
        {note ? <span className="bar-note"> {note}</span> : null}
      </div>
    </div>
  )
}

export function MetricBars({ title, rows }) {
  return (
    <div className="chart-card">
      <h4>{title}</h4>
      {rows.map((r) => (
        <Bar key={r.label} {...r} />
      ))}
    </div>
  )
}

export function BeforeAfter({ title, before, after, max = 1 }) {
  return (
    <div className="chart-card">
      <h4>{title}</h4>
      <Bar label="Before" value={before} max={max} color="#8b949e" />
      <Bar label="After" value={after} max={max} color="#3fb950" />
    </div>
  )
}
