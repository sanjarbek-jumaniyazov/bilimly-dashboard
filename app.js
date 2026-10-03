const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
if (tg) {
  tg.ready();
  tg.expand();
}

// Mobile WebViews (especially iOS) don't reliably size `100vh` to the
// actually-visible area once Telegram's own chrome is accounted for.
// Drive our full-height layout from Telegram's own viewport value instead,
// with window.innerHeight as the fallback outside Telegram.
function syncViewportHeight() {
  const h = (tg && tg.viewportStableHeight) || (tg && tg.viewportHeight) || window.innerHeight;
  document.documentElement.style.setProperty("--tg-vh", h + "px");
}
syncViewportHeight();
window.addEventListener("resize", syncViewportHeight);
if (tg && tg.onEvent) {
  tg.onEvent("viewportChanged", syncViewportHeight);
}

const root = document.getElementById("app");

const state = {
  user: null,
  majors: [],
};

const navStack = [];

function localizedMajorField(major, field) {
  const lang = currentLang();
  if (lang === "ru" && major[`${field}_ru`]) return major[`${field}_ru`];
  if (lang === "en" && major[`${field}_en`]) return major[`${field}_en`];
  return major[field];
}

function el(html) {
  const wrapper = document.createElement("div");
  wrapper.innerHTML = html.trim();
  return wrapper.firstElementChild;
}

function hapticSelect() {
  if (tg && tg.HapticFeedback) tg.HapticFeedback.selectionChanged();
}
function hapticNotify(type) {
  if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred(type);
}

function renderScreen(contentNode, { onBack, actionLabel, onAction, actionEnabled = true } = {}) {
  root.dataset.booted = "1";
  root.innerHTML = "";

  if (tg) {
    if (onBack) {
      tg.BackButton.offClick(renderScreen._lastBack);
      renderScreen._lastBack = onBack;
      tg.BackButton.onClick(onBack);
      tg.BackButton.show();
    } else {
      tg.BackButton.hide();
    }
  }

  const wrap = document.createElement("div");
  wrap.className = "screen";
  wrap.appendChild(contentNode);

  if (Api.isDebugMode && onBack) {
    const backLink = el(`<div class="profile-link" style="margin-bottom:12px;">${t("backLink")}</div>`);
    backLink.addEventListener("click", onBack);
    wrap.insertBefore(backLink, wrap.firstChild);
  }

  root.appendChild(wrap);

  if (actionLabel && onAction) {
    const bar = el(`
      <div class="action-bar">
        <button class="btn-primary" ${actionEnabled ? "" : "disabled"}>${actionLabel}</button>
      </div>
    `);
    const btn = bar.querySelector("button");
    btn.addEventListener("click", onAction);
    root.appendChild(bar);
  }

  if (Api.isDebugMode) {
    root.appendChild(el(`<div class="debug-banner">DEV MODE — debug auth (not inside Telegram)</div>`));
  }
}

function navigate(renderFn, params) {
  navStack.push({ renderFn, params });
  renderFn(params);
}

function goBack() {
  navStack.pop(); // current screen
  const prev = navStack.pop();
  if (prev) {
    navigate(prev.renderFn, prev.params);
  } else {
    navigate(screenSubjects);
  }
}

function showError(message) {
  root.dataset.booted = "1";
  root.innerHTML = "";
  root.appendChild(
    el(`<div class="screen"><div class="empty-state">⚠️ ${message}</div></div>`)
  );
}

// --- Boot ----------------------------------------------------------------

async function boot() {
  try {
    const [user, majors] = await Promise.all([Api.getMe(), Api.listMajors()]);
    state.user = user;
    state.majors = majors;
    if (!user.is_onboarded) {
      navigate(screenRegister);
    } else {
      navigate(screenSubjects);
    }
  } catch (err) {
    showError(err.message || t("loadError"));
  }
}

// --- Registration ----------------------------------------------------------

function screenRegister({ isEdit = false } = {}) {
  const major = state.majors[0]; // only one major supported for now
  const defaultMajor = state.majors.find((m) => m.id === state.user.major_id) || major;
  const draft =
    screenRegister._draft ||
    (isEdit
      ? {
          full_name: state.user.full_name || "",
          course_year: String(state.user.course_year || 1),
          major_id: String(state.user.major_id || (defaultMajor ? defaultMajor.id : "")),
          faculty: state.user.faculty || (defaultMajor ? localizedMajorField(defaultMajor, "faculty") : ""),
          language: uiLanguageOverride || state.user.language || "uz",
          group_name: state.user.group_name || "",
        }
      : {
          full_name: state.user.full_name || "",
          course_year: "1",
          major_id: String(major ? major.id : ""),
          faculty: major ? localizedMajorField(major, "faculty") : "",
          language: uiLanguageOverride || "uz",
          group_name: "",
        });

  const content = el(`
    <div>
      <div class="brand-row">
        <img src="/assets/logo.jpg" alt="Bilimly" class="brand-logo" />
        <div class="brand-name">Bilimly</div>
      </div>
      <h1>${isEdit ? t("editProfileTitle") : t("welcomeTitle")}</h1>
      ${isEdit ? "" : `<p class="subtitle">${t("welcomeSubtitle")}</p>`}

      <div class="field">
        <label>${t("fullNameLabel")}</label>
        <input type="text" id="f-name" placeholder="${t("fullNamePlaceholder")}" value="${draft.full_name}" />
      </div>

      <div class="field">
        <label>${t("courseYearLabel")}</label>
        <select id="f-year">
          ${[1, 2, 3, 4]
            .map(
              (n) =>
                `<option value="${n}" ${String(n) === draft.course_year ? "selected" : ""}>${t("yearOption", n)}</option>`
            )
            .join("")}
        </select>
      </div>

      <div class="field">
        <label>${t("majorLabel")}</label>
        <select id="f-major">
          ${state.majors
            .map(
              (m) =>
                `<option value="${m.id}" ${String(m.id) === draft.major_id ? "selected" : ""}>${localizedMajorField(m, "name")}</option>`
            )
            .join("")}
        </select>
      </div>

      <div class="field">
        <label>${t("facultyLabel")}</label>
        <input type="text" id="f-faculty" value="${draft.faculty}" />
      </div>

      <div class="field">
        <label>${t("languageLabel")}</label>
        <select id="f-lang">
          ${LANGUAGES.map(
            (l) => `<option value="${l.value}" ${l.value === draft.language ? "selected" : ""}>${l.label}</option>`
          ).join("")}
        </select>
      </div>

      <div class="field">
        <label>${t("groupLabel")}</label>
        <input type="text" id="f-group" placeholder="${t("groupPlaceholder")}" value="${draft.group_name}" />
      </div>
    </div>
  `);

  const majorSelect = content.querySelector("#f-major");
  const facultyInput = content.querySelector("#f-faculty");
  const langSelect = content.querySelector("#f-lang");

  majorSelect.addEventListener("change", () => {
    const m = state.majors.find((x) => String(x.id) === majorSelect.value);
    if (m) facultyInput.value = localizedMajorField(m, "faculty");
  });

  function saveDraft() {
    screenRegister._draft = {
      full_name: content.querySelector("#f-name").value,
      course_year: content.querySelector("#f-year").value,
      major_id: majorSelect.value,
      faculty: facultyInput.value,
      language: langSelect.value,
      group_name: content.querySelector("#f-group").value,
    };
  }

  langSelect.addEventListener("change", () => {
    saveDraft();
    uiLanguageOverride = langSelect.value;
    // re-sync the faculty field to the new language's wording for the selected major
    const m = state.majors.find((x) => String(x.id) === screenRegister._draft.major_id);
    if (m) screenRegister._draft.faculty = localizedMajorField(m, "faculty");
    hapticSelect();
    screenRegister({ isEdit });
  });

  async function submit() {
    saveDraft();
    const d = screenRegister._draft;
    const payload = {
      full_name: d.full_name.trim(),
      course_year: parseInt(d.course_year, 10),
      major_id: parseInt(d.major_id, 10),
      faculty: d.faculty.trim(),
      language: d.language,
      group_name: d.group_name.trim(),
    };
    if (!payload.full_name || !payload.group_name) {
      hapticNotify("error");
      alert(t("validationError"));
      return;
    }
    try {
      state.user = await Api.updateMe(payload);
      uiLanguageOverride = null; // state.user.language now takes over
      screenRegister._draft = null;
      hapticNotify("success");
      navStack.length = 0;
      navigate(isEdit ? screenProfile : screenSubjects);
    } catch (err) {
      showError(err.message);
    }
  }

  renderScreen(content, {
    onBack: isEdit
      ? () => {
          uiLanguageOverride = null;
          screenRegister._draft = null;
          goBack();
        }
      : undefined,
    actionLabel: isEdit ? t("saveBtn") : t("continueBtn"),
    onAction: submit,
  });
}

// --- Subjects ----------------------------------------------------------

async function screenSubjects() {
  renderScreen(el(`<div class="loading-screen" style="height:40vh;"><div class="spinner"></div></div>`));
  try {
    const subjects = await Api.listSubjects();
    const mandatory = subjects.filter((s) => !s.is_elective);
    const electives = subjects.filter((s) => s.is_elective);

    const content = el(`
      <div>
        <div class="top-row">
          <div class="brand-row">
            <img src="/assets/logo.jpg" alt="Bilimly" class="brand-logo small" />
            <h1>${t("subjectsTitle", state.user.course_year)}</h1>
          </div>
          <div class="profile-link" id="profile-link">${t("profileLink")}</div>
        </div>
        <p class="subtitle">${state.user.major_name || ""}</p>
        <div id="mandatory-list"></div>
      </div>
    `);

    const list = content.querySelector("#mandatory-list");
    if (mandatory.length === 0 && electives.length === 0) {
      list.appendChild(el(`<div class="empty-state">${t("subjectsEmpty")}</div>`));
    }
    mandatory.forEach((s) => list.appendChild(subjectCard(s)));

    if (electives.length > 0) {
      content.appendChild(el(`<div class="section-label">${t("electivesLabel")}</div>`));
      electives.forEach((s) => content.appendChild(subjectCard(s)));
    }

    content.querySelector("#profile-link").addEventListener("click", () => navigate(screenProfile));

    navStack.length = 0;
    navStack.push({ renderFn: screenSubjects });
    renderScreen(content);
  } catch (err) {
    showError(err.message);
  }
}

function subjectCard(subject) {
  const card = el(`
    <div class="card tappable">
      <div>
        <div class="card-title">${subject.name}</div>
        <div class="card-meta">${subject.track ? subject.track + " · " : ""}${t("themeCountSuffix", subject.theme_count)}</div>
      </div>
      <div class="badge ${subject.is_elective ? "elective" : ""}">${subject.theme_count > 0 ? t("statusOpen") : t("statusComingSoon")}</div>
    </div>
  `);
  card.addEventListener("click", () => {
    hapticSelect();
    if (subject.theme_count === 0) {
      alert(t("noThemesAlert"));
      return;
    }
    navigate(screenThemes, { subject });
  });
  return card;
}

// --- Themes ----------------------------------------------------------

async function screenThemes({ subject }) {
  renderScreen(el(`<div class="loading-screen" style="height:40vh;"><div class="spinner"></div></div>`), {
    onBack: goBack,
  });
  try {
    const data = await Api.listThemes(subject.id);
    const content = el(`
      <div>
        <h1>${subject.name}</h1>
        <p class="subtitle">${t("chooseTheme")}</p>
        <div id="theme-list"></div>
      </div>
    `);
    const list = content.querySelector("#theme-list");
    if (data.themes.length === 0) {
      list.appendChild(el(`<div class="empty-state">${t("themesEmpty")}</div>`));
    }
    data.themes.forEach((th, i) => {
      const card = el(`
        <div class="card tappable">
          <div>
            <div class="card-title">${i + 1}. ${th.title}</div>
          </div>
          <div class="badge ${th.best_score >= 80 ? "done" : ""}">${th.best_score > 0 ? th.best_score + "%" : t("statusNew")}</div>
        </div>
      `);
      card.addEventListener("click", () => {
        hapticSelect();
        if (!th.has_questions) {
          alert(t("noThemesAlert"));
          return;
        }
        navigate(screenQuiz, { theme: th, subject });
      });
      list.appendChild(card);
    });
    renderScreen(content, { onBack: goBack });
  } catch (err) {
    showError(err.message);
  }
}

// --- Quiz ----------------------------------------------------------

async function screenQuiz({ theme, subject }) {
  renderScreen(el(`<div class="loading-screen" style="height:40vh;"><div class="spinner"></div></div>`), {
    onBack: goBack,
  });
  try {
    const questions = await Api.getQuiz(theme.id);
    const quizState = { questions, index: 0, answers: [], correctCount: 0 };
    renderQuizQuestion({ theme, subject, quizState });
  } catch (err) {
    showError(err.message);
  }
}

function renderQuizQuestion({ theme, subject, quizState }) {
  const q = quizState.questions[quizState.index];
  const total = quizState.questions.length;
  let answered = false;
  let selectedIndex = null;

  const content = el(`
    <div>
      <div class="quiz-progress">
        ${quizState.questions
          .map((_, i) => `<div class="quiz-progress-dot ${i <= quizState.index ? "done" : ""}"></div>`)
          .join("")}
      </div>
      <p class="subtitle">${t("questionProgress", quizState.index + 1, total)}</p>
      ${q.image_url ? `<img src="${q.image_url}" class="question-image" alt="" />` : ""}
      <div class="question-text">${q.text}</div>
      <div id="options"></div>
      <div id="feedback"></div>
    </div>
  `);

  const optionsWrap = content.querySelector("#options");
  const feedbackWrap = content.querySelector("#feedback");

  function selectOption(idx) {
    if (answered) return;
    answered = true;
    selectedIndex = idx;
    const isCorrect = idx === q.correct_index;
    if (isCorrect) quizState.correctCount += 1;

    const items = q.option_images
      ? optionsWrap.querySelectorAll(".option-image-card")
      : optionsWrap.querySelectorAll(".option");
    items.forEach((o, i) => {
      if (q.option_images) {
        o.classList.add("locked");
      } else {
        o.disabled = true;
      }
      if (i === q.correct_index) o.classList.add("correct");
      else if (i === idx) o.classList.add("incorrect");
      else o.classList.add("dimmed");
    });

    if (q.explanation) {
      feedbackWrap.appendChild(
        el(`<div class="explanation">${isCorrect ? t("correctBadge") : t("incorrectBadge")} — ${q.explanation}</div>`)
      );
    }

    hapticNotify(isCorrect ? "success" : "error");
    updateActionButton();
  }

  if (q.option_images) {
    const grid = el(`<div class="option-images"></div>`);
    q.option_images.forEach((imgUrl, idx) => {
      const caption = q.options[idx] || "";
      const card = el(`
        <div class="option-image-card">
          <img src="${imgUrl}" alt="" />
          ${caption ? `<div class="caption">${caption}</div>` : ""}
        </div>
      `);
      card.addEventListener("click", () => selectOption(idx));
      grid.appendChild(card);
    });
    optionsWrap.appendChild(grid);
  } else {
    q.options.forEach((opt, idx) => {
      const btn = el(`<button class="option">${opt}</button>`);
      btn.addEventListener("click", () => selectOption(idx));
      optionsWrap.appendChild(btn);
    });
  }

  function updateActionButton() {
    const isLast = quizState.index === total - 1;
    renderScreen(content, {
      onBack: goBack,
      actionLabel: isLast ? t("finishBtn") : t("nextQuestionBtn"),
      actionEnabled: answered,
      onAction: () => {
        quizState.answers.push({ question_id: q.id, selected_index: selectedIndex });
        if (isLast) {
          submitQuiz({ theme, subject, quizState });
        } else {
          quizState.index += 1;
          renderQuizQuestion({ theme, subject, quizState });
        }
      },
    });
  }

  updateActionButton();
}

async function submitQuiz({ theme, subject, quizState }) {
  renderScreen(el(`<div class="loading-screen" style="height:40vh;"><div class="spinner"></div></div>`));
  try {
    const result = await Api.submitQuiz(theme.id, quizState.answers);
    hapticNotify(result.score_pct >= 60 ? "success" : "warning");
    navigate(screenResult, { theme, subject, result });
  } catch (err) {
    showError(err.message);
  }
}

// --- Result ----------------------------------------------------------

function screenResult({ theme, subject, result }) {
  const pct = result.score_pct;
  const tier = pct >= 80 ? "great" : pct >= 60 ? "good" : "low";
  const titles = { great: t("resultGreatTitle"), good: t("resultGoodTitle"), low: t("resultLowTitle") };
  const msgs = { great: t("resultGreatMsg"), good: t("resultGoodMsg"), low: t("resultLowMsg") };
  const wrong = result.total - result.correct_count;
  const R = 54, C = 2 * Math.PI * R;

  const content = el(`
    <div class="result-wrap tier-${tier}">
      <canvas id="confetti" class="confetti"></canvas>
      <div class="result-hero">
        <div class="result-ring">
          <svg viewBox="0 0 128 128" width="150" height="150">
            <circle class="ring-bg" cx="64" cy="64" r="${R}" />
            <circle class="ring-fg" cx="64" cy="64" r="${R}"
              style="stroke-dasharray:${C};stroke-dashoffset:${C};" data-target="${C * (1 - pct / 100)}" />
          </svg>
          <div class="ring-label"><span class="ring-pct">0%</span></div>
        </div>
        <h1 class="result-title">${titles[tier]}</h1>
        <p class="result-msg">${msgs[tier]}</p>
        <div class="result-stats">
          <div class="stat-pill ok"><span class="stat-num">${result.correct_count}</span><span class="stat-lbl">${t("resultCorrectLabel")}</span></div>
          <div class="stat-pill ko"><span class="stat-num">${wrong}</span><span class="stat-lbl">${t("resultWrongLabel")}</span></div>
        </div>
        <div class="profile-link" id="back-to-themes-link">${t("backToThemesBtn")}</div>
      </div>
    </div>
  `);

  content.querySelector("#back-to-themes-link").addEventListener("click", () => {
    navStack.length = 0;
    navigate(screenThemes, { subject });
  });

  renderScreen(content, {
    actionLabel: t("retryBtn"),
    onAction: () => {
      navStack.length = 0;
      navigate(screenQuiz, { theme, subject });
    },
  });

  // Animate the ring and the counter once the node is in the DOM.
  requestAnimationFrame(() => {
    const fg = content.querySelector(".ring-fg");
    fg.style.strokeDashoffset = fg.dataset.target;
    const label = content.querySelector(".ring-pct");
    const t0 = performance.now(), dur = 1100;
    (function tick(now) {
      const k = Math.min(1, (now - t0) / dur);
      const eased = 1 - Math.pow(1 - k, 3);
      label.textContent = Math.round(pct * eased) + "%";
      if (k < 1) requestAnimationFrame(tick);
    })(t0);
    // Guarantee the final value even if animation frames are throttled.
    setTimeout(() => { label.textContent = pct + "%"; }, dur + 100);
  });

  hapticNotify(tier === "low" ? "warning" : "success");
  if (tier === "great") launchConfetti(content.querySelector("#confetti"));
}

// Lightweight confetti burst (no dependencies) for the ≥80% result screen.
function launchConfetti(canvas) {
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const W = (canvas.width = canvas.offsetWidth * dpr);
  const H = (canvas.height = canvas.offsetHeight * dpr);
  const colors = ["#58cc02", "#1cb0f6", "#ffc800", "#ff4b4b", "#ce82ff", "#ff9600"];
  const parts = Array.from({ length: 140 }, () => ({
    x: W / 2 + (Math.random() - 0.5) * W * 0.4,
    y: H * 0.35,
    vx: (Math.random() - 0.5) * 14 * dpr,
    vy: (-Math.random() * 16 - 6) * dpr,
    w: (6 + Math.random() * 6) * dpr,
    h: (8 + Math.random() * 8) * dpr,
    rot: Math.random() * Math.PI,
    vr: (Math.random() - 0.5) * 0.3,
    color: colors[Math.floor(Math.random() * colors.length)],
  }));
  const g = 0.45 * dpr;
  const t0 = performance.now();
  (function frame(now) {
    const elapsed = now - t0;
    ctx.clearRect(0, 0, W, H);
    for (const p of parts) {
      p.vy += g; p.x += p.vx; p.y += p.vy; p.vx *= 0.99; p.rot += p.vr;
      ctx.save();
      ctx.translate(p.x, p.y); ctx.rotate(p.rot);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = Math.max(0, 1 - elapsed / 2600);
      ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
      ctx.restore();
    }
    if (elapsed < 2800) requestAnimationFrame(frame);
    else ctx.clearRect(0, 0, W, H);
  })(t0);
}

// --- Profile ----------------------------------------------------------

async function screenProfile() {
  renderScreen(el(`<div class="loading-screen" style="height:40vh;"><div class="spinner"></div></div>`), {
    onBack: goBack,
  });
  try {
    const progress = await Api.getProgress();
    const u = state.user;
    const content = el(`
      <div>
        <div class="top-row">
          <h1>${t("profileTitle")}</h1>
          <div class="profile-link" id="edit-profile-link">${t("editProfileLink")}</div>
        </div>
        <div class="card">
          <div class="card-title">${u.full_name}</div>
          <div class="card-meta">${t("yearOption", u.course_year)} · ${u.group_name || "-"}</div>
          <div class="card-meta">${u.major_name || ""}</div>
          <div class="card-meta">${u.faculty || ""}</div>
        </div>
        <div class="stat-grid">
          <div class="stat-box"><div class="num">${progress.themes_started}</div><div class="label">${t("statThemesStarted")}</div></div>
          <div class="stat-box"><div class="num">${progress.themes_mastered}</div><div class="label">${t("statThemesMastered")}</div></div>
          <div class="stat-box"><div class="num">${progress.total_attempts}</div><div class="label">${t("statTotalQuestions")}</div></div>
          <div class="stat-box"><div class="num">${progress.total_attempts ? Math.round((100 * progress.correct_attempts) / progress.total_attempts) : 0}%</div><div class="label">${t("statAccuracy")}</div></div>
        </div>
      </div>
    `);
    content.querySelector("#edit-profile-link").addEventListener("click", () => {
      hapticSelect();
      screenRegister._draft = null;
      navigate(screenRegister, { isEdit: true });
    });
    renderScreen(content, { onBack: goBack });
  } catch (err) {
    showError(err.message);
  }
}

boot();
