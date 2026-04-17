/**
 * background.js — Manifest V3 service worker.
 *
 * Responsibilities:
 *  - Stores the backend API URL in chrome.storage so both content.js and
 *    popup.js can read it without hardcoding.
 *  - Relays messages from content scripts to the backend API (avoids CORS
 *    issues since service workers are not subject to the page's CSP).
 */

// For public deployments, change this to your hosted backend URL.
// Users can also override this at any time via the popup settings.
const DEFAULT_API_URL = "https://gddl.melvinwhitaker.com";
const GDDL_API = "https://gdladder.com/api";
const SUBMISSIONS_PAGE_SIZE = 25;

// Mirrors the static mapping in backend/gddl_client.py
const TAG_ID_TO_NAME = {
  "1": "Cube",         "2": "Ship",        "3": "Ball",    "4": "UFO",
  "5": "Wave",         "6": "Robot",       "7": "Spider",  "20": "Swing",
  "8": "Nerve Control","9": "Memory",      "10": "Learny", "11": "Duals",
  "12": "Chokepoints", "13": "High CPS",   "14": "Timings","15": "Flow",
  "16": "Overall",     "17": "Gimmicky",   "18": "Fast-Paced", "19": "Slow-Paced",
};

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get("apiUrl", (result) => {
    if (!result.apiUrl) {
      chrome.storage.local.set({ apiUrl: DEFAULT_API_URL });
    }
  });
});

// Warm the user-data cache when the service worker starts so the popup can
// read it without waiting on a fresh fetch.
chrome.runtime.onStartup.addListener(() => { prefetchUserData(); });

/** Fire-and-forget cache warm — errors are intentionally swallowed. */
function prefetchUserData() {
  getUserData().catch(() => {});
}

/**
 * Message handler — content scripts and popup send messages here to make
 * API calls without dealing with CORS directly.
 *
 * Expected message shapes:
 *   { type: "RECOMMEND",     payload: RecommendRequest }
 *   { type: "GET_LEVEL",     payload: { levelId: string } }
 *   { type: "GET_USER_DATA" }
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
        if (!response.ok) { sendResponse({ error: `API error ${response.status}` }); return; }
        sendResponse({ data: await response.json() });
      } else if (message.type === "GET_LEVEL") {
        response = await fetch(`${base}/levels/${message.payload.levelId}`);
        if (!response.ok) { sendResponse({ error: `API error ${response.status}` }); return; }
        sendResponse({ data: await response.json() });
      } else if (message.type === "HEALTH") {
        response = await fetch(`${base}/health`);
        if (!response.ok) { sendResponse({ error: `API error ${response.status}` }); return; }
        sendResponse({ data: await response.json() });
      } else if (message.type === "GET_USER_DATA") {
        sendResponse(await getUserData());
      } else {
        sendResponse({ error: `Unknown message type: ${message.type}` });
      }
    } catch (err) {
      sendResponse({ error: err.message });
    }
  });

  // Return true to keep the message channel open for the async response
  return true;
});

/**
 * Fetch the logged-in user's beaten level IDs and skill distribution directly
 * from the GDDL API using the user's session cookies.
 * Results are cached in chrome.storage.local and only re-fetched when the
 * user's SubmissionCount changes (indicating new beaten levels).
 *
 * Returns { data: { userId, beatenIds, skills } } or { error: string }.
 */
async function getUserData() {
  // Step 1: get the current user's ID and SubmissionCount
  let me;
  try {
    const meResp = await fetch(`${GDDL_API}/user/me`, { credentials: "include" });
    if (!meResp.ok) return { error: `GDDL /user/me error ${meResp.status}` };
    me = await meResp.json();
  } catch (err) {
    return { error: err.message };
  }

  const userId = me?.ID ?? null;
  const submissionCount = me?.SubmissionCount ?? null;

  if (!userId) return { data: { userId: null, beatenIds: [], skills: {} } };

  // Step 2: check the cache — skip GDDL calls if submission count is unchanged
  const { userDataCache } = await chrome.storage.local.get("userDataCache");
  if (
    userDataCache &&
    userDataCache.userId === userId &&
    userDataCache.submissionCount === submissionCount
  ) {
    return { data: { userId, beatenIds: userDataCache.beatenIds, skills: userDataCache.skills } };
  }

  // Step 3: cache miss — fetch beaten IDs and skills from GDDL directly
  try {
    const [beatenIds, skills] = await Promise.all([
      fetchBeatenLevelIds(userId),
      fetchUserSkills(userId),
    ]);

    await chrome.storage.local.set({
      userDataCache: { userId, submissionCount, beatenIds, skills },
    });

    return { data: { userId, beatenIds, skills } };
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * Fetch all level IDs the user has submitted ratings for (proxy for beaten levels).
 * Handles pagination transparently.
 */
async function fetchBeatenLevelIds(userId) {
  const levelIds = [];
  let page = 0;

  while (true) {
    const url = new URL(`${GDDL_API}/user/${userId}/submissions`);
    url.searchParams.set("limit", SUBMISSIONS_PAGE_SIZE);
    url.searchParams.set("page", page);

    const resp = await fetch(url, { credentials: "include" });
    if (!resp.ok) throw new Error(`GDDL submissions error ${resp.status}`);

    const data = await resp.json();
    const submissions = data.submissions ?? [];
    if (submissions.length === 0) break;

    for (const s of submissions) {
      if (s.Level?.ID) levelIds.push(String(s.Level.ID));
    }

    if (levelIds.length >= (data.total ?? 0)) break;
    page++;
  }

  return levelIds;
}

/**
 * Fetch the user's skill distribution and return tag name -> normalized score (0–1).
 */
async function fetchUserSkills(userId) {
  const url = new URL(`${GDDL_API}/user/${userId}/skills`);
  url.searchParams.set("tierCorrection", "true");
  url.searchParams.set("adjustRarity", "true");

  const resp = await fetch(url, { credentials: "include" });
  if (!resp.ok) throw new Error(`GDDL skills error ${resp.status}`);

  const raw = await resp.json();

  const named = {};
  for (const [tagId, score] of Object.entries(raw)) {
    const name = TAG_ID_TO_NAME[tagId];
    if (name) named[name] = score;
  }

  const sum = Object.values(named).reduce((a, b) => a + b, 0);
  if (sum === 0) return named;
  return Object.fromEntries(Object.entries(named).map(([k, v]) => [k, v / sum]));
}

// Prefetch user data as soon as the user begins navigating to any gdladder.com
// page, so the cache is warm by the time content.js or the popup asks for it.
chrome.webNavigation.onCommitted.addListener(
  () => { prefetchUserData(); },
  { url: [{ hostEquals: "gdladder.com" }] }
);

/**
 * SPA navigation handler — gdladder.com uses pushState routing, so the
 * content script only runs once on initial page load.  Re-inject it
 * whenever the History API signals an in-page navigation.
 */
chrome.webNavigation.onHistoryStateUpdated.addListener(
  (details) => {
    prefetchUserData();
    chrome.scripting.executeScript({
      target: { tabId: details.tabId },
      files: ["content.js"],
    });
  },
  { url: [{ hostEquals: "gdladder.com" }] }
);
