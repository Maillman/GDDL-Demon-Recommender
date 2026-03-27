/**
 * popup.js — Drives the extension popup UI.
 */

const KNOWN_TAGS = [
  "wave", "straight fly", "ship", "cube", "ball", "ufo", "robot", "spider",
  "spam", "timings", "flow", "precision", "memory", "gimmick", "platformer",
  "mini", "dual",
];

const selectedTags = new Set();

// --- DOM refs ---
const statusBadge     = document.getElementById("status-badge");
const beatenInput     = document.getElementById("beaten-input");
const tagListEl       = document.getElementById("tag-list");
const tierMinInput    = document.getElementById("tier-min");
const tierMaxInput    = document.getElementById("tier-max");
const limitInput      = document.getElementById("limit");
const recommendBtn    = document.getElementById("recommend-btn");
const resultsEl       = document.getElementById("results");

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

// --- Tag pills ---
function renderTags() {
  tagListEl.innerHTML = "";
  KNOWN_TAGS.forEach((tag) => {
    const pill = document.createElement("span");
    pill.className = "tag";
    pill.textContent = tag;
    pill.addEventListener("click", () => {
      if (selectedTags.has(tag)) {
        selectedTags.delete(tag);
        pill.classList.remove("selected");
      } else {
        selectedTags.add(tag);
        pill.classList.add("selected");
      }
    });
    tagListEl.appendChild(pill);
  });
}

// --- Recommend ---
recommendBtn.addEventListener("click", async () => {
  const beatenIds = beatenInput.value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const payload = {
    beaten_level_ids: beatenIds,
    desired_tags: [...selectedTags],
    tier_min: tierMinInput.value ? parseInt(tierMinInput.value) : null,
    tier_max: tierMaxInput.value ? parseInt(tierMaxInput.value) : null,
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
          <div class="rec-item">
            <span class="rec-name">${level.name}</span>
            <span class="rec-meta">Tier ${level.tier} · ${level.difficulty} · ${level.tags.join(", ") || "no tags"}</span>
            <span class="rec-meta">${reason}</span>
            <span class="rec-score">${(score * 100).toFixed(0)}% match</span>
          </div>`
        )
        .join("");
    }
    resultsEl.classList.remove("hidden");
  });
});
