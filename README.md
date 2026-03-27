# GDDL Demon Recommender

A skill-aware demon recommender for Geometry Dash, built on top of the [Geometry Dash Demon Ladder (GDDL)](https://gdladder.com/).

---

## What It Does

The GDDL assigns every Demon-difficulty level a tier from 1–35, giving players a much finer difficulty scale than the game's five built-in labels. But tier alone doesn't capture *what skills* a level demands — two tier-15 levels can require completely different techniques (e.g. precision wave vs. memory cube). Picking your next level by tier alone often means jumping into something that punishes skills you've never trained.

The GDDL Demon Recommender builds a semantic skill profile for every demon from its community-assigned tags, then matches a player's existing skill set to the most appropriate next level. The result surfaces as a Chrome extension panel directly on gdladder.com, with no separate app required.

---

## Project Structure

```
GDDL-Demon-Recommender/
├── backend/            # Python API server + data pipeline
├── extension/          # Chrome Extension (Manifest V3)
└── docs/               # Design documents and project log
```

### `backend/`

A Python + FastAPI server that owns all data fetching, embedding, and recommendation logic. Nothing computationally heavy runs in the browser.

| File | Purpose |
|---|---|
| `main.py` | FastAPI app — `/health`, `/recommend`, `/levels/{id}` |
| `models.py` | Shared Pydantic data models |
| `gddl_client.py` | Async client for the GDDL REST API |
| `embedder.py` | Converts level tag sets into embedding vectors via `sentence-transformers` |
| `db.py` | ChromaDB setup, upsert, and similarity-query helpers |
| `recommender.py` | Builds a query vector from beaten levels + desired tags; runs nearest-neighbor search |
| `sync.py` | CLI script to pull fresh data from the GDDL API and upsert into ChromaDB |
| `requirements.txt` | Pinned Python dependencies |

### `extension/`

A Manifest V3 Chrome Extension that injects a recommendation panel into gdladder.com pages and provides a standalone popup for querying recommendations without navigating the site.

| File | Purpose |
|---|---|
| `manifest.json` | Extension manifest — permissions, content script targets, popup |
| `background.js` | Service worker — proxies all API calls to the backend (avoids CORS) |
| `content.js` | Injected into gdladder.com — detects the current level and renders the recommendation panel |
| `content.css` | Styles for the injected panel |
| `popup/popup.html` | Extension popup UI — beaten level input, skill tag pills, tier filter |
| `popup/popup.js` | Popup logic — builds requests, relays through background.js, renders results |
| `popup/popup.css` | Popup styles |

### `docs/`

| File | Purpose |
|---|---|
| `PROJECTPITCH.md` | Original project pitch — problem statement and motivation |
| `PROJECTINITIALDESIGN.md` | Full architecture, data model, tech stack, and development timeline |
| `LOG.md` | Running log of hours and work completed |

---

## How It Works

1. **Sync** — `sync.py` fetches all demons from the GDDL API, generates an embedding vector for each level from its tag set, and stores them in a local ChromaDB vector database.
2. **Query** — when a user provides beaten level IDs and/or desired skill tags, the backend averages the corresponding embedding vectors into a single "skill profile" vector.
3. **Search** — a nearest-neighbor search in ChromaDB returns the levels whose skill profiles are closest to the player's, optionally filtered by tier range.
4. **Display** — the Chrome extension sends the query through its background service worker to the backend and renders the ranked recommendations on the page.

---

## Getting Started

### Prerequisites
- Python 3.11+
- Google Chrome

### Backend

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env   # add your GDDL_API_KEY
python sync.py --dry-run     # verify API connection and field shapes
python sync.py               # populate the database
uvicorn main:app --reload    # start the API at http://localhost:8000
```

### Chrome Extension

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** and select the `extension/` folder
4. Navigate to any level page on [gdladder.com](https://gdladder.com/) — the recommendation panel will appear automatically

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI |
| Vector database | ChromaDB (local, embedded) |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Data source | GDDL REST API |
| Frontend | Chrome Extension — HTML/CSS/Vanilla JS (Manifest V3) |
