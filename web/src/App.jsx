import { useMemo, useState } from 'react'
import data from './data/site-data.json'
import { Bar, MetricBars, BeforeAfter } from './charts.jsx'
import {
  scoreCase,
  PASS_FAITHFULNESS,
  PASS_RECALL,
  PASS_RELEVANCE,
} from './metrics.js'

const REPO = 'https://github.com/JesunAhmadUshno/rag-eval-harness'
const pct = (x) => `${(x * 100).toFixed(1)}%`

function Header() {
  return (
    <header className="site-header">
      <div className="wrap">
        <a className="brand" href="#top">
          rag-eval-harness <span>v1.1</span>
        </a>
        <nav className="main-nav">
          <a href="#overview">Overview</a>
          <a href="#lab">Results Lab</a>
          <a href="#simulation">Simulation</a>
          <a href="#data">Data</a>
          <a href="#research">Research</a>
          <a href="#docs">Documentation</a>
          <a href="#prototypes">Prototypes</a>
          <a href={REPO}>GitHub</a>
        </nav>
      </div>
    </header>
  )
}

function Overview() {
  const deep = data.deep
  const squad = data.real.squad.with_rerank
  return (
    <section className="hero" id="overview">
      <h1>Measure a RAG system. Do not admire it.</h1>
      <p>
        rag-eval-harness is an open evaluation harness for retrieval
        augmented generation. It retrieves with BM25, answers by
        extraction, and scores every answer three ways: lexical metrics
        you can check by hand, a failure taxonomy that names what went
        wrong, and an embedding judge that runs a real model on CPU.
        Every number on this page comes from a result file in the repo.
      </p>
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">
            {pct(deep.without.pass_rate)} to {pct(deep.with.pass_rate)}
          </div>
          <div className="stat-label">
            Deep set pass rate after the reranker fix
            <span className="tag synthetic">SYNTHETIC</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{pct(squad.mean_context_recall)}</div>
          <div className="stat-label">
            Context recall at top 5 on real SQuAD questions
            <span className="tag real">REAL DATA</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {squad.model_summary.model_judge_passed} of {squad.n}
          </div>
          <div className="stat-label">
            Real SQuAD cases passed by the embedding judge, against 1 of{' '}
            {squad.n} by the lexical pass rule. The gap is the measured
            size of the metric mismatch (full sentence answers, short
            span golds).
            <span className="tag real">REAL DATA</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-value">52 tests</div>
          <div className="stat-label">
            Unit tests across Learn, Build, Deep, the embedding judge,
            and the real data path. CI runs them on Python 3.11 and 3.12.
          </div>
        </div>
      </div>
      <p className="lede">
        Synthetic and real results are always labelled and never mixed.
        Where a number is weak, this page says so and names the fix.
      </p>
    </section>
  )
}

function ResultsLab() {
  const deep = data.deep
  const real = data.real
  const tax = deep.taxonomy
  return (
    <section className="block" id="lab">
      <h2>Results Lab</h2>
      <p className="lede">
        Two kinds of evidence. Synthetic sets are written by the project
        to probe named failure classes. Real sets are public datasets
        with human gold answers. The harness treats them the same; this
        page never blends their numbers.
      </p>

      <h3 style={{ color: 'var(--text-h)' }}>
        Synthetic Deep set, 32 cases <span className="tag synthetic">SYNTHETIC</span>
      </h3>
      <div className="chart-grid">
        <MetricBars
          title="Mean metrics, no rerank vs rerank"
          rows={[
            { label: 'Pass rate, no rerank', value: deep.without.pass_rate, color: '#8b949e' },
            { label: 'Pass rate, rerank', value: deep.with.pass_rate, color: '#3fb950' },
            { label: 'Relevance, no rerank', value: deep.without.mean_answer_relevance, color: '#8b949e' },
            { label: 'Relevance, rerank', value: deep.with.mean_answer_relevance, color: '#3fb950' },
          ]}
        />
        <BeforeAfter
          title="The b11 class: right document, wrong passage on top (13 cases)"
          before={deep.b11.passed_without}
          after={deep.b11.passed_with}
          max={deep.b11.n}
        />
        <MetricBars
          title="Failure taxonomy counts on the Deep runs"
          rows={[
            { label: 'Wrong passage on top', value: tax.rag_counts.wrong_passage_on_top, max: 32, color: '#d29922' },
            { label: 'Agent loop traps (demo)', value: tax.agent_counts.loop_trap, max: 32, color: '#8b949e' },
            { label: 'Agent tool misuse (demo)', value: tax.agent_counts.tool_misuse, max: 32, color: '#8b949e' },
            { label: 'Agent silent wrong answers (demo)', value: tax.agent_counts.silent_wrong_answer, max: 32, color: '#8b949e' },
          ]}
        />
      </div>

      <h3 style={{ color: 'var(--text-h)' }}>
        Real data <span className="tag real">REAL DATA</span>
      </h3>
      <div className="chart-grid">
        {Object.entries(real).map(([name, variants]) => (
          <MetricBars
            key={name}
            title={`${name === 'squad' ? 'SQuAD' : 'HotpotQA'} sample, ${variants.with_rerank.n} cases`}
            rows={[
              { label: 'Lexical pass, no rerank', value: variants.without_rerank.pass_rate, color: '#8b949e' },
              { label: 'Lexical pass, rerank', value: variants.with_rerank.pass_rate, color: '#f85149' },
              { label: 'Context recall', value: variants.with_rerank.mean_context_recall, color: '#4cc2ff' },
              { label: 'Answer relevance (F1)', value: variants.with_rerank.mean_answer_relevance, color: '#d29922' },
              { label: 'Model judge pass', value: variants.with_rerank.model_summary.model_judge_pass_rate, color: '#3fb950' },
            ]}
          />
        ))}
        <div className="chart-card">
          <h4>Failure labels on real runs (reranked)</h4>
          {Object.entries(real).map(([name, variants]) => (
            <div key={name}>
              <p style={{ margin: '8px 0 2px', color: 'var(--muted)' }}>
                {name === 'squad' ? 'SQuAD' : 'HotpotQA'}
              </p>
              {Object.entries(variants.with_rerank.label_counts).map(
                ([label, count]) => (
                  <Bar
                    key={label}
                    label={label}
                    value={count}
                    max={variants.with_rerank.n}
                    color="#f85149"
                  />
                )
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>What the analysis says</h3>
        <ul className="tight">
          <li>
            Retrieval is the stronger half. On real SQuAD questions the
            gold fact is in the top 5 passages 83 percent of the time.
            Multi-hop HotpotQA recall is 52 percent, because a case needs
            two facts and the top 5 often holds only one.
          </li>
          <li>
            The answer step is the weak half. The pipeline answers with a
            whole sentence while gold answers are short spans, so token
            F1 is low even when the sentence is right. The embedding
            judge passes about half the SQuAD cases. The difference
            between the two judges is a measurement, not an excuse.
          </li>
          <li>
            The reranker does not transfer. It took the synthetic b11
            class from 5 of 13 to 13 of 13, and on real data it changes
            almost nothing. A fix proven only on synthetic data is a
            hypothesis. This run is the test, and the result is recorded
            either way.
          </li>
          <li>
            Faithfulness reads 1.000 everywhere. That is by construction:
            an extractive answer is copied from the context. It is not
            claimed as a quality win anywhere in this project.
          </li>
          <li>
            Named next fix: span extraction, answering with the short
            span instead of the whole sentence. It is item 1 of the
            v1.2 backlog in the repo ROADMAP.
          </li>
        </ul>
      </div>
    </section>
  )
}

function Simulation() {
  const cases = data.sim_cases
  const [picked, setPicked] = useState('case:0')
  const [form, setForm] = useState({
    question: cases[0].question || '',
    answer: cases[0].answer,
    contexts: cases[0].contexts.join('\n'),
    gold_answer: cases[0].gold_answer,
    gold_facts: cases[0].gold_facts.join('\n'),
  })

  const pick = (value) => {
    setPicked(value)
    if (value.startsWith('case:')) {
      const c = cases[Number(value.slice(5))]
      setForm({
        question: c.question || '',
        answer: c.answer,
        contexts: c.contexts.join('\n'),
        gold_answer: c.gold_answer,
        gold_facts: c.gold_facts.join('\n'),
      })
    }
  }

  const scores = useMemo(
    () =>
      scoreCase({
        answer: form.answer,
        contexts: form.contexts.split('\n').filter((s) => s.trim()),
        gold_answer: form.gold_answer,
        gold_facts: form.gold_facts.split('\n').filter((s) => s.trim()),
      }),
    [form]
  )

  const set = (key) => (e) => {
    setPicked('custom')
    setForm({ ...form, [key]: e.target.value })
  }

  return (
    <section className="block" id="simulation">
      <h2>Simulation</h2>
      <p className="lede">
        The Level 1 lexical evaluator, ported to JavaScript line for
        line from <code>level-1-learn/rag_eval.py</code>, running live in
        your browser. Pick a recorded case or paste your own. Edit the
        answer and watch the scores move. The embedding judge needs the
        Python model, so it is not part of this in-browser run.
      </p>
      <div className="sim-grid" style={{ marginTop: 16 }}>
        <div className="card" style={{ margin: 0 }}>
          <label>Recorded case</label>
          <select value={picked} onChange={(e) => pick(e.target.value)}>
            {cases.map((c, i) => (
              <option key={c.id} value={`case:${i}`}>
                {c.id} ({c.kind})
              </option>
            ))}
            <option value="custom">Your own text (edited)</option>
          </select>
          <label>Question (shown for context; the lexical metrics do not use it)</label>
          <textarea rows={2} value={form.question} onChange={set('question')} />
          <label>System answer</label>
          <textarea rows={3} value={form.answer} onChange={set('answer')} />
          <label>Retrieved context passages, one per line</label>
          <textarea rows={5} value={form.contexts} onChange={set('contexts')} />
          <label>Gold answer</label>
          <textarea rows={2} value={form.gold_answer} onChange={set('gold_answer')} />
          <label>Gold facts, one per line</label>
          <textarea rows={3} value={form.gold_facts} onChange={set('gold_facts')} />
        </div>
        <div className="card" style={{ margin: 0 }}>
          <h3>Scores, computed now</h3>
          <div className="score-line">
            <span>Faithfulness (pass at {PASS_FAITHFULNESS})</span>
            <span>{scores.faithfulness.toFixed(3)}</span>
          </div>
          <Bar label="" value={scores.faithfulness} color="#4cc2ff" />
          <div className="score-line">
            <span>Context recall (pass at {PASS_RECALL})</span>
            <span>{scores.context_recall.toFixed(3)}</span>
          </div>
          <Bar label="" value={scores.context_recall} color="#4cc2ff" />
          <div className="score-line">
            <span>Answer relevance (pass at {PASS_RELEVANCE})</span>
            <span>{scores.answer_relevance.toFixed(3)}</span>
          </div>
          <Bar label="" value={scores.answer_relevance} color="#4cc2ff" />
          <p style={{ marginTop: 14 }}>
            Verdict:{' '}
            {scores.passed ? (
              <span className="pass">PASS</span>
            ) : (
              <span className="fail">FAIL</span>
            )}
          </p>
          {scores.labels.map((l) => (
            <span key={l} className="label-chip">{l}</span>
          ))}
          <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 12 }}>
            Try this: shorten a full-sentence answer to just the gold
            span and watch answer relevance jump. That is the metric
            mismatch the Results Lab measures on real data.
          </p>
        </div>
      </div>
    </section>
  )
}

function DataSection() {
  return (
    <section className="block" id="data">
      <h2>Data</h2>
      <p className="lede">
        Real datasets are public and license checked. Synthetic sets are
        written by this project and are always labelled synthetic. Full
        record: <code>real-data/DATASETS.md</code> in the repo.
      </p>
      <table className="data">
        <thead>
          <tr>
            <th>Dataset</th>
            <th>Kind</th>
            <th>Source</th>
            <th>License</th>
            <th>Used here</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>SQuAD v1.1 (rajpurkar/squad)</td>
            <td>Real</td>
            <td>
              <a href="https://huggingface.co/datasets/rajpurkar/squad">
                Hugging Face
              </a>
            </td>
            <td>CC BY-SA 4.0</td>
            <td>
              100 validation cases (every 10th of the first 1,000 rows),
              72 context documents, 323 passages. Full set: 10,570
              validation questions.
            </td>
          </tr>
          <tr>
            <td>HotpotQA (hotpotqa/hotpot_qa, distractor)</td>
            <td>Real</td>
            <td>
              <a href="https://huggingface.co/datasets/hotpotqa/hotpot_qa">
                Hugging Face
              </a>
            </td>
            <td>CC BY-SA 4.0</td>
            <td>
              60 validation cases, 591 context documents, 2,572 passages.
              Full set: 7,405 validation questions.
            </td>
          </tr>
          <tr>
            <td>Learn golden set</td>
            <td>Synthetic</td>
            <td>Written for this project (level-1-learn/golden_set.json)</td>
            <td>Apache-2.0, part of this repo</td>
            <td>
              8 cases, 3 built to fail with named labels: hallucination,
              retrieval miss, wrong or incomplete answer.
            </td>
          </tr>
          <tr>
            <td>Build golden set and Northlight corpus</td>
            <td>Synthetic</td>
            <td>Written for this project (level-2-build/)</td>
            <td>Apache-2.0, part of this repo</td>
            <td>20 cases over a 12 document invented library corpus.</td>
          </tr>
          <tr>
            <td>Deep golden set</td>
            <td>Synthetic</td>
            <td>Written for this project (level-3-deep/)</td>
            <td>Apache-2.0, part of this repo</td>
            <td>
              32 cases over 24 documents, including the 13 case b11 class
              (right document, wrong passage on top).
            </td>
          </tr>
        </tbody>
      </table>
      <p className="lede">
        Model: the embedding judge uses minishlab/potion-base-8M through
        Model2Vec, a small static embedding model that runs on CPU. It
        is downloaded once from Hugging Face; no API key, no cost.
      </p>
    </section>
  )
}

const REFERENCES = [
  {
    title: 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks',
    authors: 'Lewis, Perez, Piktus et al.',
    venue: 'NeurIPS 2020',
    url: 'https://arxiv.org/abs/2005.11401',
    note: 'The RAG architecture this harness evaluates.',
  },
  {
    title: 'Ragas: Automated Evaluation of Retrieval Augmented Generation',
    authors: 'Es, James, Espinosa-Anke, Schockaert',
    venue: '2023, arXiv:2309.15217',
    url: 'https://arxiv.org/abs/2309.15217',
    note: 'Reference-free RAG metrics. The metric names in this harness (faithfulness, context recall, answer relevance) follow the same dimensions, implemented here in the open with lexical and embedding methods.',
  },
  {
    title: 'Lost in the Middle: How Language Models Use Long Contexts',
    authors: 'Liu, Lin, Hewitt et al.',
    venue: 'TACL 2024, arXiv:2307.03172',
    url: 'https://arxiv.org/abs/2307.03172',
    note: 'Why passage position matters; the b11 failure class (right document, wrong passage on top) is this problem at sentence scale.',
  },
  {
    title: 'The Probabilistic Relevance Framework: BM25 and Beyond',
    authors: 'Robertson and Zaragoza',
    venue: 'Foundations and Trends in Information Retrieval, 2009',
    url: 'https://doi.org/10.1561/1500000019',
    note: 'The BM25 ranking function the pipeline implements.',
  },
  {
    title: 'Dense Passage Retrieval for Open-Domain Question Answering',
    authors: 'Karpukhin et al.',
    venue: 'EMNLP 2020, arXiv:2004.04906',
    url: 'https://arxiv.org/abs/2004.04906',
    note: 'The dense retrieval alternative to BM25; the v1.2 comparison point.',
  },
  {
    title: 'Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks',
    authors: 'Reimers and Gurevych',
    venue: 'EMNLP 2019, arXiv:1908.10084',
    url: 'https://arxiv.org/abs/1908.10084',
    note: 'The embedding similarity method behind the model judge (served here by a small static Model2Vec model).',
  },
  {
    title: 'SQuAD: 100,000+ Questions for Machine Comprehension of Text',
    authors: 'Rajpurkar et al.',
    venue: 'EMNLP 2016, arXiv:1606.05250',
    url: 'https://arxiv.org/abs/1606.05250',
    note: 'One of the two real datasets in the Results Lab.',
  },
  {
    title: 'HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering',
    authors: 'Yang et al.',
    venue: 'EMNLP 2018, arXiv:1809.09600',
    url: 'https://arxiv.org/abs/1809.09600',
    note: 'The second real dataset; its supporting facts are the gold facts for context recall.',
  },
]

function Research() {
  return (
    <section className="block" id="research">
      <h2>Research</h2>
      <p className="lede">
        The methods here are not invented. Each one traces to a paper or
        a dataset paper, listed with links so any reader can check the
        source.
      </p>
      {REFERENCES.map((r) => (
        <div className="card" key={r.title}>
          <h3>
            <a href={r.url}>{r.title}</a>
          </h3>
          <p style={{ color: 'var(--muted)', fontSize: 14 }}>
            {r.authors}. {r.venue}.
          </p>
          <p>{r.note}</p>
        </div>
      ))}
    </section>
  )
}

function Docs() {
  return (
    <section className="block" id="docs">
      <h2>Documentation</h2>
      <div className="card">
        <h3>Install and run</h3>
        <pre>{`git clone https://github.com/JesunAhmadUshno/rag-eval-harness
cd rag-eval-harness
python level-1-learn/run_eval.py     # Learn golden set
python level-2-build/run_build.py    # end to end pipeline run
python level-3-deep/run_deep.py      # Deep run with the reranker
python level-3-deep/regression_gate.py
pip install model2vec                # only for the model judge
python real-data/run_real_eval.py    # real SQuAD and HotpotQA runs
python -m unittest discover -s tests # 52 tests`}</pre>
        <p>
          The core harness is Python standard library only. Model2Vec is
          the single optional dependency, used only by the embedding
          judge.
        </p>
      </div>
      <div className="card">
        <h3>The metrics, in plain words</h3>
        <ul className="tight">
          <li>
            <strong>Faithfulness:</strong> the share of answer content
            words that appear in the retrieved context. A pass needs
            0.80 or more.
          </li>
          <li>
            <strong>Context recall:</strong> the share of gold facts the
            retrieved context covers. A fact counts as covered when at
            least 80 percent of its content words appear in the context.
            A pass needs 0.80 or more.
          </li>
          <li>
            <strong>Answer relevance:</strong> token F1 between the
            system answer and the gold answer. A pass needs 0.50 or
            more. Known limit: it punishes correct answers in different
            words, and correct full sentences against short gold spans.
          </li>
          <li>
            <strong>Semantic answer similarity (model):</strong> cosine
            similarity between embeddings of the system answer and the
            gold answer, from minishlab/potion-base-8M.
          </li>
          <li>
            <strong>Semantic support (model):</strong> the best cosine
            similarity between the system answer and any one retrieved
            passage. The model judge passes a case at similarity 0.30
            and support 0.25 or more.
          </li>
        </ul>
      </div>
      <div className="card">
        <h3>Failure taxonomy</h3>
        <ul className="tight">
          <li><strong>hallucination:</strong> faithfulness below the pass line; the answer says things the context does not support.</li>
          <li><strong>retrieval_miss:</strong> context recall below the pass line; the needed fact was not retrieved.</li>
          <li><strong>wrong_or_incomplete_answer:</strong> answer relevance below the pass line; the answer does not match the gold answer.</li>
          <li><strong>wrong_passage_on_top (Deep):</strong> the right document was retrieved but the wrong passage ranked first, so the extractive answer is the wrong sentence.</li>
          <li>Agent classes (Deep, demo agents): loop_trap, tool_misuse, silent_wrong_answer, excess_steps.</li>
        </ul>
      </div>
      <div className="card">
        <h3>Roadmap</h3>
        <p>
          v1.2 backlog, in order: span extraction for short answers;
          a generative answer step behind the same metrics; dense
          retrieval next to BM25; a learned reranker compared on the
          same sets; real agent evaluation once the agent project
          exists. Full text: <code>ROADMAP.md</code> in the repo. The
          regression gate (pass rate at or above 0.900 on the Deep
          baseline) must stay green through every change.
        </p>
      </div>
    </section>
  )
}

function Prototypes() {
  const items = [
    {
      name: 'Level 1, Learn (v0.1)',
      body: 'Three lexical metrics and a seed failure taxonomy over an 8 case synthetic golden set, 5 of 8 passed by design. Proved the scoring idea is small, open, and checkable by hand.',
    },
    {
      name: 'Level 2, Build (v0.5)',
      body: 'An end to end pipeline: BM25 over sentences, extractive answers, a budgeted judge layer with a hard call cap and cost accounting. 19 of 20 synthetic cases passed. The one failure, b11, named the next problem.',
    },
    {
      name: 'Level 3, Deep (v1.0)',
      body: 'A stemmed-overlap reranker took the Deep set from 23 of 32 to 32 of 32 and the b11 class from 5 of 13 to 13 of 13, behind a CI regression gate at 0.900. Proved the fix on synthetic data, and set up the question v1.1 answers: does it hold on real data? (It does not, and the Results Lab shows the numbers.)',
    },
    {
      name: 'v1.1, the research upgrade',
      body: 'Real public datasets (SQuAD and HotpotQA samples, license checked), a model inside the evaluation path (an embedding judge on CPU), and this React lab: results, a live simulation, data provenance, references, full documentation, and the prototype history. The same honesty rules, on evidence that can prove the project wrong.',
    },
  ]
  return (
    <section className="block" id="prototypes">
      <h2>Prototypes</h2>
      <p className="lede">
        The level history of the project. Each stage shipped, was
        measured, and named what the next stage had to prove.
      </p>
      {items.map((it) => (
        <div className="card" key={it.name}>
          <h3>{it.name}</h3>
          <p>{it.body}</p>
        </div>
      ))}
    </section>
  )
}

export default function App() {
  return (
    <div id="top">
      <Header />
      <main>
        <div className="wrap">
          <Overview />
          <ResultsLab />
          <Simulation />
          <DataSection />
          <Research />
          <Docs />
          <Prototypes />
        </div>
      </main>
      <footer className="site">
        <div className="wrap">
          rag-eval-harness v1.1. Code Apache-2.0, tutorials CC BY 4.0.
          Real data samples under CC BY-SA 4.0 with attribution in the
          repo. Every number on this page traces to a result file in{' '}
          <a href={REPO}>the repository</a>. Synthetic results are
          labelled synthetic; real results are labelled real.
        </div>
      </footer>
    </div>
  )
}
