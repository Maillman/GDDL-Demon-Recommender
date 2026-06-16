/**
 * content.js — injected into every gdladder.com page.
 *
 * Current responsibilities:
 *  - Detect what page the user is on (level page vs. profile page).
 *  - Extract relevant data from the DOM (beaten levels, current level ID).
 *  - Inject a recommendation panel when appropriate.
 */

(function () {
  "use strict";

  const PANEL_ID = "gddl-recommender-panel";
  const TARGET_WAIT_TIMEOUT_MS = 10000;

  /** Attempt to read the level ID from the current URL or page DOM. */
  function getCurrentLevelId() {
    // e.g. https://gdladder.com/level/12345
    const match = window.location.pathname.match(/\/level\/(\d+)/);
    return match ? match[1] : null;
  }

  /** Find the element that should receive the panel. */
  function findInjectionTarget() {
    const main = document.querySelector("main");
    if (!main) {
      return null;
    }

    const mainTarget = main.querySelector("div") || main;
    return mainTarget.querySelectorAll("div")[0] || mainTarget;
  }

  /** Wait for the target element to exist before mounting the panel. */
  function waitForInjectionTarget(onReady) {
    const target = findInjectionTarget();
    if (target) {
      onReady(target);
      return;
    }

    const observer = new MutationObserver(() => {
      const nextTarget = findInjectionTarget();
      if (!nextTarget) {
        return;
      }

      observer.disconnect();
      clearTimeout(timeoutId);
      onReady(nextTarget);
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });

    const timeoutId = window.setTimeout(() => {
      observer.disconnect();
      onReady(document.body);
    }, TARGET_WAIT_TIMEOUT_MS);
  }

  /** Build the recommendation panel markup. */
  function createPanel(recommendations, matchResult) {
    const panel = document.createElement("div");
    panel.id = PANEL_ID;

    let matchBadge = "";
    if (matchResult) {
      const pct = (matchResult.score * 100).toFixed(0);
      matchBadge = `
        <div class="gddl-match-badge">
          <span class="gddl-match-label">Skill Match</span>
          <span class="gddl-match-score">${pct}%</span>
          <span class="gddl-match-reason">${matchResult.reason}</span>
        </div>`;
    }

    if (!recommendations || recommendations.length === 0) {
      panel.innerHTML = `${matchBadge}<p class="gddl-empty">No recommendations found. Run a sync or adjust your filters.</p>`;
      return panel;
    }

    const items = recommendations
      .map(
        ({ level, score, reason }) => `
          <a class="gddl-rec-item tier-${Math.round(level.tier)}" href="https://gdladder.com/level/${level.id}" rel="noopener noreferrer">
            <span class="gddl-rec-name">${level.name}</span>
            <span class="gddl-rec-tier">Tier ${level.tier.toFixed(2)}</span>
            <span class="gddl-rec-reason">${reason}</span>
            <span class="gddl-rec-score">${(score * 100).toFixed(0)}% Match</span>
          </a>`
      )
      .join("");

    panel.innerHTML = `
      ${matchBadge}
      <h3 class="gddl-panel-title">Recommended Demons</h3>
      <div class="gddl-rec-list">${items}</div>`;
    return panel;
  }

  /** Inject the recommendation panel into the page. */
  function injectPanel(recommendations, matchResult) {
    const panel = createPanel(recommendations, matchResult);

    waitForInjectionTarget((target) => {
      const existing = document.getElementById(PANEL_ID);
      if (existing) existing.remove();

      if (!target.isConnected) {
        document.body.appendChild(panel);
        return;
      }

      target.after(panel);
    });
  }

  /** Request recommendations and a skill-match score from the backend (via background.js). */
  async function fetchRecommendations(levelId) {
    // Try to get the logged-in user's beaten levels and skills; falls back to empty if not logged in.
    let beatenIds = [];
    let userSkills = {};
    try {
      const userResp = await chrome.runtime.sendMessage({ type: "GET_USER_DATA" });
      beatenIds = userResp?.data?.beatenIds ?? [];
      userSkills = userResp?.data?.skills ?? {};
    } catch (_) {}

    const recommendPayload = {
      level_id: levelId ?? null,
      desired_tags: {},
      limit: 10,
      user_beaten_ids: beatenIds,
      user_skills: userSkills,
    };

    const matchPayload = {
      levelId,
      body: { user_skills: userSkills },
    };

    const [recommendResp, matchResp] = await Promise.all([
      new Promise((resolve) =>
        chrome.runtime.sendMessage({ type: "RECOMMEND", payload: recommendPayload }, resolve)
      ),
      new Promise((resolve) =>
        chrome.runtime.sendMessage({ type: "MATCH_LEVEL", payload: matchPayload }, resolve)
      ),
    ]);

    if (chrome.runtime.lastError) {
      console.warn("[GDDL Recommender] API error:", chrome.runtime.lastError);
      return;
    }

    const recommendations = recommendResp?.data?.recommendations ?? [];
    const matchResult = matchResp?.data ?? null;
    injectPanel(recommendations, matchResult);
  }

  // --- Entry point ---
  const levelId = getCurrentLevelId();
  if (levelId) {
    fetchRecommendations(levelId);
  }
})();
