# CLAUDE.md

## Project Overview

GDDL Demon Recommender is a Chrome extension + FastAPI backend that recommends Geometry Dash demons from [gdladder.com](https://gdladder.com) based on a user's skill profile. It embeds levels as semantic vectors using community-voted skill tags, then performs cosine similarity search via ChromaDB.

## Commands

### Backend

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Configure environment (requires GDDL API key from gdladder.com)
cp .env.example .env

# Populate ChromaDB (one-time or periodic; supports resumable checkpoints)
python backend/sync.py

# Start the API server (http://localhost:8000)
uvicorn backend.main:app --reload

# Regenerate embeddings after changing embedder.level_to_text() without re-fetching API data
python backend/reembed.py
python backend/reembed.py --dry-run        # preview only
python backend/reembed.py --batch-size 64  # custom batch size
```

### Chrome Extension

1. Open `chrome://extensions`, enable **Developer mode**
2. **Load unpacked** → select the `extension/` folder
3. Visit `https://gdladder.com/` to see the injected panel, or click the extension icon for the popup

There is no formal test suite. Manual testing is documented in [docs/LOG.md](docs/LOG.md).

## Architecture

```
Chrome Extension (Manifest V3)
  ├── content.js       — injected into gdladder.com; extracts level ID, injects recommendation panel
  ├── background.js    — service worker; proxies all API calls to localhost:8000 (avoids CORS)
  └── popup/           — standalone popup UI with tag pills, tier filters, beaten-level input

FastAPI Backend (localhost:8000)
  ├── main.py          — 3 endpoints: GET /health, POST /recommend, GET /levels/{id}
  ├── recommender.py   — builds query vector, applies tier filters, generates explanations
  ├── embedder.py      — converts tag profiles → text → sentence-transformer embeddings
  ├── db.py            — ChromaDB wrapper (cosine distance, upsert, similarity query)
  └── gddl_client.py   — async GDDL API client with retry + rate-limit handling

Data Pipeline
  └── sync.py          — fetches all levels + tags from GDDL API, embeds, stores in ChromaDB
```

### Recommendation Query Flow

1. User provides `beaten_level_ids` + `desired_tags` + `tier_min/max`
2. `recommender._build_query_vector()` averages embeddings of beaten levels with a desired-tag embedding
3. `db.query()` runs cosine similarity search in ChromaDB with optional tier metadata filter
4. Results returned with score (0–1) and human-readable reason string

### Embedding Strategy

- Tags are weighted by community ReactCount share; a tag with 35% of votes appears ~7× in the embedding text (scale factor: 20)
- `embedder.level_to_text()` produces the text fed to `sentence-transformers/all-MiniLM-L6-v2`
- Levels with no tags default to the `"unknown"` token
- After changing `level_to_text()`, run `reembed.py` to regenerate embeddings without re-fetching the API

### Extension Messaging

`content.js` and `popup.js` never call the backend directly — all requests go through `background.js` via `chrome.runtime.sendMessage`. The API base URL is stored in `chrome.storage.local` (default: `http://localhost:8000`).

## Key Constraints

- **GDDL API rate limit**: 100 req/min; `sync.py` uses 0.7s delays + exponential backoff. Do not remove these delays.
- **ChromaDB is local and persistent** at `backend/chroma_db/` (git-ignored). It must be populated via `sync.py` before the backend can serve recommendations.
- **No formal test suite** exists; changes to `recommender.py`, `embedder.py`, or `db.py` should be validated manually via the `/recommend` endpoint.
- The `sync.py` checkpoint file (`backend/sync_checkpoint.json`) is git-ignored; it enables resuming interrupted syncs.
