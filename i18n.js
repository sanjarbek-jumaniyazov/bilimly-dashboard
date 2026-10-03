const STRINGS = {
  uz: {
    resultGreatTitle: "Ajoyib natija! 🎉",
    resultGreatMsg: "Siz bu mavzuni mukammal bilasiz. Shu ruhda davom eting — keyingi mavzu sizni kutmoqda!",
    resultGoodTitle: "Yaxshi ish! 👍",
    resultGoodMsg: "Asosiy g'oyalarni tushunibsiz. Xatolaringizdagi izohlarni o'qib, yana bir bor urinib ko'ring — 80% dan oshish qo'lingizdan keladi.",
    resultLowTitle: "Hechqisi yo'q, bu boshlanishi! 💪",
    resultLowMsg: "Har bir xato — o'rganish imkoniyati. Keling, yana bir bor urinib ko'ramiz, lekin bu safar diqqat bilan o'qib, shoshmasdan javob beramiz.",
    resultCorrectLabel: "To'g'ri",
    resultWrongLabel: "Xato",
    welcomeTitle: "Xush kelibsiz 👋",
    welcomeSubtitle: "Davom etishdan oldin bir nechta savolga javob bering.",
    fullNameLabel: "Ism va familiya",
    fullNamePlaceholder: "Masalan: Sanjarbek Jumaniyazov",
    courseYearLabel: "Nechanchi kursda o'qiysiz?",
    yearOption: (n) => `${n}-kurs`,
    majorLabel: "Yo'nalish (major)",
    facultyLabel: "Fakultet",
    languageLabel: "Darslar qaysi tilda o'tiladi?",
    groupLabel: "Guruh",
    groupPlaceholder: "Masalan: FINTEX-21",
    continueBtn: "Davom etish",
    saveBtn: "Saqlash",
    editProfileTitle: "Profilni tahrirlash",
    editProfileLink: "✏️ Tahrirlash",
    validationError: "Iltimos, ism va guruh nomini kiriting.",

    subjectsTitle: (year) => `${year}-kurs fanlari`,
    profileLink: "👤 Profil",
    subjectsEmpty: "Bu kurs uchun hali fanlar qo'shilmagan.",
    electivesLabel: "Tanlov fanlari",
    themeCountSuffix: (n) => `${n} ta mavzu`,
    statusOpen: "Ochiq",
    statusComingSoon: "Tez orada",
    noThemesAlert: "Bu mavzu uchun savollar hozir qo'shilmoqda. Birozdan so'ng qayta urinib ko'ring.",

    chooseTheme: "Mavzuni tanlang",
    themesEmpty: "Hali mavzular yo'q.",
    questionCountSuffix: (n) => `${n} ta savol`,
    statusRead: "O'qilgan",
    statusNew: "Yangi",

    lessonSubtitle: "Avval qisqa matnlarni o'qing, keyin test topshiring",
    lessonEmpty: "Bu mavzu uchun hali matn qo'shilmagan.",
    startQuizBtn: "Testni boshlash",
    noQuizBtn: "Testlar mavjud emas",

    questionProgress: (i, total) => `Savol ${i}/${total}`,
    nextQuestionBtn: "Keyingi savol",
    finishBtn: "Yakunlash",

    resultSummary: (correct, total) => `${correct}/${total} savolga to'g'ri javob berdingiz`,
    reviewLabel: "Sharhlar",
    reviewQuestion: (i) => `Savol ${i}`,
    correctBadge: "✅ to'g'ri",
    incorrectBadge: "❌ noto'g'ri",
    backToThemesBtn: "Mavzularga qaytish",
    retryBtn: "🔄 Yana urinish",

    profileTitle: "👤 Profil",
    statThemesStarted: "boshlangan mavzu",
    statThemesMastered: "o'zlashtirilgan (80%+)",
    statTotalQuestions: "jami savollar",
    statAccuracy: "aniqlik",

    backLink: "← Orqaga",
    loadError: "Ilovani yuklashda xatolik yuz berdi.",
  },

  ru: {
    resultGreatTitle: "Отличный результат! 🎉",
    resultGreatMsg: "Вы прекрасно знаете эту тему. Продолжайте в том же духе — следующая тема уже ждёт!",
    resultGoodTitle: "Хорошая работа! 👍",
    resultGoodMsg: "Основные идеи вы поняли. Прочитайте пояснения к ошибкам и попробуйте ещё раз — 80% вам по силам.",
    resultLowTitle: "Ничего страшного, это только начало! 💪",
    resultLowMsg: "Каждая ошибка — возможность научиться. Давайте попробуем ещё раз, но в этот раз внимательнее и без спешки.",
    resultCorrectLabel: "Верно",
    resultWrongLabel: "Ошибки",
    welcomeTitle: "Добро пожаловать 👋",
    welcomeSubtitle: "Прежде чем продолжить, ответьте на несколько вопросов.",
    fullNameLabel: "Имя и фамилия",
    fullNamePlaceholder: "Например: Санжарбек Джуманиязов",
    courseYearLabel: "На каком курсе вы учитесь?",
    yearOption: (n) => `${n} курс`,
    majorLabel: "Направление (специальность)",
    facultyLabel: "Факультет",
    languageLabel: "На каком языке проходят занятия?",
    groupLabel: "Группа",
    groupPlaceholder: "Например: FINTEX-21",
    continueBtn: "Продолжить",
    saveBtn: "Сохранить",
    editProfileTitle: "Редактирование профиля",
    editProfileLink: "✏️ Редактировать",
    validationError: "Пожалуйста, укажите имя и название группы.",

    subjectsTitle: (year) => `Предметы ${year} курса`,
    profileLink: "👤 Профиль",
    subjectsEmpty: "Для этого курса пока нет предметов.",
    electivesLabel: "Предметы по выбору",
    themeCountSuffix: (n) => `тем: ${n}`,
    statusOpen: "Доступно",
    statusComingSoon: "Скоро",
    noThemesAlert: "Вопросы для этой темы сейчас добавляются. Попробуйте чуть позже.",

    chooseTheme: "Выберите тему",
    themesEmpty: "Пока нет тем.",
    questionCountSuffix: (n) => `вопросов: ${n}`,
    statusRead: "Прочитано",
    statusNew: "Новое",

    lessonSubtitle: "Сначала прочитайте короткие карточки, затем пройдите тест",
    lessonEmpty: "Для этой темы пока нет текста.",
    startQuizBtn: "Начать тест",
    noQuizBtn: "Тесты недоступны",

    questionProgress: (i, total) => `Вопрос ${i}/${total}`,
    nextQuestionBtn: "Следующий вопрос",
    finishBtn: "Завершить",

    resultSummary: (correct, total) => `Правильных ответов: ${correct}/${total}`,
    reviewLabel: "Разбор",
    reviewQuestion: (i) => `Вопрос ${i}`,
    correctBadge: "✅ верно",
    incorrectBadge: "❌ неверно",
    backToThemesBtn: "Вернуться к темам",
    retryBtn: "🔄 Попробовать ещё раз",

    profileTitle: "👤 Профиль",
    statThemesStarted: "начатых тем",
    statThemesMastered: "освоено (80%+)",
    statTotalQuestions: "всего вопросов",
    statAccuracy: "точность",

    backLink: "← Назад",
    loadError: "Ошибка при загрузке приложения.",
  },

  en: {
    resultGreatTitle: "Excellent result! 🎉",
    resultGreatMsg: "You know this topic really well. Keep it up — the next theme is waiting for you!",
    resultGoodTitle: "Good work! 👍",
    resultGoodMsg: "You've got the main ideas. Read the explanations for your mistakes and try again — 80% is within reach.",
    resultLowTitle: "No worries, this is just the start! 💪",
    resultLowMsg: "Every mistake is a chance to learn. Let's try again, but this time read carefully and take your time.",
    resultCorrectLabel: "Correct",
    resultWrongLabel: "Wrong",
    welcomeTitle: "Welcome 👋",
    welcomeSubtitle: "Before you continue, answer a few questions.",
    fullNameLabel: "Full name",
    fullNamePlaceholder: "e.g. John Smith",
    courseYearLabel: "What year are you in?",
    yearOption: (n) => `Year ${n}`,
    majorLabel: "Major",
    facultyLabel: "Faculty",
    languageLabel: "What language are your classes in?",
    groupLabel: "Group",
    groupPlaceholder: "e.g. FINTEX-21",
    continueBtn: "Continue",
    saveBtn: "Save",
    editProfileTitle: "Edit Profile",
    editProfileLink: "✏️ Edit",
    validationError: "Please enter your name and group.",

    subjectsTitle: (year) => `Year ${year} Subjects`,
    profileLink: "👤 Profile",
    subjectsEmpty: "No subjects have been added for this year yet.",
    electivesLabel: "Elective Subjects",
    themeCountSuffix: (n) => `${n} themes`,
    statusOpen: "Open",
    statusComingSoon: "Coming soon",
    noThemesAlert: "Questions for this topic are being added right now. Please check back shortly.",

    chooseTheme: "Choose a theme",
    themesEmpty: "No themes yet.",
    questionCountSuffix: (n) => `${n} questions`,
    statusRead: "Read",
    statusNew: "New",

    lessonSubtitle: "Read the short cards first, then take the quiz",
    lessonEmpty: "No lesson text has been added for this theme yet.",
    startQuizBtn: "Start quiz",
    noQuizBtn: "No quiz available",

    questionProgress: (i, total) => `Question ${i}/${total}`,
    nextQuestionBtn: "Next question",
    finishBtn: "Finish",

    resultSummary: (correct, total) => `You got ${correct}/${total} correct`,
    reviewLabel: "Review",
    reviewQuestion: (i) => `Question ${i}`,
    correctBadge: "✅ correct",
    incorrectBadge: "❌ incorrect",
    backToThemesBtn: "Back to themes",
    retryBtn: "🔄 Try again",

    profileTitle: "👤 Profile",
    statThemesStarted: "themes started",
    statThemesMastered: "mastered (80%+)",
    statTotalQuestions: "total questions",
    statAccuracy: "accuracy",

    backLink: "← Back",
    loadError: "Something went wrong loading the app.",
  },
};

const LANGUAGES = [
  { value: "uz", label: "O'zbek tili" },
  { value: "ru", label: "Русский язык" },
  { value: "en", label: "English" },
];

// Set while the student is picking a language on the registration screen,
// before it's saved to their profile — lets the form itself re-render live
// in the language they just picked.
let uiLanguageOverride = null;

function currentLang() {
  if (uiLanguageOverride === "uz" || uiLanguageOverride === "ru" || uiLanguageOverride === "en") {
    return uiLanguageOverride;
  }
  const userLang = state.user && state.user.language;
  if (userLang === "ru" || userLang === "en") return userLang;
  return "uz";
}

function t(key, ...args) {
  const dict = STRINGS[currentLang()] || STRINGS.uz;
  let value = dict[key];
  if (value === undefined) value = STRINGS.uz[key];
  if (typeof value === "function") return value(...args);
  return value;
}
