const Api = (() => {
  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
  const initData = tg && tg.initData ? tg.initData : "";

  // Dev-mode fallback so the mini app is testable in a regular browser
  // (outside Telegram) against a backend started with DEBUG_AUTH=true.
  function debugId() {
    let id = localStorage.getItem("debug_telegram_id");
    if (!id) {
      id = String(900000000 + Math.floor(Math.random() * 99999999));
      localStorage.setItem("debug_telegram_id", id);
    }
    return id;
  }

  const isDebugMode = !initData;

  async function request(path, options = {}) {
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    let url = path;

    // Try both headers and query params for compatibility with mobile WebViews
    if (initData) {
      headers["X-Telegram-Init-Data"] = initData;
    } else {
      headers["X-Debug-Telegram-Id"] = debugId();
      // Also add as query param for mobile WebViews that block custom headers
      url = path + (path.includes("?") ? "&" : "?") + "debug_id=" + encodeURIComponent(debugId());
    }

    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      const err = new Error(body.detail || `Request failed: ${res.status}`);
      err.status = res.status;
      throw err;
    }
    return res.json();
  }

  return {
    isDebugMode,
    getMe: () => request("/api/me"),
    updateMe: (payload) => request("/api/me", { method: "PUT", body: JSON.stringify(payload) }),
    listMajors: () => request("/api/majors"),
    listSubjects: () => request("/api/subjects"),
    listThemes: (subjectId) => request(`/api/subjects/${subjectId}/themes`),
    getQuiz: (themeId) => request(`/api/themes/${themeId}/quiz`),
    submitQuiz: (themeId, answers) =>
      request(`/api/themes/${themeId}/quiz/submit`, {
        method: "POST",
        body: JSON.stringify({ answers }),
      }),
    getProgress: () => request("/api/progress"),
  };
})();
