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
| 4/03/2026 | 2.5 hours | Retrieve beaten levels and skill distribution using user id |
| 4/04/2026 | 2 hours | UI polish: injected panel styling tuned to gdladder.com theme |
| 4/04/2026 | 1 hours | UI polish: popup styling tuned to gdladder.com theme |
| 4/06/2026 | 2 hours | Adjust user id influence on RecommendationRequest. UI polish: popup styling further tuned to gdladder.com theme |
| 4/07/2026 | 2.5 hours | Migrated fetching user information from backend to extension to cache in browser. Run full `sync.py` to fetch updated tags |
| 4/10/2026 | 2.5 hours | Added icon set to extension. Prepare backend for deployment with Oracle Cloud |
| 4/11/2026 | 3 hours | Creating and running script to acquire Oracle Cloud VM.Standard.A1.Flex instance |
| 4/13/2026 | 2.5 hours | Eliminate XSS risk and bump version for Chrome Web Store |