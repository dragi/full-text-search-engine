import ResultItem from './ResultItem.jsx'

export default function ResultList({ status, results }) {
  if (status === 'done' && results.length === 0) {
    return <p className="empty">No matching articles.</p>
  }

  if (results.length === 0) {
    return null
  }

  return (
    <ol className="results">
      {results.map((result) => (
        <ResultItem key={result.id} result={result} />
      ))}
    </ol>
  )
}
