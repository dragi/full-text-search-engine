import { useState } from 'react'
import { getDocument } from '../api.js'

export default function ResultItem({ result }) {
  const [expanded, setExpanded] = useState(false)
  const [doc, setDoc] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function toggle() {
    const next = !expanded
    setExpanded(next)
    if (next && !doc && !loading) {
      setLoading(true)
      setError(null)
      try {
        setDoc(await getDocument(result.id))
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
  }

  return (
    <li className="result">
      <button type="button" className="result-head" onClick={toggle} aria-expanded={expanded}>
        <span className="result-title">{result.title}</span>
        <span className="result-score" title="Relevance score">
          {result.score.toFixed(3)}
        </span>
      </button>
      {/* The snippet HTML is produced by the API, which emits only <mark> tags
          wrapping HTML-escaped text — safe to render directly. */}
      <p
        className="result-snippet"
        dangerouslySetInnerHTML={{ __html: result.snippet }}
      />
      {expanded && (
        <div className="result-body">
          {loading && <p className="muted">Loading…</p>}
          {error && <p className="stats-error">{error}</p>}
          {doc && <p>{doc.body}</p>}
        </div>
      )}
    </li>
  )
}
