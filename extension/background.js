/**
 * background.js — Manifest V3 service worker.
 *
 * Responsibilities:
 *  - Stores the backend API URL in chrome.storage so both content.js and
 *    popup.js can read it without hardcoding.
 *  - Relays messages from content scripts to the backend API (avoids CORS
 *    issues since service workers are not subject to the page's CSP).
 */

const DEFAULT_API_URL = "http://localhost:8000";

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get("apiUrl", (result) => {
    if (!result.apiUrl) {
      chrome.storage.local.set({ apiUrl: DEFAULT_API_URL });
    }
  });
});

/**
 * Message handler — content scripts and popup send messages here to make
 * API calls without dealing with CORS directly.
 *
 * Expected message shapes:
 *   { type: "RECOMMEND", payload: RecommendRequest }
 *   { type: "GET_LEVEL",  payload: { levelId: string } }
 */
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  chrome.storage.local.get("apiUrl", async ({ apiUrl }) => {
    const base = apiUrl || DEFAULT_API_URL;

    try {
      let response;

      if (message.type === "RECOMMEND") {
        response = await fetch(`${base}/recommend`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(message.payload),
        });
      } else if (message.type === "GET_LEVEL") {
        response = await fetch(`${base}/levels/${message.payload.levelId}`);
      } else if (message.type === "HEALTH") {
        response = await fetch(`${base}/health`);
      } else {
        sendResponse({ error: `Unknown message type: ${message.type}` });
        return;
      }

      if (!response.ok) {
        sendResponse({ error: `API error ${response.status}` });
        return;
      }

      const data = await response.json();
      sendResponse({ data });
    } catch (err) {
      sendResponse({ error: err.message });
    }
  });

  // Return true to keep the message channel open for the async response
  return true;
});
