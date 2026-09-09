import { useEffect, useState } from 'react'
import { getStats, search } from './api.js'
import SearchBar from './components/SearchBar.jsx'
import ResultList from './components/ResultList.jsx'
import Stats from './components/Stats.jsx'

const DEBOUNCE_MS = 250
const LIMIT = 20

export default function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState(null)
  const [clientMs, setClientMs] = useState(null)
  const [status, setStatus] = useState('idle') // idle | loading | done | error
  const [error, setError] = useState(null)
  const [corpus, setCorpus] = useState(null)

  useEffect(() => {
    getStats()
      .then(setCorpus)
      .catch(() => {})
  }, [])

  function handleQuery(next) {
    setQuery(next)
    if (next.trim()) {
      setStatus('loading')
    } else {
      setResponse(null)
      setClientMs(null)
      setError(null)
      setStatus('idle')
    }
  }

  useEffect(() => {
    const trimmed = query.trim()
    if (!trimmed) return undefined

    const controller = new AbortController()
    const timer = setTimeout(async () => {
      const started = performance.now()
      try {
        const data = await search(trimmed, LIMIT, controller.signal)
        setResponse(data)
        setClientMs(performance.now() - started)
        setError(null)
        setStatus('done')
      } catch (err) {
        if (controller.signal.aborted) return
        setError(err.message)
        setStatus('error')
      }
    }, DEBOUNCE_MS)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [query])

  const articleCount = corpus?.documents?.toLocaleString()

  return (
    <main className="app">
      <header className="app-header">
        <h1>Wikipedia Search</h1>
        <p className="tagline">
          A from-scratch full-text search engine over{' '}
          {articleCount
            ? `${articleCount} Simple English Wikipedia articles`
            : 'Simple English Wikipedia'}
          .
        </p>
      </header>
      <SearchBar value={query} onChange={handleQuery} busy={status === 'loading'} />
      <Stats status={status} response={response} clientMs={clientMs} error={error} />
      <ResultList status={status} results={response?.results ?? []} />
    </main>
  )
}
