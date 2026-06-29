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
  shuffleQuestions: false,
  shuffleChoices: false,
};

const els = {
  startScreen: document.getElementById("startScreen"),
  quizScreen: document.getElementById("quizScreen"),
  startForm: document.getElementById("startForm"),
  quizSelect: document.getElementById("quizSelect"),
  shuffleQuestions: document.getElementById("shuffleQuestions"),
  shuffleChoices: document.getElementById("shuffleChoices"),
  loading: document.getElementById("loading"),
  questionView: document.getElementById("questionView"),
  sourceLabel: document.getElementById("sourceLabel"),
  progressLabel: document.getElementById("progressLabel"),
  questionTitle: document.getElementById("questionTitle"),
  questionPrompt: document.getElementById("questionPrompt"),
  selectionHint: document.getElementById("selectionHint"),
  questionMedia: document.getElementById("questionMedia"),
  choiceList: document.getElementById("choiceList"),
  resultBox: document.getElementById("resultBox"),
  prevBtn: document.getElementById("prevBtn"),
  nextBtn: document.getElementById("nextBtn"),
  themeToggle: document.getElementById("themeToggle"),
};

const glossary = {
  "IaaS": "Infrastructure as a Service - บริการโครงสร้างพื้นฐานไอที (เช่น เซิร์ฟเวอร์, สตอเรจ, เครือข่าย) บนคลาวด์",
  "PaaS": "Platform as a Service - บริการแพลตฟอร์มสำหรับนักพัฒนา (เช่น ฐานข้อมูล, รันไทม์) เพื่อสร้างแอปพลิเคชัน",
  "SaaS": "Software as a Service - บริการซอฟต์แวร์ที่ใช้งานผ่านอินเทอร์เน็ตโดยไม่ต้องติดตั้ง",
  "VPC": "Virtual Private Cloud - เครือข่ายส่วนตัวเสมือนในระบบคลาวด์ที่แยกขาดจากลูกค้ารายอื่น",
  "SLA": "Service Level Agreement - ข้อตกลงระดับบริการระหว่างผู้ให้บริการและลูกค้าที่ระบุคุณภาพและ Uptime",
  "HA": "High Availability - ความพร้อมใช้งานสูง ระบบที่ออกแบบมาให้ทำงานต่อเนื่องและลด Downtime",
  "Scalability": "ความสามารถของระบบในการขยาย (Scale-up) หรือเพิ่มจำนวน (Scale-out) เพื่อรองรับโหลด",
  "Elasticity": "ความยืดหยุ่นในการเพิ่มหรือลดทรัพยากรคลาวด์แบบอัตโนมัติตามปริมาณการใช้งานจริง",
  "Hypervisor": "ซอฟต์แวร์หรือฮาร์ดแวร์ที่ใช้สร้างและบริหารจัดการ Virtual Machines (VMs)",
  "VPN": "Virtual Private Network - เครือข่ายส่วนตัวเสมือนที่เข้ารหัสข้อมูลระหว่างการส่ง",
  "CDN": "Content Delivery Network - เครือข่ายเซิร์ฟเวอร์กระจายทั่วโลกเพื่อส่งเนื้อหาให้ผู้ใช้ได้รวดเร็วขึ้น",
  "IAM": "Identity and Access Management - ระบบบริหารจัดการตัวตนและสิทธิ์การเข้าถึงทรัพยากร",
  "Load Balancer": "ตัวกระจายโหลด หรือการส่งทราฟฟิกเครือข่ายไปยังเซิร์ฟเวอร์หลายตัวให้สมดุล",
  "BCP": "Business Continuity Plan - แผนความต่อเนื่องทางธุรกิจ เพื่อให้องค์กรทำงานต่อได้เมื่อมีเหตุขัดข้อง",
  "RTO": "Recovery Time Objective - ระยะเวลาสูงสุดที่ยอมรับได้ในการกู้คืนระบบหลังเกิดเหตุ",
  "RPO": "Recovery Point Objective - ปริมาณข้อมูลเป้าหมาย (ระยะเวลา) ที่ยอมรับได้หากสูญหาย",
  "DRP": "Disaster Recovery Plan - แผนรับมือภัยพิบัติและขั้นตอนกู้คืนระบบไอที",
  "WAF": "Web Application Firewall - ไฟร์วอลล์สำหรับป้องกันแอปพลิเคชันเว็บจากการโจมตี (เช่น SQLi, XSS)",
  "API": "Application Programming Interface - ช่องทางหรือโปรโตคอลให้ซอฟต์แวร์สื่อสารกันได้",
  "CASB": "Cloud Access Security Broker - จุดควบคุมนโยบายความปลอดภัยระหว่างผู้ใช้งานกับระบบคลาวด์",
  "DDoS": "Distributed Denial of Service - การโจมตีโดยส่งทราฟฟิกมหาศาลจากหลายเครื่องเพื่อให้ระบบล่ม",
  "SAN": "Storage Area Network - เครือข่ายความเร็วสูงเฉพาะทางสำหรับจัดเก็บข้อมูลแบบ Block",
  "NAS": "Network Attached Storage - อุปกรณ์หรือระบบแชร์ไฟล์ในเครือข่าย (File-level storage)",
  "IOPS": "Input/Output Operations Per Second - หน่วยวัดประสิทธิภาพความเร็วในการอ่าน/เขียนของ Storage",
  "CI\/CD": "Continuous Integration / Continuous Deployment - กระบวนการทดสอบและปล่อยซอฟต์แวร์แบบอัตโนมัติ",
  "SDN": "Software-Defined Networking - การจัดการเครือข่ายโดยแยกส่วนควบคุม (Control Plane) ไปอยู่ที่ซอฟต์แวร์",
  "VDI": "Virtual Desktop Infrastructure - โครงสร้างพื้นฐานสำหรับให้บริการเดสก์ท็อปเสมือน (Virtual Desktop)",
  "IP tables": "โปรแกรมสำหรับผู้ดูแลระบบ เพื่อกำหนดค่า firewall ของ Linux kernel",
  "Remediation": "การแก้ไข หรือการบรรเทาความเสี่ยงจากช่องโหว่",
  "Vulnerability": "ช่องโหว่ หรือจุดอ่อนในระบบที่อาจถูกนำไปใช้โจมตีได้",
  "Assessment": "การประเมิน ตรวจสอบ หรือวิเคราะห์หาความเสี่ยง"
};

function highlightTerms(text) {
  let result = escapeHtml(text || "");
  for (const [term, def] of Object.entries(glossary)) {
    const regex = new RegExp(`\\b${term}\\b`, "gi");
    result = result.replace(regex, `<span class="term-highlight" data-tooltip="${def}">$&</span>`);
  }
  return result;
}

function shuffleArray(array) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

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

function requiredSelections(item) {
  return Math.max(1, new Set(item.correctLabels || []).size || (item.mode === "multiple" ? 2 : 1));
}

function hasEnoughSelections(item) {
  return state.selected.size === requiredSelections(item);
}

function clearAnswersFor(items) {
  items.forEach((item) => delete state.answers[answerKey(item)]);
  saveAnswers();
}

function updateSelectionHint(item) {
  const required = requiredSelections(item);
  els.selectionHint.textContent =
    required > 1
      ? `เลือกคำตอบให้ครบ ${required} ข้อ - เลือกแล้ว ${state.selected.size} / ${required}`
      : "เลือกคำตอบ 1 ข้อ แล้วกดยืนยัน";
}

function renderStartScreen() {
  const quizMap = new Map();
  state.all.forEach((item) => {
    if (!quizMap.has(item.quizId)) {
      quizMap.set(item.quizId, { id: item.quizId, name: item.quiz, count: 0 });
    }
    quizMap.get(item.quizId).count += 1;
  });

  const options = [
    { id: "all", name: "ทำข้อสอบทั้งหมด", count: state.all.length },
    ...[...quizMap.values()].map((quiz) => ({
      ...quiz,
    })),
  ];

  els.quizSelect.innerHTML = "";
  options.forEach((quiz) => {
    const option = document.createElement("option");
    option.value = quiz.id;
    option.textContent = `${quiz.name} (${quiz.count} ข้อ)`;
    els.quizSelect.appendChild(option);
  });
}

function startQuiz(quizId, quizName) {
  state.activeQuizId = quizId;
  state.activeQuizName = quizName;
  state.baseSet = quizId === "all" ? [...state.all] : state.all.filter((item) => item.quizId === quizId);
  clearAnswersFor(state.baseSet);
  state.current = 0;
  state.selected = new Set();
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
  let filtered = [...state.baseSet];
  if (state.shuffleQuestions) {
    filtered = shuffleArray(filtered);
  }
  state.filtered = filtered;
  state.current = 0;
  render();
}

function renderStats() {
  return Object.entries(state.answers)
    .filter(([id]) => state.baseSet.some((item) => item.id === id))
    .map(([, answer]) => answer);
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
  els.questionPrompt.innerHTML = highlightTerms(item.prompt) || "อ่านโจทย์จากข้อความและภาพประกอบด้านล่าง";
  updateSelectionHint(item);
  renderMedia(item);
  renderChoices(item, Boolean(saved));

  els.nextBtn.disabled = state.current >= state.filtered.length - 1 || !hasConfirmedCurrent();
  els.prevBtn.disabled = state.current <= 0;

  if (saved) showResult(item, saved.correct, true);
}

function renderChoices(item, locked) {
  els.choiceList.innerHTML = "";
  const saved = state.answers[answerKey(item)];
  const correctLabels = new Set(item.correctLabels || []);
  const selectedLabels = new Set(saved?.selected || state.selected);
  const maxSelections = requiredSelections(item);
  const limitReached = !locked && maxSelections > 1 && selectedLabels.size >= maxSelections;

  if (state.shuffleChoices && !item.shuffledChoices) {
    const originalLabels = item.choices.map(c => c.label);
    const shuffledItems = shuffleArray(item.choices);
    item.shuffledChoices = shuffledItems.map((choice, index) => ({
      ...choice,
      displayLabel: originalLabels[index]
    }));
  } else if (!state.shuffleChoices && !item.shuffledChoices) {
    item.shuffledChoices = item.choices.map(c => ({...c, displayLabel: c.label}));
  }
  
  const choicesToRender = item.shuffledChoices || item.choices;

  choicesToRender.forEach((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "choice";
    button.dataset.label = choice.label;
    if (selectedLabels.has(choice.label)) button.classList.add("selected");
    if (locked && correctLabels.has(choice.label)) button.classList.add("correct");
    if (locked && selectedLabels.has(choice.label) && !correctLabels.has(choice.label)) button.classList.add("wrong");
    if (limitReached && !selectedLabels.has(choice.label)) button.classList.add("limited");
    button.disabled = locked || (limitReached && !selectedLabels.has(choice.label));
    button.innerHTML = `<span class="choice-label">${escapeHtml(choice.displayLabel || choice.label)}</span><span>${escapeHtml(choice.text || `Option ${choice.label}`)}</span>`;
    button.addEventListener("click", () => toggleChoice(item, choice.label));
    els.choiceList.appendChild(button);
  });
}

function toggleChoice(item, label) {
  if (isAnswered(item)) return;
  const maxSelections = requiredSelections(item);
  if (maxSelections > 1) {
    if (state.selected.has(label)) {
      state.selected.delete(label);
    } else if (state.selected.size < maxSelections) {
      state.selected.add(label);
    }
  } else {
    state.selected = new Set([label]);
  }
  renderChoices(item, false);
  updateSelectionHint(item);
  
  if (hasEnoughSelections(item)) {
    submitAnswer();
  }
}

function isCorrect(item) {
  const selected = [...state.selected].sort();
  const correct = [...new Set(item.correctLabels || [])].sort();
  return correct.length > 0 && selected.length === correct.length && selected.every((label, idx) => label === correct[idx]);
}

function submitAnswer() {
  const item = state.filtered[state.current];
  if (!item || !hasEnoughSelections(item) || isAnswered(item)) return;
  const correct = isCorrect(item);
  state.answers[answerKey(item)] = { selected: [...state.selected], correct };
  saveAnswers();
  renderChoices(item, true);
  showResult(item, correct, true);
  renderStats();
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
  const choicesToRender = item.shuffledChoices || item.choices;
  const rows = choicesToRender
    .map((choice) => {
      const text = explanations[choice.label];
      if (!text) return "";
      const choiceText = choice.text || `Option ${choice.label}`;
      const displayLabel = choice.displayLabel || choice.label;
      return `
        <li>
          <strong>${escapeHtml(displayLabel)}. ${escapeHtml(choiceText)}</strong>
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

  els.resultBox.className = `result ${correct ? "ok" : "bad"}`;
  els.resultBox.innerHTML = `
    <h3>${correct ? "ตอบถูก" : "ยังไม่ถูก"}</h3>
    <p><strong>เฉลย:</strong> ${escapeHtml(correctText)}</p>
    <p>${escapeHtml(explanation)}</p>
    ${renderChoiceExplanations(item)}
  `;
  els.resultBox.hidden = false;
}

async function init() {
  setTheme(state.theme);
  const response = await fetch("data/questions.json");
  const payload = await response.json();
  state.all = payload.questions || [];
  renderStartScreen();

  els.prevBtn.addEventListener("click", () => {
    state.current = Math.max(0, state.current - 1);
    render();
  });
  els.nextBtn.addEventListener("click", () => {
    if (!hasConfirmedCurrent()) return;
    state.current = Math.min(state.filtered.length - 1, state.current + 1);
    render();
  });
  
  els.startForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const quizId = els.quizSelect.value;
    const option = els.quizSelect.options[els.quizSelect.selectedIndex];
    const quizName = option.textContent.split(" (")[0];
    state.shuffleQuestions = els.shuffleQuestions.checked;
    state.shuffleChoices = els.shuffleChoices.checked;
    startQuiz(quizId, quizName);
  });
  
  els.themeToggle.addEventListener("click", () => setTheme(state.theme === "dark" ? "light" : "dark"));
}

init().catch((error) => {
  els.startScreen.innerHTML = `<div class="notice">โหลดข้อมูลไม่สำเร็จ: ${error.message}</div>`;
});
