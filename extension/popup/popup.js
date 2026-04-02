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

// tag name -> raw slider value (0–100)
const tagWeights = {};

// --- DOM refs ---
const statusBadge     = document.getElementById("status-badge");
const beatenInput     = document.getElementById("beaten-input");
const tagListEl       = document.getElementById("tag-list");
const tierMinInput    = document.getElementById("tier-min");
const tierMaxInput    = document.getElementById("tier-max");
const limitInput      = document.getElementById("limit");
const recommendBtn    = document.getElementById("recommend-btn");
const resultsEl       = document.getElementById("results");

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
  const beatenIds = beatenInput.value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const total = Object.values(tagWeights).reduce((a, b) => a + b, 0);
  const desired_tags = {};
  if (total > 0) {
    for (const [tag, weight] of Object.entries(tagWeights)) {
      if (weight > 0) desired_tags[tag] = weight / total;
    }
  }

  const payload = {
    beaten_level_ids: beatenIds,
    desired_tags,
    tier_min: tierMinInput.value ? parseFloat(tierMinInput.value) : null,
    tier_max: tierMaxInput.value ? parseFloat(tierMaxInput.value) : null,
    limit: parseInt(limitInput.value) || 10,
  };

  recommendBtn.disabled = true;
  recommendBtn.textContent = "Loading...";
  resultsEl.classList.add("hidden");
  resultsEl.innerHTML = "";

  chrome.runtime.sendMessage({ type: "RECOMMEND", payload }, (response) => {
    recommendBtn.disabled = false;
    recommendBtn.textContent = "Get Recommendations";

    if (chrome.runtime.lastError || response?.error) {
      resultsEl.innerHTML = `<p style="color:#f87171">Error: ${response?.error || "Unknown error"}</p>`;
      resultsEl.classList.remove("hidden");
      return;
    }

    const recs = response.data?.recommendations ?? [];
    if (recs.length === 0) {
      resultsEl.innerHTML = `<p style="color:#94a3b8">No results. Try adjusting your filters or run a sync.</p>`;
    } else {
      resultsEl.innerHTML = recs
        .map(
          ({ level, score, reason }) => `
          <a class="rec-item" href="https://gdladder.com/level/${level.id}">
            <span class="rec-name">${level.name}</span>
            <span class="rec-meta">Tier ${level.tier.toFixed(2)} · ${level.difficulty} Demon · ${Object.keys(level.tags).join(", ") || "no tags"}</span>
            <span class="rec-meta">${reason}</span>
            <span class="rec-score">${(score * 100).toFixed(0)}% Match</span>
          </a>`
        )
        .join("");
    }
    resultsEl.classList.remove("hidden");
  });
});
