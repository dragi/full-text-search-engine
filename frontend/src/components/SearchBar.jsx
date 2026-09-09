export default function SearchBar({ value, onChange, busy }) {
  return (
    <div className="search-bar">
      <input
        type="search"
        className="search-input"
        placeholder="Search articles…"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        autoFocus
        autoComplete="off"
        spellCheck="false"
        aria-label="Search query"
      />
      <span className={busy ? 'search-spinner is-busy' : 'search-spinner'} aria-hidden="true" />
    </div>
  )
}
