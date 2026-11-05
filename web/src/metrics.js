// A faithful JavaScript port of level-1-learn/rag_eval.py.
// Same stopwords, same token rule, same thresholds, same labels.
// The dashboard simulation runs this code live in the browser.

const STOPWORDS = new Set(
  (
    'a an the is are was were be been of to in on for and or as at by ' +
    'it its this that these those from with without into over under'
  ).split(' ')
)

const RECALL_COVERAGE = 0.8
export const PASS_FAITHFULNESS = 0.8
export const PASS_RECALL = 0.8
export const PASS_RELEVANCE = 0.5

export function contentTokens(text) {
  return (text.toLowerCase().match(/[a-z0-9]+/g) || []).filter(
    (t) => !STOPWORDS.has(t)
  )
}

function tokenSet(text) {
  return new Set(contentTokens(text))
}

function contextTokenSet(contexts) {
  const all = new Set()
  for (const chunk of contexts) {
    for (const t of tokenSet(chunk)) all.add(t)
  }
  return all
}

export function faithfulness(answer, contexts) {
  const answerTokens = tokenSet(answer)
  if (answerTokens.size === 0) return 0
  const ctx = contextTokenSet(contexts)
  let shared = 0
  for (const t of answerTokens) if (ctx.has(t)) shared += 1
  return shared / answerTokens.size
}

export function contextRecall(contexts, goldFacts) {
  if (!goldFacts || goldFacts.length === 0) return 0
  const ctx = contextTokenSet(contexts)
  let covered = 0
  for (const fact of goldFacts) {
    const factTokens = tokenSet(fact)
    if (factTokens.size === 0) continue
    let overlap = 0
    for (const t of factTokens) if (ctx.has(t)) overlap += 1
    if (overlap / factTokens.size >= RECALL_COVERAGE) covered += 1
  }
  return covered / goldFacts.length
}

export function answerRelevance(answer, goldAnswer) {
  const a = tokenSet(answer)
  const g = tokenSet(goldAnswer)
  if (a.size === 0 || g.size === 0) return 0
  let shared = 0
  for (const t of a) if (g.has(t)) shared += 1
  if (shared === 0) return 0
  const precision = shared / a.size
  const recall = shared / g.size
  return (2 * precision * recall) / (precision + recall)
}

export function failureLabels(scores) {
  const labels = []
  if (scores.faithfulness < PASS_FAITHFULNESS) labels.push('hallucination')
  if (scores.context_recall < PASS_RECALL) labels.push('retrieval_miss')
  if (scores.answer_relevance < PASS_RELEVANCE)
    labels.push('wrong_or_incomplete_answer')
  return labels
}

export function scoreCase(kase) {
  const scores = {
    faithfulness: faithfulness(kase.answer, kase.contexts),
    context_recall: contextRecall(kase.contexts, kase.gold_facts),
    answer_relevance: answerRelevance(kase.answer, kase.gold_answer),
  }
  const labels = failureLabels(scores)
  return { ...scores, passed: labels.length === 0, labels }
}
