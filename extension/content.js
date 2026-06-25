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
  function findPanelInjectionTarget() {
    const main = document.querySelector("main");
    if (!main) {
      return null;
    }

    const mainTarget = main.querySelector("div") || main;
    return mainTarget.querySelectorAll("div")[0] || mainTarget;
  }

  /** Find the element that should receive the match result. */
  function findMatchInjectionTarget() {
    const firstDivTarget = findPanelInjectionTarget();
    return firstDivTarget.querySelectorAll("div")[0] || firstDivTarget;
  }

  /** Wait for a target element (found by finderFn) to exist before calling onReady. */
  function waitForInjectionTarget(finderFn, onReady) {
    const target = finderFn();
    if (target) {
      onReady(target);
      return;
    }

    const observer = new MutationObserver(() => {
      const nextTarget = finderFn();
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

  /** Build the match badge element. */
  function createMatchBadge(matchResult) {
    const wrapper = document.createElement("div");
    wrapper.id = "gddl-match-badge-wrapper";
    if (matchResult) {
      const pct = (matchResult.score * 100).toFixed(0);
      wrapper.innerHTML = `
        <div class="gddl-match-badge">
          <div class="gddl-match-results">
            <span class="gddl-match-label">Skill Match</span>
            <span class="gddl-match-score">${pct}%</span>
          </div>
          <span class="gddl-match-reason">${matchResult.reason}</span>
        </div>`;
    }
    return wrapper;
  }

  /** Build the recommendation panel markup. */
  function createPanel(recommendations) {
    const panel = document.createElement("div");
    panel.id = PANEL_ID;

    if (!recommendations || recommendations.length === 0) {
      panel.innerHTML = `<p class="gddl-empty">No recommendations found. Run a sync or adjust your filters.</p>`;
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
      <h3 class="gddl-panel-title">Recommended Demons</h3>
      <div class="gddl-rec-list">${items}</div>`;
    return panel;
  }

  /** Inject the recommendation panel and match badge into their separate targets.
   *  Pass undefined for either argument to skip that injection entirely. */
  function injectPanel(recommendations, matchResult) {
    if (recommendations !== undefined) {
      const panel = createPanel(recommendations);
      waitForInjectionTarget(findPanelInjectionTarget, (target) => {
        const existing = document.getElementById(PANEL_ID);
        if (existing) existing.remove();

        if (!target.isConnected) {
          document.body.appendChild(panel);
        } else {
          target.after(panel);
        }
      });
    }

    if (matchResult !== undefined) {
      const badge = createMatchBadge(matchResult);
      waitForInjectionTarget(findMatchInjectionTarget, (target) => {
        const existing = document.getElementById("gddl-match-badge-wrapper");
        if (existing) existing.remove();

        if (!target.isConnected) {
          document.body.appendChild(badge);
        } else {
          target.after(badge);
        }
      });
    }
  }

  /** Request recommendations and a skill-match score from the backend (via background.js). */
  async function fetchRecommendations(levelId) {
    const settings = await new Promise((resolve) =>
      chrome.storage.local.get(["showPanel", "showMatchBadge"], resolve)
    );
    const showPanel = settings.showPanel !== false;
    const showMatchBadge = settings.showMatchBadge !== false;

    if (!showPanel && !showMatchBadge) return;

    // Try to get the logged-in user's beaten levels and skills; falls back to empty if not logged in.
    let beatenIds = [];
    let userSkills = {};
    try {
      const userResp = await chrome.runtime.sendMessage({ type: "GET_USER_DATA" });
      beatenIds = userResp?.data?.beatenIds ?? [];
      userSkills = userResp?.data?.skills ?? {};
    } catch (_) {}

    const requests = [];

    if (showPanel) {
      const recommendPayload = {
        level_id: levelId ?? null,
        desired_tags: {},
        limit: 10,
        user_beaten_ids: beatenIds,
        user_skills: userSkills,
      };
      requests.push(
        new Promise((resolve) =>
          chrome.runtime.sendMessage({ type: "RECOMMEND", payload: recommendPayload }, resolve)
        )
      );
    } else {
      requests.push(Promise.resolve(null));
    }

    if (showMatchBadge) {
      const matchPayload = { levelId, body: { user_skills: userSkills } };
      requests.push(
        new Promise((resolve) =>
          chrome.runtime.sendMessage({ type: "MATCH_LEVEL", payload: matchPayload }, resolve)
        )
      );
    } else {
      requests.push(Promise.resolve(null));
    }

    const [recommendResp, matchResp] = await Promise.all(requests);

    if (chrome.runtime.lastError) {
      console.warn("[GDDL Recommender] API error:", chrome.runtime.lastError);
      return;
    }

    // undefined = feature disabled (skip injection); null = enabled but no result
    const recommendations = showPanel ? (recommendResp?.data?.recommendations ?? []) : undefined;
    const matchResult = showMatchBadge ? (matchResp?.data ?? null) : undefined;
    injectPanel(recommendations, matchResult);
  }

  // --- Entry point ---
  const levelId = getCurrentLevelId();
  if (levelId) {
    fetchRecommendations(levelId);
  }
})();
