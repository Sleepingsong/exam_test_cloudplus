const state = {
  all: [],
  baseSet: [],
  filtered: [],
  current: 0,
  selected: new Set(),
  activeQuizId: null,
  activeQuizName: "",
  answers: JSON.parse(localStorage.getItem("cloudplus-answers") || "{}"),
  theme: localStorage.getItem("cloudplus-theme") || "light",
};

const els = {
  startScreen: document.getElementById("startScreen"),
  quizScreen: document.getElementById("quizScreen"),
  quizCards: document.getElementById("quizCards"),
  loading: document.getElementById("loading"),
  questionView: document.getElementById("questionView"),
  activeQuizName: document.getElementById("activeQuizName"),
  searchInput: document.getElementById("searchInput"),
  totalCount: document.getElementById("totalCount"),
  scoreCount: document.getElementById("scoreCount"),
  doneCount: document.getElementById("doneCount"),
  sourceLabel: document.getElementById("sourceLabel"),
  progressLabel: document.getElementById("progressLabel"),
  questionTitle: document.getElementById("questionTitle"),
  questionPrompt: document.getElementById("questionPrompt"),
  questionMedia: document.getElementById("questionMedia"),
  choiceList: document.getElementById("choiceList"),
  submitBtn: document.getElementById("submitBtn"),
  revealBtn: document.getElementById("revealBtn"),
  resultBox: document.getElementById("resultBox"),
  prevBtn: document.getElementById("prevBtn"),
  nextBtn: document.getElementById("nextBtn"),
  backBtn: document.getElementById("backBtn"),
  resetBtn: document.getElementById("resetBtn"),
  themeToggle: document.getElementById("themeToggle"),
};

function setTheme(theme) {
  state.theme = theme;
  document.documentElement.dataset.theme = theme;
  els.themeToggle.textContent = theme === "dark" ? "Light" : "Dark";
  localStorage.setItem("cloudplus-theme", theme);
}

function saveAnswers() {
  localStorage.setItem("cloudplus-answers", JSON.stringify(state.answers));
}

function normalize(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9+.#/\- ก-๙]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function answerKey(item) {
  return item.id;
}

function isAnswered(item) {
  return Boolean(state.answers[answerKey(item)]);
}

function hasConfirmedCurrent() {
  const item = state.filtered[state.current];
  return item ? isAnswered(item) : false;
}

function renderStartScreen() {
  const quizMap = new Map();
  state.all.forEach((item) => {
    if (!quizMap.has(item.quizId)) {
      quizMap.set(item.quizId, { id: item.quizId, name: item.quiz, count: 0 });
    }
    quizMap.get(item.quizId).count += 1;
  });

  const cards = [
    { id: "all", name: "ทำข้อสอบทั้งหมด", count: state.all.length, description: "รวมทุกชุดข้อสอบไว้ในรอบเดียว" },
    ...[...quizMap.values()].map((quiz) => ({
      ...quiz,
      description: `${quiz.count} ข้อจาก ${quiz.name}`,
    })),
  ];

  els.quizCards.innerHTML = "";
  cards.forEach((quiz) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "quiz-card";
    button.innerHTML = `
      <span>${quiz.name}</span>
      <strong>${quiz.count} ข้อ</strong>
      <small>${quiz.description}</small>
    `;
    button.addEventListener("click", () => startQuiz(quiz.id, quiz.name));
    els.quizCards.appendChild(button);
  });
}

function startQuiz(quizId, quizName) {
  state.activeQuizId = quizId;
  state.activeQuizName = quizName;
  state.baseSet = quizId === "all" ? [...state.all] : state.all.filter((item) => item.quizId === quizId);
  state.current = 0;
  state.selected = new Set();
  els.activeQuizName.textContent = quizName;
  els.searchInput.value = "";
  els.startScreen.hidden = true;
  els.quizScreen.hidden = false;
  applyFilters();
}

function backToStart() {
  els.quizScreen.hidden = true;
  els.startScreen.hidden = false;
  state.activeQuizId = null;
  state.baseSet = [];
  state.filtered = [];
  renderStartScreen();
}

function applyFilters() {
  const query = normalize(els.searchInput.value);
  state.filtered = state.baseSet.filter((item) => {
    const haystack = normalize([
      item.prompt,
      item.correctAnswerText,
      item.sourcePdf,
      item.choices.map((choice) => choice.text).join(" "),
    ].join(" "));
    return !query || haystack.includes(query);
  });
  state.current = Math.min(state.current, Math.max(0, state.filtered.length - 1));
  render();
}

function renderStats() {
  const visibleIds = new Set(state.baseSet.map((item) => item.id));
  const done = Object.entries(state.answers).filter(([id]) => visibleIds.has(id)).map(([, answer]) => answer);
  els.totalCount.textContent = state.filtered.length;
  els.doneCount.textContent = done.length;
  els.scoreCount.textContent = done.filter((answer) => answer.correct).length;
}

function renderMedia(item) {
  const media = item.media || [];
  els.questionMedia.innerHTML = "";
  els.questionMedia.hidden = media.length === 0;

  media.forEach((entry) => {
    if (entry.type !== "image") return;
    const img = document.createElement("img");
    img.src = entry.src;
    img.alt = entry.alt || "ภาพประกอบคำถาม";
    els.questionMedia.appendChild(img);
  });
}

function render() {
  renderStats();
  if (!state.filtered.length) {
    els.loading.hidden = false;
    els.loading.textContent = "ไม่พบข้อสอบตามเงื่อนไขที่เลือก";
    els.questionView.hidden = true;
    return;
  }

  const item = state.filtered[state.current];
  const saved = state.answers[answerKey(item)];
  state.selected = new Set(saved?.selected || []);

  els.loading.hidden = true;
  els.questionView.hidden = false;
  els.resultBox.hidden = true;
  els.resultBox.className = "result";
  els.sourceLabel.textContent = `${item.quiz} • ${item.sourcePdf}`;
  els.progressLabel.textContent = `${state.current + 1} / ${state.filtered.length}`;
  els.questionTitle.textContent = `ข้อ ${item.number}`;
  els.questionPrompt.textContent = item.prompt || "อ่านโจทย์จากข้อความและภาพประกอบด้านล่าง";
  renderMedia(item);
  renderChoices(item, Boolean(saved));

  els.submitBtn.disabled = state.selected.size === 0 || Boolean(saved);
  els.revealBtn.disabled = Boolean(saved);
  els.nextBtn.disabled = state.current >= state.filtered.length - 1 || !hasConfirmedCurrent();
  els.prevBtn.disabled = state.current <= 0;

  if (saved) showResult(item, saved.correct, true);
}

function renderChoices(item, locked) {
  els.choiceList.innerHTML = "";
  const saved = state.answers[answerKey(item)];
  const correctLabels = new Set(item.correctLabels || []);
  const selectedLabels = new Set(saved?.selected || state.selected);

  item.choices.forEach((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "choice";
    button.dataset.label = choice.label;
    if (selectedLabels.has(choice.label)) button.classList.add("selected");
    if (locked && correctLabels.has(choice.label)) button.classList.add("correct");
    if (locked && selectedLabels.has(choice.label) && !correctLabels.has(choice.label)) button.classList.add("wrong");
    button.disabled = locked;
    button.innerHTML = `<span class="choice-label">${escapeHtml(choice.label)}</span><span>${escapeHtml(choice.text || `Option ${choice.label}`)}</span>`;
    button.addEventListener("click", () => toggleChoice(item, choice.label));
    els.choiceList.appendChild(button);
  });
}

function toggleChoice(item, label) {
  if (isAnswered(item)) return;
  if (item.mode === "multiple") {
    state.selected.has(label) ? state.selected.delete(label) : state.selected.add(label);
  } else {
    state.selected = new Set([label]);
  }
  renderChoices(item, false);
  els.submitBtn.disabled = state.selected.size === 0;
}

function isCorrect(item) {
  const selected = [...state.selected].sort();
  const correct = [...new Set(item.correctLabels || [])].sort();
  return correct.length > 0 && selected.length === correct.length && selected.every((label, idx) => label === correct[idx]);
}

function submitAnswer() {
  const item = state.filtered[state.current];
  if (!item || state.selected.size === 0 || isAnswered(item)) return;
  const correct = isCorrect(item);
  state.answers[answerKey(item)] = { selected: [...state.selected], correct };
  saveAnswers();
  renderChoices(item, true);
  showResult(item, correct, true);
  renderStats();
  els.submitBtn.disabled = true;
  els.revealBtn.disabled = true;
  els.nextBtn.disabled = state.current >= state.filtered.length - 1;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderChoiceExplanations(item) {
  const explanations = item.choiceExplanations || {};
  const rows = item.choices
    .map((choice) => {
      const text = explanations[choice.label];
      if (!text) return "";
      const choiceText = choice.text || `Option ${choice.label}`;
      return `
        <li>
          <strong>${escapeHtml(choice.label)}. ${escapeHtml(choiceText)}</strong>
          <span>${escapeHtml(text)}</span>
        </li>
      `;
    })
    .filter(Boolean)
    .join("");

  if (!rows) return "";
  return `
    <div class="explanations">
      <h4>เหตุผลของแต่ละตัวเลือก</h4>
      <ul>${rows}</ul>
    </div>
  `;
}

function showResult(item, correct) {
  const correctText = item.correctAnswerText || item.correctAnswers.join(", ");
  const explanation = item.explanation || "คำตอบนี้เหมาะที่สุดตามแนวคิดของหัวข้อที่โจทย์ถาม";
  const selectedText = [...(state.answers[answerKey(item)]?.selected || state.selected)].join(", ") || "-";

  els.resultBox.className = `result ${correct ? "ok" : "bad"}`;
  els.resultBox.innerHTML = `
    <h3>${correct ? "ตอบถูก" : "ยังไม่ถูก"}</h3>
    <p><strong>คำตอบของคุณ:</strong> ${escapeHtml(selectedText)}</p>
    <p><strong>เฉลย:</strong> ${escapeHtml(correctText)}</p>
    <p>${escapeHtml(explanation)}</p>
    ${renderChoiceExplanations(item)}
  `;
  els.resultBox.hidden = false;
}

function revealAnswer() {
  const item = state.filtered[state.current];
  if (!item || isAnswered(item)) return;
  state.answers[answerKey(item)] = { selected: [...state.selected], correct: false, revealed: true };
  saveAnswers();
  renderChoices(item, true);
  showResult(item, false);
  renderStats();
  els.submitBtn.disabled = true;
  els.revealBtn.disabled = true;
  els.nextBtn.disabled = state.current >= state.filtered.length - 1;
}

function resetActiveAnswers() {
  const activeIds = new Set(state.baseSet.map((item) => item.id));
  Object.keys(state.answers).forEach((id) => {
    if (activeIds.has(id)) delete state.answers[id];
  });
  saveAnswers();
  render();
}

async function init() {
  setTheme(state.theme);
  const response = await fetch("data/questions.json");
  const payload = await response.json();
  state.all = payload.questions || [];
  renderStartScreen();

  els.searchInput.addEventListener("input", applyFilters);
  els.prevBtn.addEventListener("click", () => {
    state.current = Math.max(0, state.current - 1);
    render();
  });
  els.nextBtn.addEventListener("click", () => {
    if (!hasConfirmedCurrent()) return;
    state.current = Math.min(state.filtered.length - 1, state.current + 1);
    render();
  });
  els.backBtn.addEventListener("click", backToStart);
  els.submitBtn.addEventListener("click", submitAnswer);
  els.revealBtn.addEventListener("click", revealAnswer);
  els.resetBtn.addEventListener("click", resetActiveAnswers);
  els.themeToggle.addEventListener("click", () => setTheme(state.theme === "dark" ? "light" : "dark"));
}

init().catch((error) => {
  els.quizCards.innerHTML = `<div class="notice">โหลดข้อมูลไม่สำเร็จ: ${error.message}</div>`;
});
