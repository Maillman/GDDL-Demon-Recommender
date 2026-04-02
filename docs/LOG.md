# Project Log
## Time Spent On Project
| Date | Time | Description |
| :---: | :---: | --- |
| 3/26/2026 | 2 hours | Initializing Project, Researching Project Structure and Tech Stack |
| 3/28/2026 | 2 hours | Researched GDDL API document: fetch raw JSON, confirm actual field names and tag structure, update python scripts and javascript files accordingly |
| 3/30/2026 | 1 hours | Added RatingCount caching to avoid API calls when it's unlikely the tags have changed |
| 3/30/2026 | 1 hours | Run `sync.py` with checkpointing to ensure correct data is stored properly |
| 3/31/2026 | 2 hours | Modified embedding storage so more dominant skillsets have greater influence on the embedding vector. Run full `sync.py` to populate ChromaDB; verify level count and spot-check stored embeddings |
| 4/01/2026 | 1.5 hours | Validate and adjust for better embedding quality: query ChromaDB manually and confirm similar-tag levels cluster together |
| 4/01/2026 | 2 hours | Chrome extension Phase 1: load as unpacked extension, confirm `content.js` injects on gdladder.com, inspect DOM for correct selectors |
| 4/02/2026 | 4 hours | Chrome extension Phase 2: popup full flow — tag selection → background.js relay → API → results rendered. Research GDDL API and documentation for skill distribution endpoint and accuracy |