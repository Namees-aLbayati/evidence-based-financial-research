import React from 'react';
import ReactMarkdown from 'react-markdown';

const statusText = {
  answered: ['Answer available', 'The pipeline returned an answer. Review its supporting sources and any limitations below.'],
  partial: ['Partially answered', 'Some parts of your question have supporting evidence. Other parts remain uncertain or unanswered.'],
  insufficient_evidence: ['More evidence needed', 'The retrieved evidence was not sufficient for a reliable complete answer. Available calculations and sources are shown below.']
};
const number = value => Number.isFinite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : 'Unavailable';
const percent = value => Number.isFinite(value) ? `${value > 0 ? '+' : ''}${number(value)}%` : 'Unavailable';
function safeLink(value) {
  try { const url = new URL(value); return ['http:', 'https:'].includes(url.protocol) ? url.href : null; } catch { return null; }
}
function sourceId(index) { return `research-source-${index}`; }
function citedText(text, sources) {
  return text.replace(/\[(?:news|price|filing) \d+\]/g, label => {
    const index = sources.findIndex(source => source.label === label);
    return index < 0 ? label : `[${label.slice(1, -1)}](#${sourceId(index)})`;
  });
}
export default function ResearchAnswer({ result }) {
  const sources = result.sources || [];
  const prices = sources.filter(source => ['weekly_close_change', 'three_month_close_change'].includes(source.calculation));
  const financials = sources.filter(source => source.calculation === 'quarterly_growth');
  const [title, explanation] = statusText[result.status] || statusText.insufficient_evidence;
  const limitations = result.limitations || [];
  const citations = source => <a className="citation" href={`#${sourceId(sources.indexOf(source))}`}>{source.label || 'Source'}</a>;
  return <section className="card result report" aria-labelledby="answer-title">
    <div className="result-heading"><div><p className="eyebrow">YOUR RESEARCH REPORT</p><h2 id="answer-title">Understand the answer</h2></div><span className={`badge ${result.status}`}>{title}</span></div>
    <p className="asked">{result.question}</p>
    <nav className="report-nav" aria-label="Answer sections"><a href="#overview">Overview</a>{(prices.length > 0 || financials.length > 0) && <a href="#figures">Key figures</a>}<a href="#analysis">Analysis</a><a href="#limitations">Limitations</a><a href="#sources">Sources</a></nav>
    <section id="overview" className="overview"><h3>At a glance</h3><p>{explanation}</p><div className="report-facts"><span><strong>{sources.length}</strong> source records</span><span><strong>{prices.length + financials.length}</strong> calculations</span><span><strong>{limitations.length}</strong> listed limitations</span></div></section>
    {(prices.length > 0 || financials.length > 0) && <section id="figures" className="report-section"><h3>Key figures</h3><p className="section-note">Calculated from the supplied historical data. Each card or row shows its own reporting period.</p>
      <div className="metric-grid">{prices.map((source, index) => <article className="metric-card" key={index}>
        <div className="metric-top"><strong>{source.ticker || source.company}</strong>{citations(source)}</div>
        <p className="metric-caption">Closing price change</p><p className="metric-value">{percent(source.percent_change)}</p>
        <p className="metric-dates">{source.first_date} → {source.date}</p>
        <dl><div><dt>Starting close</dt><dd>USD {number(source.first_close)}</dd></div><div><dt>Ending close</dt><dd>USD {number(source.last_close)}</dd></div><div><dt>Window low / high</dt><dd>USD {number(source.minimum_low)} / {number(source.maximum_high)}</dd></div></dl>
        {Number.isFinite(source.percent_change) && <p className="metric-reading">The closing price {source.percent_change > 0 ? 'rose' : source.percent_change < 0 ? 'fell' : 'was unchanged'} across this window. This describes the observed change; it does not explain its cause or predict the next move.</p>}
      </article>)}</div>
      {financials.length > 0 && <><h4>Company financial performance</h4><p className="section-note">Revenue and net income are in USD millions. Growth compares the reported quarter with its prior-year quarter. Different quarter ends may not be directly comparable.</p><div className="table-scroll" role="region" aria-label="Financial performance comparison" tabIndex="0"><table><thead><tr><th>Company / quarter ended</th><th>Revenue</th><th>Revenue growth</th><th>Net income</th><th>Net income growth</th><th>Evidence</th></tr></thead><tbody>{financials.map((source,index) => <tr key={index}><th>{source.company}<small>{source.period_end}</small></th><td>{number(source.revenue_current)}</td><td>{percent(source.revenue_growth_percent)}</td><td>{number(source.net_income_current)}</td><td>{percent(source.net_income_growth_percent)}</td><td>{citations(source)}</td></tr>)}</tbody></table></div></>}
    </section>}
    <section id="analysis" className="report-section"><h3>Detailed answer & analysis</h3><p className="section-note">Read the complete released answer below. Click a citation to jump to its source record.</p><div className="answer"><ReactMarkdown>{citedText(result.answer || 'No answer was returned.', sources)}</ReactMarkdown></div></section>
    <section id="limitations" className="limitations"><h3>What remains uncertain</h3>{limitations.length ? <ul>{limitations.map((text,index) => <li key={index}>{text}</li>)}</ul> : <p>No specific limitations were returned. This does not establish that every claim is correct.</p>}<p>These are historical observations. They do not establish why a market moved or whether an investment will perform well.</p></section>
    {result.coverage_notes?.length > 0 && <details className="coverage"><summary>Dates and dataset coverage</summary><ul>{result.coverage_notes.map((text,index) => <li key={index}>{text}</li>)}</ul></details>}
    <section id="sources" className="report-section"><h3>Check the evidence <span className="count">{sources.length} records</span></h3><p className="section-note">These records were retrieved for this answer. Check that each cited record supports the associated claim.</p>{!sources.length && <p>No supporting sources were returned.</p>}<div className="sources">{sources.map((source,index) => {
      const url = safeLink(source.url);
      return <article className="source" id={sourceId(index)} key={index}><small>{source.label || `Source ${index + 1}`} · {source.source_type || 'Evidence'}</small><p>{source.title || source.report_identifier || source.company || source.ticker || 'Source record'}</p>{(source.date || source.period_end) && <small>{source.date || source.period_end}</small>}{source.calculation && <p className="source-kind">Calculated evidence</p>}{url && <a href={url} target="_blank" rel="noopener noreferrer">Open original source ↗</a>}</article>;
    })}</div></section>
    <p className="fine">Citation labels: {result.citation_labels_valid ? 'passed structural checks' : 'not verified by structural checks'}. This is not a factual-accuracy score. {result.cache_hit ? 'Loaded from a saved answer.' : ''}</p>
  </section>;
}
