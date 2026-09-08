import SearchBar from './components/SearchBar.jsx'
import ResultList from './components/ResultList.jsx'
import Stats from './components/Stats.jsx'

export default function App() {
  return (
    <main className="app">
      <h1>Search</h1>
      <SearchBar />
      <Stats />
      <ResultList />
    </main>
  )
}
