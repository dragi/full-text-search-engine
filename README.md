# Full-Text Search Engine

A small information-retrieval engine built from scratch in Python: a tokenizer, an
in-memory inverted index, and TF-IDF ranking, exposed through a FastAPI REST API with
a React search demo pre-loaded with a Simple English Wikipedia subset.

## Demo

The backend runs on Render's free plan and sleeps when idle, so the first search 
after a while can take a minute or two to cold start.

https://dragi-search-engine.vercel.app/
