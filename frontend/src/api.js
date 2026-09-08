const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function search(q, limit = 10) {
  const params = new URLSearchParams({ q, limit: String(limit) })
  const res = await fetch(`${BASE_URL}/search?${params}`)
  if (!res.ok) throw new Error(`search failed: ${res.status}`)
  return res.json()
}

export async function getDocument(id) {
  const res = await fetch(`${BASE_URL}/documents/${id}`)
  if (!res.ok) throw new Error(`document ${id} not found`)
  return res.json()
}

export async function getStats() {
  const res = await fetch(`${BASE_URL}/stats`)
  if (!res.ok) throw new Error(`stats failed: ${res.status}`)
  return res.json()
}
