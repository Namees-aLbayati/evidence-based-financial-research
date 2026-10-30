import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import ResearchAnswer from './ResearchAnswer.jsx';
import './style.css';
import evaluation from './evaluation.json';

const examples = ["How did Apple's stock price change?", 'What is the news sentiment around Amazon?', 'Compare Apple, Amazon, and Alphabet.'];
function App() {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  async function submit(event) {
    event.preventDefault();
    if (loading || !question.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const response = await fetch('/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: question.trim() }) });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Please check your question and try again.');
      setResult(data);
    } catch (err) { setError(err instanceof TypeError ? 'Could not connect. Check that your backend is running, then try again.' : err.message); }
    finally { setLoading(false); }
  }
  return <div className="shell">
    <header><a className="brand" href="/"><span className="mark">↗</span> Financial Research<span className="tag">WORKSPACE</span></a><a href="/docs">API docs ↗</a></header>
    <main>
      <div className="intro"><p className="eyebrow">FINANCIAL EVIDENCE WORKSPACE</p><h1>From financial data<br/>to supported insights.</h1><p>Research the supplied news, historical prices, and company filings.<br/>Each report brings together retrieved evidence, available calculations, and explicit limitations.</p></div>
      <section className="workflow" aria-labelledby="workflow-title">
        <div className="workflow-heading"><h2 id="workflow-title">How your research becomes a report</h2><span>RAG → calculations → validation</span></div>
        <ol className="workflow-steps">
          <li><span className="step-number" aria-hidden="true">01</span><h3>Set the question</h3><p>Ask about a company, a historical price trend, or a comparison.</p></li>
          <li><span className="step-number" aria-hidden="true">02</span><h3>Retrieve with RAG</h3><p>Your question is matched to relevant news, price records, and filing passages in the vector index.</p></li>
          <li><span className="step-number" aria-hidden="true">03</span><h3>Generate & check</h3><p>The model receives retrieved evidence to draft an answer. Python calculates supported figures; validation checks citations and comparison coverage.</p></li>
          <li><span className="step-number" aria-hidden="true">04</span><h3>Review the report</h3><p>Read the findings, check source records, and see which parts remain unsupported.</p></li>
        </ol>
        <p className="workflow-note"><strong>RAG means Retrieval-Augmented Generation:</strong> retrieve relevant source passages, provide them as context to the model, then generate an answer tied to that evidence. The model is not trained again on your question.</p>
      </section>
      <details className="evaluation-panel">
        <summary>How the system is evaluated <span>RAG quality & answer checks</span></summary>
        <div className="evaluation-content">
          <h3>On every answer</h3><p>The pipeline checks citation labels, filters unsupported generated numerical claims, and checks evidence coverage for identified multi-company comparisons. Supported Python calculations are attached separately. Missing support can produce a partial answer or an abstention.</p>
          <h3>Offline notebook evaluation</h3><p>Recorded model-judge scores assess four dimensions. These benchmarks run separately from your questions; this app does not calculate a live judge score for each report.</p>
          <dl className="metric-definitions"><div><dt>Faithfulness</dt><dd>Does the answer stay faithful to the retrieved evidence?</dd></div><div><dt>Groundedness</dt><dd>Are the claims supported by source evidence?</dd></div><div><dt>Relevance</dt><dd>Does the answer address the question?</dd></div><div><dt>Actionability</dt><dd>Is the response useful, with clear limits and next steps?</dd></div></dl>
          <h3>Recorded results from a prior notebook run</h3>
          <div className="table-scroll"><table><thead><tr><th>Metric · score out of 1</th><th>Required questions · 5</th><th>Held-out cases · 3</th></tr></thead><tbody>{evaluation.required.map(row => <tr key={row.metric}><th>{row.metric}</th><td>{row.score.toFixed(3)}</td><td>{evaluation.held_out.find(other => other.metric === row.metric)?.score.toFixed(3)}</td></tr>)}</tbody></table></div>
          <p className="evaluation-caveat">These are model-judge estimates, not accuracy percentages or confidence scores for your current answer. The held-out cases were inspected in earlier revisions and are not a fresh independent test. Small samples do not establish general reliability. The current app has not been re-evaluated end to end against these benchmarks.</p>
          <p className="evaluation-source">Recorded source: <code>{evaluation.source}</code>. Citation checks assess structure and do not prove factual support.</p>
        </div>
      </details>
      <section className="card" aria-label="Start a research report">
        <form onSubmit={submit}><label htmlFor="question">Start your research</label><textarea id="question" placeholder="Ask about a company, price trend, or financial report…" value={question} maxLength={4000} required disabled={loading} onChange={e => setQuestion(e.target.value)} />
        <div className="form-bottom"><span>Based on your historical dataset</span><button className="primary" disabled={loading || !question.trim()} type="submit">{loading ? 'Researching…' : 'Generate report →'}</button></div></form>
        <div className="examples"><span>Try a question</span>{examples.map(text => <button key={text} type="button" disabled={loading} onClick={() => setQuestion(text)}>{text}</button>)}</div>
      </section>
      {loading && <p className="notice" role="status">Searching your sources and preparing an answer. This may take a moment.</p>}
      {error && <div className="error" role="alert">{error}</div>}
      {result && <ResearchAnswer result={result} />}
      <footer><span>Historical evidence, not live market quotes.</span><span>Review sources before making decisions. Questions may incur API charges.</span></footer>
    </main>
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
