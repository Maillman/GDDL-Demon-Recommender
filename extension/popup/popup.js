/**
 * popup.js — Drives the extension popup UI.
 */

// Tag names match the GDDL API exactly (from /api/level/{ID}/tags → Tag.Name).
const KNOWN_TAGS = [
  "Cube", "Ship", "Ball", "UFO", "Wave", "Robot", "Spider", "Swing",
  "Timings", "High CPS", "Flow", "Memory", "Nerve Control",
  "Duals", "Chokepoints", "Learny", "Gimmicky", "Overall",
  "Fast-Paced", "Slow-Paced",
];

const DEFAULT_API_URL = "https://gddl.melvinwhitaker.com";

// tag name -> raw slider value (0–100)
const tagWeights = {};

// --- DOM refs ---
const statusBadge      = document.getElementById("status-badge");
const levelIdInput     = document.getElementById("level-id-input");
const showBeatenInput  = document.getElementById("show-beaten-input");
const tagListEl        = document.getElementById("tag-list");
const tierMinInput     = document.getElementById("tier-min");
const tierMaxInput     = document.getElementById("tier-max");
const limitInput       = document.getElementById("limit");
const recommendBtn     = document.getElementById("recommend-btn");
const resultsEl        = document.getElementById("results");
const settingsLink     = document.getElementById("settings-link");
const settingsPanel    = document.getElementById("settings-panel");
const apiUrlInput      = document.getElementById("api-url-input");
const saveUrlBtn       = document.getElementById("save-url-btn");
const resetUrlBtn      = document.getElementById("reset-url-btn");
const settingsStatus   = document.getElementById("settings-status");

// --- Settings panel ---
settingsLink.addEventListener("click", (e) => {
  e.preventDefault();
  const isHidden = settingsPanel.classList.toggle("hidden");
  settingsLink.textContent = isHidden ? "Settings" : "Hide Settings";
  if (!isHidden) {
    chrome.storage.local.get("apiUrl", ({ apiUrl }) => {
      apiUrlInput.value = apiUrl || DEFAULT_API_URL;
    });
  }
});

saveUrlBtn.addEventListener("click", () => {
  const url = apiUrlInput.value.trim();
  if (!url) return;
  chrome.storage.local.set({ apiUrl: url }, () => {
    settingsStatus.textContent = "Saved.";
    setTimeout(() => { settingsStatus.textContent = ""; }, 2000);
    checkHealth();
  });
});

resetUrlBtn.addEventListener("click", () => {
  chrome.storage.local.set({ apiUrl: DEFAULT_API_URL }, () => {
    apiUrlInput.value = DEFAULT_API_URL;
    settingsStatus.textContent = "Reset to default.";
    setTimeout(() => { settingsStatus.textContent = ""; }, 2000);
    checkHealth();
  });
});

// Open recommendation links in the currently active tab instead of creating a new one.
resultsEl.addEventListener("click", async (event) => {
  const link = event.target.closest("a.rec-item");
  if (!link) return;

  event.preventDefault();
  const url = link.href;

  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const activeTab = tabs[0];
    if (activeTab?.id !== undefined) {
      await chrome.tabs.update(activeTab.id, { url });
      window.close();
      return;
    }
  } catch (err) {
    console.error("Failed to reuse active tab:", err);
  }

  chrome.tabs.create({ url });
});

// --- Init ---
checkHealth();
renderTags();

// --- Health check ---
function checkHealth() {
  chrome.runtime.sendMessage({ type: "HEALTH" }, (response) => {
    if (chrome.runtime.lastError || response?.error) {
      setStatus("error", "API offline");
      recommendBtn.disabled = true;
      return;
    }
    const count = response.data?.level_count ?? 0;
    setStatus("ok", `${count} levels`);
  });
}

function setStatus(state, text) {
  statusBadge.textContent = text;
  statusBadge.className = `badge badge--${state}`;
}

// --- Tag sliders ---
function renderTags() {
  tagListEl.innerHTML = "";
  KNOWN_TAGS.forEach((tag) => {
    tagWeights[tag] = 0;

    const row = document.createElement("div");
    row.className = "slider-row";

    const label = document.createElement("span");
    label.className = "slider-label";
    label.textContent = tag;

    const slider = document.createElement("input");
    slider.type = "range";
    slider.min = "0";
    slider.max = "100";
    slider.value = "0";

    const valueDisplay = document.createElement("span");
    valueDisplay.className = "slider-value";
    valueDisplay.textContent = "0";

    slider.addEventListener("input", () => {
      tagWeights[tag] = parseInt(slider.value);
      valueDisplay.textContent = slider.value;
    });

    row.appendChild(label);
    row.appendChild(slider);
    row.appendChild(valueDisplay);
    tagListEl.appendChild(row);
  });
}

// --- Recommend ---
recommendBtn.addEventListener("click", async () => {
  const levelId = levelIdInput.value.trim() || null;

  const total = Object.values(tagWeights).reduce((a, b) => a + b, 0);
  const desired_tags = {};
  if (total > 0) {
    for (const [tag, weight] of Object.entries(tagWeights)) {
      if (weight > 0) desired_tags[tag] = weight / total;
    }
  }

  // Try to get the logged-in user's beaten levels and skills; falls back to empty if not logged in.
  let beatenIds = [];
  let userSkills = {};
  try {
    const userResp = await chrome.runtime.sendMessage({ type: "GET_USER_DATA" });
    beatenIds = userResp?.data?.beatenIds ?? [];
    userSkills = userResp?.data?.skills ?? {};
  } catch (_) {}

  const payload = {
    level_id: levelId,
    desired_tags,
    show_beaten: showBeatenInput.checked,
    tier_min: tierMinInput.value ? parseFloat(tierMinInput.value) : null,
    tier_max: tierMaxInput.value ? parseFloat(tierMaxInput.value) : null,
    limit: parseInt(limitInput.value) || 10,
    user_beaten_ids: beatenIds,
    user_skills: userSkills,
  };

  recommendBtn.disabled = true;
  recommendBtn.textContent = "Loading...";
  resultsEl.classList.add("hidden");
  resultsEl.innerHTML = "";

  chrome.runtime.sendMessage({ type: "RECOMMEND", payload }, (response) => {
    recommendBtn.disabled = false;
    recommendBtn.textContent = "Get Recommendations";

    if (chrome.runtime.lastError || response?.error) {
      const errP = document.createElement("p");
      errP.style.color = "#f87171";
      errP.textContent = `Error: ${response?.error || "Unknown error"}`;
      resultsEl.replaceChildren(errP);
      resultsEl.classList.remove("hidden");
      return;
    }

    const recs = response.data?.recommendations ?? [];
    if (recs.length === 0) {
      const emptyP = document.createElement("p");
      emptyP.style.color = "#94a3b8";
      emptyP.textContent = "No results. Try adjusting your filters or run a sync.";
      resultsEl.replaceChildren(emptyP);
    } else {
      const items = recs.map(({ level, score, reason }) => {
        const a = document.createElement("a");
        a.className = `rec-item tier-${Math.round(level.tier)}`;
        a.href = `https://gdladder.com/level/${level.id}`;

        const name = document.createElement("span");
        name.className = "rec-name";
        name.textContent = level.name;

        const topTags = Object.keys(level.tags).slice(0, 3).join(", ") || "no tags";
        const meta1 = document.createElement("span");
        meta1.className = "rec-meta";
        meta1.textContent = `Tier ${level.tier.toFixed(2)} · ${level.difficulty} Demon · ${topTags}`;

        const meta2 = document.createElement("span");
        meta2.className = "rec-meta";
        meta2.textContent = reason;

        const scoreEl = document.createElement("span");
        scoreEl.className = "rec-score";
        scoreEl.textContent = `${(score * 100).toFixed(0)}% Match`;

        a.append(name, meta1, meta2, scoreEl);
        return a;
      });
      resultsEl.replaceChildren(...items);
    }
    resultsEl.classList.remove("hidden");
  });
});
