const state = {
  all: [],
  filtered: [],
  current: 0,
  selected: new Set(),
  answers: JSON.parse(localStorage.getItem("cloudplus-answers") || "{}"),
  theme: localStorage.getItem("cloudplus-theme") || "light",
};

const els = {
  loading: document.getElementById("loading"),
  questionView: document.getElementById("questionView"),
  quizSelect: document.getElementById("quizSelect"),
  searchInput: document.getElementById("searchInput"),
  totalCount: document.getElementById("totalCount"),
  scoreCount: document.getElementById("scoreCount"),
  doneCount: document.getElementById("doneCount"),
  sourceLabel: document.getElementById("sourceLabel"),
  progressLabel: document.getElementById("progressLabel"),
  questionTitle: document.getElementById("questionTitle"),
  questionPrompt: document.getElementById("questionPrompt"),
  questionImage: document.getElementById("questionImage"),
  choiceList: document.getElementById("choiceList"),
  submitBtn: document.getElementById("submitBtn"),
  revealBtn: document.getElementById("revealBtn"),
  resultBox: document.getElementById("resultBox"),
  prevBtn: document.getElementById("prevBtn"),
  nextBtn: document.getElementById("nextBtn"),
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
  return String(value || "").toLowerCase().replace(/[^a-z0-9+.#/\- ]+/g, " ").replace(/\s+/g, " ").trim();
}

function applyFilters() {
  const quiz = els.quizSelect.value;
  const query = normalize(els.searchInput.value);
  state.filtered = state.all.filter((item) => {
    const quizOk = quiz === "all" || item.quizId === quiz;
    const haystack = normalize([
      item.prompt,
      item.correctAnswerText,
      item.sourcePdf,
      item.choices.map((choice) => choice.text).join(" "),
    ].join(" "));
    return quizOk && (!query || haystack.includes(query));
  });
  state.current = Math.min(state.current, Math.max(0, state.filtered.length - 1));
  render();
}

function renderStats() {
  const done = Object.values(state.answers);
  els.totalCount.textContent = state.filtered.length;
  els.doneCount.textContent = done.length;
  els.scoreCount.textContent = done.filter((answer) => answer.correct).length;
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
  state.selected = new Set(state.answers[item.id]?.selected || []);
  els.loading.hidden = true;
  els.questionView.hidden = false;
  els.resultBox.hidden = true;
  els.resultBox.className = "result";
  els.sourceLabel.textContent = `${item.quiz} • ${item.sourcePdf}`;
  els.progressLabel.textContent = `${state.current + 1} / ${state.filtered.length}`;
  els.questionTitle.textContent = `ข้อ ${item.number}`;
  els.questionPrompt.textContent = item.prompt || "อ่านโจทย์จากภาพต้นฉบับด้านล่าง";
  els.questionImage.src = item.questionImage;
  els.choiceList.innerHTML = "";

  item.choices.forEach((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "choice";
    button.dataset.label = choice.label;
    if (state.selected.has(choice.label)) button.classList.add("selected");
    button.innerHTML = `<span class="choice-label">${choice.label}</span><span>${choice.text || `Option ${choice.label}`}</span>`;
    button.addEventListener("click", () => toggleChoice(item, choice.label));
    els.choiceList.appendChild(button);
  });

  const saved = state.answers[item.id];
  if (saved) showResult(item, saved.correct, false);
}

function toggleChoice(item, label) {
  if (item.mode === "multiple") {
    state.selected.has(label) ? state.selected.delete(label) : state.selected.add(label);
  } else {
    state.selected = new Set([label]);
  }
  [...els.choiceList.querySelectorAll(".choice")].forEach((button) => {
    button.classList.toggle("selected", state.selected.has(button.dataset.label));
  });
}

function isCorrect(item) {
  const selected = [...state.selected].sort();
  const correct = [...new Set(item.correctLabels || [])].sort();
  return correct.length > 0 && selected.length === correct.length && selected.every((label, idx) => label === correct[idx]);
}

function submitAnswer() {
  const item = state.filtered[state.current];
  const correct = isCorrect(item);
  state.answers[item.id] = { selected: [...state.selected], correct };
  saveAnswers();
  showResult(item, correct, true);
  renderStats();
}

function showResult(item, correct, updateChoices) {
  const correctLabels = new Set(item.correctLabels || []);
  if (updateChoices) {
    [...els.choiceList.querySelectorAll(".choice")].forEach((button) => {
      const label = button.dataset.label;
      button.classList.toggle("correct", correctLabels.has(label));
      button.classList.toggle("wrong", state.selected.has(label) && !correctLabels.has(label));
    });
  }

  const explanationHtml = item.choices.map((choice) => {
    const text = item.choiceExplanations?.[choice.label] || "";
    return `<p><strong>${choice.label}.</strong> ${text}</p>`;
  }).join("");

  els.resultBox.className = `result ${correct ? "ok" : "bad"}`;
  els.resultBox.innerHTML = `
    <h3>${correct ? "ตอบถูก" : "ยังไม่ถูก"}</h3>
    <p><strong>เฉลยจากไฟล์:</strong> ${item.correctAnswerText || item.correctAnswers.join(", ")}</p>
    <img class="answer-image" src="${item.answerImage}" alt="Official answer crop from source PDF" />
    <div class="explanations">${explanationHtml}</div>
  `;
  els.resultBox.hidden = false;
}

function revealAnswer() {
  const item = state.filtered[state.current];
  showResult(item, false, true);
}

async function init() {
  setTheme(state.theme);
  const response = await fetch("data/questions.json");
  const payload = await response.json();
  state.all = payload.questions || [];

  const quizzes = [...new Map(state.all.map((item) => [item.quizId, item.quiz])).entries()];
  els.quizSelect.innerHTML = `<option value="all">ทั้งหมด</option>${quizzes.map(([id, name]) => `<option value="${id}">${name}</option>`).join("")}`;

  els.quizSelect.addEventListener("change", applyFilters);
  els.searchInput.addEventListener("input", applyFilters);
  els.prevBtn.addEventListener("click", () => {
    state.current = Math.max(0, state.current - 1);
    render();
  });
  els.nextBtn.addEventListener("click", () => {
    state.current = Math.min(state.filtered.length - 1, state.current + 1);
    render();
  });
  els.submitBtn.addEventListener("click", submitAnswer);
  els.revealBtn.addEventListener("click", revealAnswer);
  els.resetBtn.addEventListener("click", () => {
    state.answers = {};
    saveAnswers();
    render();
  });
  els.themeToggle.addEventListener("click", () => setTheme(state.theme === "dark" ? "light" : "dark"));
  applyFilters();
}

init().catch((error) => {
  els.loading.textContent = `โหลดข้อมูลไม่สำเร็จ: ${error.message}`;
});
