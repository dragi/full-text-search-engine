export default function Stats({ status, response, clientMs, error }) {
  if (status === 'error') {
    return (
      <p className="stats stats-error" role="alert">
        Could not reach the search API{error ? ` — ${error}` : ''}.
      </p>
    )
  }

  if (status !== 'done' || !response) {
    return <p className="stats">&nbsp;</p>
  }

  const { count, elapsed_ms: elapsedMs } = response
  const noun = count === 1 ? 'result' : 'results'

  return (
    <p className="stats" role="status">
      {count.toLocaleString()} {noun} in {elapsedMs.toFixed(1)} ms
      {typeof clientMs === 'number' && (
        <span className="stats-client"> · {clientMs.toFixed(0)} ms round-trip</span>
      )}
    </p>
  )
}
