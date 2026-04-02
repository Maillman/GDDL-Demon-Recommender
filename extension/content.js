/**
 * content.js — injected into every gdladder.com page.
 *
 * Current responsibilities:
 *  - Detect what page the user is on (level page vs. profile page).
 *  - Extract relevant data from the DOM (beaten levels, current level ID).
 *  - Inject a recommendation panel when appropriate.
 *
 * NOTE: The DOM selectors here are placeholders. They need to be updated
 * once the actual gdladder.com HTML structure is inspected (Phase 4).
 */

(function () {
  "use strict";

  /** Attempt to read the level ID from the current URL or page DOM. */
  function getCurrentLevelId() {
    // e.g. https://gdladder.com/level/12345
    const match = window.location.pathname.match(/\/level\/(\d+)/);
    return match ? match[1] : null;
  }

  /** Inject the recommendation panel into the page. */
  function injectPanel(recommendations) {
    const existing = document.getElementById("gddl-recommender-panel");
    if (existing) existing.remove();

    const panel = document.createElement("div");
    panel.id = "gddl-recommender-panel";

    if (!recommendations || recommendations.length === 0) {
      panel.innerHTML = `<p class="gddl-empty">No recommendations found. Run a sync or adjust your filters.</p>`;
    } else {
      const items = recommendations
        .map(
          ({ level, score, reason }) => `
          <div class="gddl-rec-item">
            <span class="gddl-rec-name">${level.name}</span>
            <span class="gddl-rec-tier">Tier ${level.tier.toFixed(2)}</span>
            <span class="gddl-rec-reason">${reason}</span>
            <span class="gddl-rec-score">${(score * 100).toFixed(0)}% Match</span>
          </div>`
        )
        .join("");
      panel.innerHTML = `
        <h3 class="gddl-panel-title">Recommended Demons</h3>
        <div class="gddl-rec-list">${items}</div>`;
    }

    // Append to main content area — selector needs verification against live site
    const main = document.querySelector("main") || document.body;
    const mainTarget = main.querySelector("div") || main;
    const target = mainTarget.querySelectorAll("div")[0] || mainTarget;
    target.after(panel);
  }

  /** Request recommendations from the backend (via background.js). */
  function fetchRecommendations(levelId) {
    const payload = {
      beaten_level_ids: [],
      desired_tags: {},
      limit: 10,
    };

    // If we're on a level page, use that level's neighbors as context
    if (levelId) {
      payload.beaten_level_ids = [levelId];
    }

    chrome.runtime.sendMessage({ type: "RECOMMEND", payload }, (response) => {
      if (chrome.runtime.lastError || response?.error) {
        console.warn("[GDDL Recommender] API error:", response?.error || chrome.runtime.lastError);
        return;
      }
      injectPanel(response.data?.recommendations ?? []);
    });
  }

  // --- Entry point ---
  const levelId = getCurrentLevelId();
  if (levelId) {
    fetchRecommendations(levelId);
  }
})();
