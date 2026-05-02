// AI Resume Analyzer - Frontend JavaScript
const API_BASE = "http://localhost:5000/api";
let selectedFile = null;
let currentFeedback = null;

// ===== FILE UPLOAD HANDLING =====
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFileSelect(files[0]);
  }
});

fileInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    handleFileSelect(e.target.files[0]);
  }
});

function handleFileSelect(file) {
  const validTypes = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
  if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|txt)$/i)) {
    showError("Invalid file type. Please upload PDF, DOCX, or TXT.");
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    showError("File too large. Maximum size is 5MB.");
    return;
  }
  selectedFile = file;
  fileName.textContent = file.name;
  dropZone.style.display = "none";
  fileInfo.style.display = "flex";

  // Auto-read TXT files and populate textarea
  if (file.type === "text/plain" || file.name.endsWith(".txt")) {
    const reader = new FileReader();
    reader.onload = function(e) {
      document.getElementById("resumeText").value = e.target.result;
    };
    reader.onerror = function() {
      showError("Failed to read file content.");
    };
    reader.readAsText(file);
  }
}

function removeFile() {
  selectedFile = null;
  fileInput.value = "";
  dropZone.style.display = "block";
  fileInfo.style.display = "none";
  document.getElementById("resumeText").value = ""; // Clear textarea when removing file
}

// ===== ANALYZE RESUME =====
async function analyzeResume() {
  const resumeText = document.getElementById("resumeText").value.trim();
  const jobDescription = document.getElementById("jobDescription").value.trim();
  const roleSelector = document.getElementById("roleSelector");
  const targetRole = roleSelector ? roleSelector.value : "";
  const finalJobDescription = jobDescription || targetRole;

  if (!selectedFile && !resumeText) {
    showError("Please upload a resume file or paste resume text.");
    return;
  }

  const analyzeBtn = document.getElementById("analyzeBtn");
  const btnText = document.getElementById("btnText");
  const btnLoader = document.getElementById("btnLoader");

  analyzeBtn.disabled = true;
  btnText.style.display = "none";
  btnLoader.style.display = "inline";

  try {
    let response;
    if (selectedFile) {
      const formData = new FormData();
      formData.append("resume", selectedFile);
      formData.append("job_description", finalJobDescription);
      response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        body: formData,
      });
    } else {
      response = await fetch(`${API_BASE}/analyze-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: resumeText, job_description: finalJobDescription }),
      });
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Analysis failed");
    }

    const data = await response.json();
    displayResults(data);
  } catch (error) {
    showError(error.message);
  } finally {
    analyzeBtn.disabled = false;
    btnText.style.display = "inline";
    btnLoader.style.display = "none";
  }
}

function showError(message) {
  const errorBanner = document.getElementById("errorBanner");
  const errorMsg = document.getElementById("errorMsg");
  errorMsg.textContent = message;
  errorBanner.style.display = "flex";
  setTimeout(() => {
    errorBanner.style.display = "none";
  }, 5000);
}

// ===== DISPLAY RESULTS =====
function displayResults(data) {
  currentFeedback = data.feedback;
  // Capture state for advanced features
  currentResumeText = document.getElementById("resumeText").value.trim();
  currentJobDescription = document.getElementById("jobDescription").value.trim() || (document.getElementById("roleSelector") ? document.getElementById("roleSelector").value : "");
  currentScoreData = data.ats_score;
  document.getElementById("resultsSection").style.display = "block";
  document.getElementById("advancedSection").style.display = "block";
  document.getElementById("resultsSection").scrollIntoView({ behavior: "smooth" });

  const score = data.ats_score.final_score;
  const grade = data.ats_score.grade;
  const dimensions = data.ats_score.dimension_scores;
  const details = data.ats_score.details;
  
  // Domain
  const domainBadge = document.getElementById("detectedDomain");
  if (data.nlp_analysis.domain) {
    domainBadge.textContent = "Detected Domain: " + data.nlp_analysis.domain;
    domainBadge.style.display = "inline-block";
  } else {
    domainBadge.style.display = "none";
  }

  // Score circle
  const scoreNumEl = document.getElementById("scoreNum");
  document.getElementById("scoreGrade").textContent = grade;
  document.getElementById("scoreGrade").style.color = getScoreColor(score);
  document.getElementById("scoreSummary").textContent = data.feedback.overall_summary;

  const circumference = 2 * Math.PI * 52;
  const offset = circumference - (score / 100) * circumference;
  const ring = document.getElementById("scoreRing");
  ring.style.strokeDashoffset = offset;
  ring.style.stroke = getScoreColor(score);

  // Animate score from 0 to final
  let startTimestamp = null;
  const duration = 1200;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    // easing out cubic
    const easeOut = 1 - Math.pow(1 - progress, 3);
    scoreNumEl.textContent = Math.round(easeOut * Math.round(score));
    if (progress < 1) {
      window.requestAnimationFrame(step);
    } else {
      scoreNumEl.textContent = Math.round(score);
      scoreNumEl.style.color = getScoreColor(score);
    }
  };
  window.requestAnimationFrame(step);

  // Dimension bars
  const dimBars = document.getElementById("dimensionBars");
  dimBars.innerHTML = "";
  const dimLabels = {
    semantic_similarity: "Semantic Similarity",
    keyword_coverage: "Keyword Coverage",
    section_completeness: "Section Completeness",
    content_strength: "Content Strength",
    readability: "Readability",
  };
  for (const [key, value] of Object.entries(dimensions)) {
    const row = document.createElement("div");
    row.className = "dim-row";
    row.innerHTML = `
      <div class="dim-label">${dimLabels[key]}</div>
      <div class="dim-bar-wrap">
        <div class="dim-bar" style="width: ${value}%; background: ${getScoreColor(value)}"></div>
      </div>
      <div class="dim-score">${Math.round(value)}</div>
    `;
    dimBars.appendChild(row);
  }

  // Categorized Skills
  const skillsContainer = document.getElementById("skillsContainer");
  skillsContainer.innerHTML = "";
  const skillsData = data.nlp_analysis.skills;
  
  const categories = [
      { key: "Technical Skills", title: "Technical Skills" },
      { key: "Tools & Technologies", title: "Tools & Technologies" },
      { key: "Soft Skills", title: "Soft Skills" }
  ];
  
  let totalSkills = 0;
  
  categories.forEach(cat => {
      const catSkills = skillsData[cat.key] || [];
      if (catSkills.length > 0) {
          totalSkills += catSkills.length;
          const section = document.createElement("div");
          section.style.marginBottom = "15px";
          section.innerHTML = `<div style="font-weight: 600; font-size: 0.85rem; color: var(--text2); margin-bottom: 8px;">${cat.title}</div>`;
          
          const tagsWrap = document.createElement("div");
          tagsWrap.className = "skills-wrap";
          
          catSkills.forEach(skill => {
              const tag = document.createElement("span");
              tag.className = "skill-tag";
              tag.textContent = skill;
              tagsWrap.appendChild(tag);
          });
          
          section.appendChild(tagsWrap);
          skillsContainer.appendChild(section);
      }
  });

  if (totalSkills === 0) {
    skillsContainer.innerHTML = '<p style="color: var(--text3); font-size: 0.85rem;">No skills detected. Try adding more clear, industry-standard keywords.</p>';
  }

  // Keywords
  const keywordPanel = document.getElementById("keywordPanel");
  const matched = data.ats_score.matched_keywords.slice(0, 15);
  const missing = data.ats_score.missing_keywords.slice(0, 15);
  keywordPanel.innerHTML = `
    <div class="kw-section">
      <div class="kw-section-title">✅ Matched (${matched.length})</div>
      <div>${matched.map((k) => `<span class="kw-matched">${k}</span>`).join("") || '<span style="color: var(--text3); font-size: 0.85rem;">None</span>'}</div>
    </div>
    <div class="kw-section">
      <div class="kw-section-title">❌ Missing (${missing.length})</div>
      <div>${missing.map((k) => `<span class="kw-missing">${k}</span>`).join("") || '<span style="color: var(--text3); font-size: 0.85rem;">None</span>'}</div>
    </div>
  `;

  // NER
  const nerPanel = document.getElementById("nerPanel");
  const entities = data.nlp_analysis.entities;
  nerPanel.innerHTML = "";
  if (Object.keys(entities).length === 0) {
    nerPanel.innerHTML = '<p style="color: var(--text3); font-size: 0.85rem;">No entities detected</p>';
  } else {
    for (const [label, items] of Object.entries(entities)) {
      if (items.length > 0) {
        const group = document.createElement("div");
        group.className = "ner-group";
        group.innerHTML = `
          <div class="ner-label">${label}</div>
          <div class="ner-tags">
            ${items.slice(0, 10).map((item) => `<span class="ner-tag ner-${label}">${item}</span>`).join("")}
          </div>
        `;
        nerPanel.appendChild(group);
      }
    }
  }

  // Sections
  const sectionsPanel = document.getElementById("sectionsPanel");
  const sections = data.nlp_analysis.sections;
  sectionsPanel.innerHTML = "";
  for (const [section, present] of Object.entries(sections)) {
    const row = document.createElement("div");
    row.className = "section-row";
    let summaryBtnHtml = "";
    if (section === "summary" && !present) {
      summaryBtnHtml = `<button class="btn-outline-sm" id="genSummaryBtn" style="margin-left:8px; padding: 2px 8px; font-size: 0.7rem;" onclick="generateSummary()">Generate</button>`;
    }
    row.innerHTML = `
      <span class="section-name">${section}</span>
      <div>
        <span class="badge-${present ? "present" : "missing"}">${present ? "✓ Present" : "✗ Missing"}</span>
        ${summaryBtnHtml}
      </div>
    `;
    sectionsPanel.appendChild(row);
  }

  // Action Verbs
  const verbsPanel = document.getElementById("verbsPanel");
  const actionVerbs = data.nlp_analysis.action_verbs;
  const weakVerbs = data.nlp_analysis.weak_verbs;
  verbsPanel.innerHTML = `
    <div style="margin-bottom: 12px;">
      <div style="font-size: 0.75rem; color: var(--text3); margin-bottom: 6px; font-weight: 600;">STRONG VERBS (${actionVerbs.length})</div>
      ${actionVerbs.slice(0, 15).map((v) => `<span class="verb-tag-strong">${v}</span>`).join("") || '<span style="color: var(--text3); font-size: 0.85rem;">None found</span>'}
    </div>
    <div>
      <div style="font-size: 0.75rem; color: var(--text3); margin-bottom: 6px; font-weight: 600;">WEAK VERBS (${weakVerbs.length})</div>
      ${weakVerbs.slice(0, 10).map((v) => `<span class="verb-tag-weak">${v}</span>`).join("") || '<span style="color: var(--text3); font-size: 0.85rem;">None found</span>'}
    </div>
  `;

  // Readability
  const readabilityPanel = document.getElementById("readabilityPanel");
  const readability = data.nlp_analysis.readability;
  readabilityPanel.innerHTML = `
    <div class="read-metric"><span class="read-key">Word Count</span><span class="read-val">${readability.word_count}</span></div>
    <div class="read-metric"><span class="read-key">Sentences</span><span class="read-val">${readability.sentence_count}</span></div>
    <div class="read-metric"><span class="read-key">Avg Words/Sentence</span><span class="read-val">${readability.avg_words_per_sentence}</span></div>
    <div class="read-metric"><span class="read-key">Flesch-Kincaid</span><span class="read-val">${readability.flesch_kincaid_score}</span></div>
    <div class="read-metric"><span class="read-key">Grade</span><span class="read-val">${readability.readability_grade}</span></div>
  `;

  // Top Suggestions (Quick Improvements Panel)
  const topSuggestions = document.getElementById("topSuggestions");
  topSuggestions.innerHTML = "";
  let quickItems = [];
  
  if (data.feedback.actionable_suggestions && data.feedback.actionable_suggestions.length > 0) {
      const topKw = data.feedback.actionable_suggestions[0];
      quickItems.push(`Add keyword <strong>${topKw.keyword}</strong> to boost score.`);
  }
  
  if (data.feedback.readability_feedback && data.feedback.readability_feedback.actionable_fixes) {
      const fixes = data.feedback.readability_feedback.actionable_fixes;
      if (fixes.length > 0) {
          quickItems.push(`Fix <strong>${fixes[0].issue}</strong> for better ATS parsing.`);
      }
  }
  
  if (data.feedback.project_strength_feedback && data.feedback.project_strength_feedback.score < 70) {
      quickItems.push(`Add measurable metrics to your project bullet points.`);
  }
  
  data.feedback.top_suggestions.slice(0, 3).forEach(s => quickItems.push(s));
  
  [...new Set(quickItems)].slice(0, 4).forEach((suggestion, i) => {
    const card = document.createElement("div");
    card.className = "suggestion-card";
    card.innerHTML = `
      <div class="suggestion-num">Tip ${i + 1}</div>
      <p>${suggestion}</p>
    `;
    topSuggestions.appendChild(card);
  });

  // Show first tab
  showTab("keywords");
}

function getScoreColor(score) {
  if (score >= 85) return "#10b981";
  if (score >= 70) return "#3b82f6";
  if (score >= 55) return "#f59e0b";
  if (score >= 40) return "#f97316";
  return "#ef4444";
}

// ===== FEEDBACK TABS =====
function showTab(tabName) {
  const buttons = document.querySelectorAll(".tab-btn");
  buttons.forEach((btn) => btn.classList.remove("active"));
  event?.target?.classList.add("active");

  const tabContent = document.getElementById("tabContent");
  tabContent.innerHTML = "";

  if (!currentFeedback) return;

  if (tabName === "keywords") {
    const kw = currentFeedback.keyword_feedback;
    tabContent.innerHTML = `
      <div class="feedback-item">
        <div class="feedback-item-title">Keyword Score: ${kw.keyword_score}/100</div>
        <p>${kw.tip}</p>
      </div>
      ${kw.actionable_suggestions && kw.actionable_suggestions.length > 0 ? `
        <div class="feedback-item priority-high">
          <div class="feedback-item-title">Actionable Suggestions</div>
          ${kw.actionable_suggestions.map((s) => `
            <div style="margin-bottom: 12px; font-size: 0.85rem;">
              <span class="kw-missing">${s.keyword}</span> ${s.suggestion}<br/>
              <span style="color:var(--text3); font-style: italic;">Example: "${s.example}"</span>
            </div>
          `).join("")}
        </div>
      ` : ""}
      ${kw.suggestions ? kw.suggestions.map((s) => `<div class="feedback-item priority-medium"><p>${s}</p></div>`).join("") : ""}
    `;
  } else if (tabName === "bullets") {
    // Bullet Strength
    const ba = currentData.bullet_analysis || []; // Needs currentData in scope
    tabContent.innerHTML = ba.length === 0 ? '<p style="color: var(--text3);">No bullets found to analyze.</p>' : 
      ba.map(b => `
      <div class="feedback-item ${b.issues.length > 0 ? 'priority-high' : 'priority-low'}">
        <div style="font-size: 0.85rem; margin-bottom: 8px;">${b.original}</div>
        ${b.issues.length > 0 ? `<div style="font-size: 0.8rem; color: var(--red); margin-bottom: 4px;">Issues: ${b.issues.join(", ")}</div>` : ''}
        <div style="font-size: 0.82rem; color: var(--green);"><strong>Improved:</strong> ${b.improved}</div>
      </div>
    `).join("");
  } else if (tabName === "projects") {
    const pf = currentFeedback.project_strength_feedback;
    tabContent.innerHTML = `
      <div class="feedback-item">
        <div class="feedback-item-title">Project Strength: ${pf.score}/100</div>
        <p>${pf.message}</p>
        <div style="margin-top: 8px; font-size: 0.85rem; display: flex; gap: 16px;">
            <span><span style="color:var(--green); font-weight: bold;">${pf.quantified_bullets}</span> with metrics</span>
            <span><span style="color:var(--accent); font-weight: bold;">${pf.strong_verb_bullets}</span> with strong verbs</span>
        </div>
      </div>
      ${pf.tips.map((tip) => `<div class="feedback-item priority-medium"><p>${tip}</p></div>`).join("")}
    `;
  } else if (tabName === "verbs") {
    const av = currentFeedback.action_verb_feedback;
    tabContent.innerHTML = `
      <div class="feedback-item">
        <div class="feedback-item-title">Verb Strength: ${av.verb_strength}</div>
        <p>${av.tip}</p>
      </div>
      ${av.upgrade_suggestions.length > 0 ? `
        <div class="feedback-item priority-high">
          <div class="feedback-item-title">Replace Weak Verbs</div>
          ${av.upgrade_suggestions.map((u) => `
            <div class="upgrade-row">
              <span class="upgrade-weak">${u.weak}</span>
              <span class="upgrade-arrow">→</span>
              <span class="upgrade-strong">${u.suggestions}</span>
            </div>
          `).join("")}
        </div>
      ` : ""}
    `;
  } else if (tabName === "content") {
    const content = currentFeedback.content_feedback;
    tabContent.innerHTML = content.map((item) => `
      <div class="feedback-item priority-${item.priority}">
        <div class="feedback-item-title">${item.type}</div>
        <p>${item.message}</p>
      </div>
    `).join("") || '<p style="color: var(--text3);">No content feedback</p>';
  } else if (tabName === "structure") {
    const structure = currentFeedback.structure_feedback;
    tabContent.innerHTML = structure.map((item) => `
      <div class="feedback-item priority-medium">
        <div class="feedback-item-title">${item.type}</div>
        <p>${item.message}</p>
      </div>
    `).join("") || '<p style="color: var(--text3);">No structure feedback</p>';
  } else if (tabName === "readability") {
    const read = currentFeedback.readability_feedback;
    tabContent.innerHTML = `
      <div class="feedback-item">
        <div class="feedback-item-title">Readability Grade: ${read.grade}</div>
        <p>Flesch-Kincaid Score: ${read.flesch_kincaid_score} | Avg Sentence Length: ${read.avg_sentence_length} words</p>
      </div>
      ${read.actionable_fixes && read.actionable_fixes.length > 0 ? `
        <div class="feedback-item priority-high">
          <div class="feedback-item-title">Suggested Fixes</div>
          ${read.actionable_fixes.map(f => `
            <div style="margin-bottom: 12px; font-size: 0.85rem;">
              <strong>${f.issue}:</strong><br/>
              <span style="color:var(--red); text-decoration: line-through;">${f.before}</span><br/>
              <span style="color:var(--green);">${f.after.replace(/\\n/g, '<br/>')}</span>
            </div>
          `).join("")}
        </div>
      ` : ""}
      ${read.tips.map((tip) => `<div class="feedback-item priority-medium"><p>${tip}</p></div>`).join("")}
    `;
  }
}

// ===== NEW FEATURES =====

function toggleRecruiterMode() {
  const isChecked = document.getElementById("recruiterModeToggle").checked;
  if (isChecked) {
    document.body.classList.add("recruiter-mode");
  } else {
    document.body.classList.remove("recruiter-mode");
  }
}

async function generateSummary() {
  const btn = document.getElementById("genSummaryBtn");
  btn.disabled = true;
  btn.textContent = "Generating...";
  
  try {
    const response = await fetch(`${API_BASE}/generate-summary`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: currentResumeText }),
    });
    const data = await response.json();
    if (!data.success) throw new Error(data.error);
    
    alert("Generated Summary:\n\n" + data.summaries[0]);
  } catch (e) {
    showError("Failed to generate summary: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate";
  }
}

async function downloadResume() {
  const btn = document.getElementById("downloadBtn");
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = "Generating...";
  
  try {
    const response = await fetch(`${API_BASE}/download-resume`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: currentResumeText, bullet_analysis: currentData.bullet_analysis }),
    });
    const data = await response.json();
    if (!data.success) throw new Error(data.error);
    
    // Create a Blob and trigger download
    const blob = new Blob([data.html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "Optimized_Resume.html";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (e) {
    showError("Failed to export resume: " + e.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalText;
  }
}

function resetAnalysis() {
  document.getElementById("resultsSection").style.display = "none";
  document.getElementById("upload-section").scrollIntoView({ behavior: "smooth" });
  removeFile();
  document.getElementById("resumeText").value = "";
  document.getElementById("jobDescription").value = "";
  currentFeedback = null;
}

// ===== ADVANCED FEATURES STATE =====
let currentResumeText = "";
let currentJobDescription = "";
let currentScoreData = null;
let sessionId = "session_" + Date.now();
let versionCompareSelection = [];

// Store resume text after analysis for advanced features
function scrollToAdvanced() {
  document.getElementById("advancedSection").scrollIntoView({ behavior: "smooth" });
}

// ===== ADVANCED TAB SWITCHING =====
function switchAdvTab(tabName) {
  document.querySelectorAll(".adv-tab-btn").forEach((btn, i) => {
    btn.classList.remove("active");
  });
  event.target.classList.add("active");

  const panels = ["ats-sim", "skill-gap", "bullet", "versions", "github"];
  panels.forEach(p => {
    const el = document.getElementById("adv-" + p);
    if (el) el.style.display = p === tabName ? "block" : "none";
  });
}

// ===== FEATURE 3: ATS SIMULATION =====
async function runATSSimulation() {
  if (!currentResumeText) {
    showError("Please upload and analyze a resume on the main tab first.");
    return;
  }
  const btn = document.getElementById("atsSimBtn");
  const btnText = document.getElementById("atsSimBtnText");
  const loader = document.getElementById("atsSimLoader");
  btn.disabled = true;
  btnText.style.display = "none";
  loader.style.display = "inline";

  try {
    const response = await fetch(`${API_BASE}/ats-simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: currentResumeText, job_description: currentJobDescription }),
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    renderATSSimulation(data);
  } catch (e) {
    showError(e.message);
  } finally {
    btn.disabled = false;
    btnText.style.display = "inline";
    loader.style.display = "none";
  }
}

function renderATSSimulation(data) {
  const el = document.getElementById("atsSimResult");
  el.style.display = "block";

  const verdictClass = data.verdict === "PASS" ? "pass" : data.verdict === "FAIL" ? "fail" : "conditional";
  const scoreColor = data.ats_score >= 70 ? "#10b981" : data.ats_score >= 45 ? "#f59e0b" : "#ef4444";

  const weakSectionsHtml = data.weak_sections.map(ws => `
    <div class="weak-section-item">
      <span class="severity-badge severity-${ws.severity}">${ws.severity}</span>
      <div>
        <div style="font-size:0.85rem;font-weight:600;margin-bottom:2px;">${ws.section}</div>
        <div style="font-size:0.82rem;color:var(--text2);">${ws.reason}</div>
      </div>
    </div>
  `).join("") || '<p style="color:var(--text3);font-size:0.85rem;">No critical weak sections found.</p>';

  const scanStrengths = data.six_second_scan.strengths.map(s =>
    `<div class="ats-item ok"><span class="ats-dot ok"></span>${s}</div>`
  ).join("");
  const scanIssues = data.six_second_scan.issues.map(s =>
    `<div class="ats-item bad"><span class="ats-dot bad"></span>${s}</div>`
  ).join("");

  const parseIssues = data.parse_issues.length > 0
    ? data.parse_issues.map(i => `<div class="ats-item bad"><span class="ats-dot bad"></span>${i}</div>`).join("")
    : '<div class="ats-item ok"><span class="ats-dot ok"></span>No parsing issues detected.</div>';

  const recsHtml = data.recommendations.map(r => `
    <div class="feedback-item priority-${r.priority === 'critical' ? 'high' : r.priority}">
      <p>${r.action}</p>
    </div>
  `).join("") || "";

  const kdHtml = data.keyword_density && data.keyword_density.density_percent !== undefined ? `
    <div class="ats-card">
      <h4>Keyword Density</h4>
      <div style="font-size:1.4rem;font-weight:800;color:${data.keyword_density.density_percent >= 50 ? '#10b981' : '#f59e0b'}">
        ${data.keyword_density.density_percent}%
      </div>
      <div style="font-size:0.82rem;color:var(--text3);margin-bottom:8px;">${data.keyword_density.matched_count} of ${data.keyword_density.total_jd_words} JD keywords matched</div>
      ${data.keyword_density.top_missing && data.keyword_density.top_missing.length > 0 ? `
        <div style="font-size:0.78rem;color:var(--text3);margin-bottom:4px;font-weight:600;">TOP MISSING</div>
        ${data.keyword_density.top_missing.map(k => `<span class="kw-missing">${k}</span>`).join("")}
      ` : ""}
    </div>
  ` : "";

  el.innerHTML = `
    <div class="ats-verdict ${verdictClass}" style="margin-top:20px;">
      <div>
        <div class="ats-verdict-badge">${data.verdict}</div>
      </div>
      <div class="ats-verdict-score" style="color:${scoreColor}">${data.ats_score}</div>
      <div class="ats-verdict-reasoning">${data.reasoning.join(" ")}</div>
    </div>
    <div class="ats-grid">
      <div class="ats-card">
        <h4>6-Second Scan</h4>
        ${scanStrengths}${scanIssues}
      </div>
      <div class="ats-card">
        <h4>Parse Issues</h4>
        ${parseIssues}
      </div>
      <div class="ats-card">
        <h4>Weak Sections</h4>
        ${weakSectionsHtml}
      </div>
      ${kdHtml}
    </div>
    ${recsHtml ? `<div style="margin-top:16px;"><div style="font-size:0.8rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;">Recommendations</div>${recsHtml}</div>` : ""}
  `;
}

// ===== FEATURE 4: SKILL GAP ANALYZER =====
async function runSkillGap() {
  if (!currentResumeText) {
    showError("Please upload and analyze a resume on the main tab first.");
    return;
  }
  if (!currentJobDescription) {
    showError("A job description is required for skill gap analysis.");
    return;
  }
  const btn = document.getElementById("skillGapBtn");
  const btnText = document.getElementById("skillGapBtnText");
  const loader = document.getElementById("skillGapLoader");
  btn.disabled = true;
  btnText.style.display = "none";
  loader.style.display = "inline";

  try {
    const response = await fetch(`${API_BASE}/skill-gap`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: currentResumeText, job_description: currentJobDescription }),
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    renderSkillGap(data);
  } catch (e) {
    showError(e.message);
  } finally {
    btn.disabled = false;
    btnText.style.display = "inline";
    loader.style.display = "none";
  }
}

function renderSkillGap(data) {
  const el = document.getElementById("skillGapResult");
  el.style.display = "block";

  const priorityHtml = data.priority_skills.length > 0
    ? `<div style="margin-bottom:16px;">
        <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Priority Skills to Learn</div>
        ${data.priority_skills.map(s => `<span class="priority-skill-tag">${s}</span>`).join("")}
      </div>`
    : "";

  const roadmapHtml = data.learning_roadmap.map(item => `
    <div class="roadmap-item">
      <div class="roadmap-skill">${item.skill}</div>
      <div class="roadmap-row"><span class="roadmap-label">Timeline</span><span>${item.roadmap.timeline}</span></div>
      <div class="roadmap-row"><span class="roadmap-label">Resources</span><span>${item.roadmap.resources.join(" · ")}</span></div>
      <div class="roadmap-row"><span class="roadmap-label">Projects</span><span>${item.roadmap.projects.join(" · ")}</span></div>
    </div>
  `).join("") || '<p style="color:var(--text3);font-size:0.85rem;">No skill gaps detected — your resume covers the required skills.</p>';

  const presentHtml = data.skills_present.map(s => `<span class="kw-matched">${s}</span>`).join("") || "None";
  const missingHtml = data.skills_missing.map(s => `<span class="kw-missing">${s}</span>`).join("") || "None";

  el.innerHTML = `
    <div class="skill-gap-summary" style="margin-top:20px;">
      <div class="skill-gap-stat match">
        <div class="skill-gap-stat-num">${data.match_percent}%</div>
        <div class="skill-gap-stat-label">Match</div>
      </div>
      <div class="skill-gap-stat present">
        <div class="skill-gap-stat-num">${data.skills_present.length}</div>
        <div class="skill-gap-stat-label">Skills Present</div>
      </div>
      <div class="skill-gap-stat missing">
        <div class="skill-gap-stat-num">${data.skills_missing.length}</div>
        <div class="skill-gap-stat-label">Skills Missing</div>
      </div>
    </div>
    <div style="margin-bottom:16px;">
      <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Skills You Have</div>
      ${presentHtml}
    </div>
    <div style="margin-bottom:20px;">
      <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Skills to Acquire</div>
      ${missingHtml}
    </div>
    ${priorityHtml}
    <div style="font-size:0.8rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px;">Learning Roadmap</div>
    ${roadmapHtml}
  `;
}

// ===== FEATURE 2: BULLET IMPROVER =====
async function runBulletImprover() {
  const bullet = document.getElementById("bulletInput").value.trim();
  if (!bullet) {
    showError("Please enter a bullet point to improve.");
    return;
  }
  const btn = document.getElementById("bulletBtn");
  const btnText = document.getElementById("bulletBtnText");
  const loader = document.getElementById("bulletLoader");
  btn.disabled = true;
  btnText.style.display = "none";
  loader.style.display = "inline";

  try {
    const response = await fetch(`${API_BASE}/improve-bullet`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bullet }),
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    renderBulletResult(data);
  } catch (e) {
    showError(e.message);
  } finally {
    btn.disabled = false;
    btnText.style.display = "inline";
    loader.style.display = "none";
  }
}

function renderBulletResult(data) {
  const el = document.getElementById("bulletResult");
  el.style.display = "block";

  const issuesHtml = data.issues.map(i =>
    `<div class="bullet-issue"><span class="bullet-issue-dot"></span>${i}</div>`
  ).join("") || '<div style="color:var(--text3);font-size:0.83rem;">No major issues detected.</div>';

  const suggestionsHtml = data.suggestions.map(s =>
    `<div class="feedback-item priority-medium"><p>${s}</p></div>`
  ).join("");

  el.innerHTML = `
    <div class="bullet-compare" style="margin-top:20px;">
      <div class="bullet-box">
        <div class="bullet-box-label">Original</div>
        <div class="bullet-box-text">${data.original}</div>
      </div>
      <div class="bullet-box improved">
        <div class="bullet-box-label">Improved</div>
        <div class="bullet-box-text">${data.improved}</div>
      </div>
    </div>
    <div style="margin-bottom:16px;">
      <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Issues Found</div>
      ${issuesHtml}
    </div>
    ${suggestionsHtml ? `<div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Suggestions</div>${suggestionsHtml}` : ""}
  `;
}

// ===== FEATURE 5: RESUME VERSIONING =====
async function saveVersion() {
  if (!currentResumeText || !currentScoreData) {
    showError("Please upload and analyze a resume on the main tab first before saving a version.");
    return;
  }
  const label = document.getElementById("versionLabel").value.trim();
  if (!label) {
    showError("Please enter a version name.");
    return;
  }
  try {
    const response = await fetch(`${API_BASE}/versions/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        label,
        resume_text: currentResumeText,
        score_data: currentScoreData,
      }),
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    document.getElementById("versionLabel").value = "";
    renderVersionsList(data.versions);
  } catch (e) {
    showError(e.message);
  }
}

async function loadVersionsList() {
  try {
    const response = await fetch(`${API_BASE}/versions/list`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });
    const data = await response.json();
    renderVersionsList(data.versions || []);
  } catch (e) {}
}

function renderVersionsList(versions) {
  const el = document.getElementById("versionsList");
  versionCompareSelection = [];

  if (!versions || versions.length === 0) {
    el.innerHTML = '<p style="color:var(--text3);font-size:0.85rem;margin-top:12px;">No saved versions yet. Analyze a resume and save it as a version.</p>';
    return;
  }

  el.innerHTML = `
    <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;margin-top:16px;">Saved Versions</div>
    ${versions.map(v => `
      <div class="version-card">
        <div>
          <div class="version-label">${v.label}</div>
          <div class="version-grade">${v.grade}</div>
        </div>
        <div class="version-score" style="color:${getScoreColor(v.score)}">${v.score}</div>
        <div class="version-actions">
          <button class="version-compare-btn" id="vcbtn-${v.id}" onclick="selectVersionForCompare(${v.id})">Compare</button>
        </div>
      </div>
    `).join("")}
    ${versions.length >= 2 ? `<button class="btn-outline" style="margin-top:8px;" onclick="runVersionCompare()">Compare Selected</button>` : ""}
  `;
}

function selectVersionForCompare(id) {
  const btn = document.getElementById("vcbtn-" + id);
  const idx = versionCompareSelection.indexOf(id);
  if (idx === -1) {
    if (versionCompareSelection.length >= 2) {
      const removed = versionCompareSelection.shift();
      const oldBtn = document.getElementById("vcbtn-" + removed);
      if (oldBtn) oldBtn.classList.remove("selected");
    }
    versionCompareSelection.push(id);
    btn.classList.add("selected");
  } else {
    versionCompareSelection.splice(idx, 1);
    btn.classList.remove("selected");
  }
}

async function runVersionCompare() {
  if (versionCompareSelection.length < 2) {
    showError("Select exactly 2 versions to compare.");
    return;
  }
  try {
    const response = await fetch(`${API_BASE}/versions/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        id_a: versionCompareSelection[0],
        id_b: versionCompareSelection[1],
      }),
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    renderVersionCompare(data);
  } catch (e) {
    showError(e.message);
  }
}

function renderVersionCompare(data) {
  const el = document.getElementById("versionCompare");
  el.style.display = "block";

  const delta = data.score_delta;
  const deltaClass = delta >= 0 ? "positive" : "negative";
  const deltaStr = (delta >= 0 ? "+" : "") + delta;

  const dimLabels = {
    semantic_similarity: "Semantic Similarity",
    keyword_coverage: "Keyword Coverage",
    section_completeness: "Section Completeness",
    content_strength: "Content Strength",
    readability: "Readability",
  };

  const dimsHtml = data.dimension_comparison.map(d => {
    const dClass = d.delta >= 0 ? "positive" : "negative";
    const dStr = (d.delta >= 0 ? "+" : "") + d.delta;
    return `
      <div class="compare-dim-row">
        <div class="compare-dim-label">${dimLabels[d.dimension] || d.dimension}</div>
        <div class="compare-dim-vals">
          <span style="color:var(--text2)">${d.version_a}</span>
          <span style="color:var(--text3)">→</span>
          <span style="color:var(--text2)">${d.version_b}</span>
          <span class="compare-dim-delta ${dClass}">${dStr}</span>
        </div>
      </div>
    `;
  }).join("");

  el.innerHTML = `
    <div class="compare-result">
      <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:14px;">Version Comparison</div>
      <div class="compare-header">
        <div class="compare-version-box">
          <div class="compare-version-name">${data.version_a.label}</div>
          <div class="compare-version-score" style="color:${getScoreColor(data.version_a.score)}">${data.version_a.score}</div>
          <div style="font-size:0.78rem;color:var(--text3)">${data.version_a.grade}</div>
        </div>
        <div style="display:flex;align-items:center;font-size:1.5rem;color:var(--text3)">→</div>
        <div class="compare-version-box">
          <div class="compare-version-name">${data.version_b.label}</div>
          <div class="compare-version-score" style="color:${getScoreColor(data.version_b.score)}">${data.version_b.score}</div>
          <div style="font-size:0.78rem;color:var(--text3)">${data.version_b.grade}</div>
        </div>
        <div style="display:flex;align-items:center;">
          <div>
            <div style="font-size:0.75rem;color:var(--text3)">Score Change</div>
            <div class="compare-delta ${deltaClass}" style="font-size:1.4rem;">${deltaStr}</div>
          </div>
        </div>
      </div>
      <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;">Dimension Breakdown</div>
      ${dimsHtml}
    </div>
  `;
}

// ===== FEATURE 6: GITHUB ANALYZER =====
async function runGitHubAnalyzer() {
  const url = document.getElementById("githubUrl").value.trim();
  if (!url) {
    showError("Please enter a GitHub URL.");
    return;
  }
  const btn = document.getElementById("githubBtn");
  const btnText = document.getElementById("githubBtnText");
  const loader = document.getElementById("githubLoader");
  btn.disabled = true;
  btnText.style.display = "none";
  loader.style.display = "inline";

  try {
    const response = await fetch(`${API_BASE}/github-analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ github_url: url }),
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    renderGitHubResult(data);
  } catch (e) {
    showError(e.message);
  } finally {
    btn.disabled = false;
    btnText.style.display = "inline";
    loader.style.display = "none";
  }
}

function renderGitHubResult(data) {
  const el = document.getElementById("githubResult");
  el.style.display = "block";

  const techHtml = (data.tech_stack || []).map(t =>
    `<span class="github-tech-tag">${t}</span>`
  ).join("");

  const bulletsHtml = (data.resume_bullets || []).map(b =>
    `<div class="github-bullet">${b}</div>`
  ).join("");

  const skillsHtml = (data.skills_extracted || []).map(s =>
    `<span class="skill-tag">${s}</span>`
  ).join("");

  let reposHtml = "";
  if (data.type === "profile" && data.top_repos) {
    reposHtml = `
      <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;margin-top:16px;">Top Repositories</div>
      ${data.top_repos.map(r => `
        <div class="github-repo-card">
          <div class="github-repo-name">${r.name}</div>
          ${r.description ? `<div class="github-repo-desc">${r.description}</div>` : ""}
          <div class="github-repo-meta">${r.language || "Unknown"} · ${r.stars} stars</div>
        </div>
      `).join("")}
    `;
  }

  const headerInfo = data.type === "profile"
    ? `${data.public_repos} repos · ${data.followers} followers · ${data.total_stars} total stars`
    : `${data.stars} stars · ${data.forks} forks`;

  el.innerHTML = `
    <div class="github-profile-header" style="margin-top:20px;">
      <div>
        <div class="github-username">${data.name || data.username || data.repo_name || ""}</div>
        <div class="github-meta">${headerInfo}</div>
        ${data.description ? `<div class="github-meta" style="margin-top:4px;">${data.description}</div>` : ""}
      </div>
    </div>
    <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Tech Stack</div>
    <div class="github-tech-stack">${techHtml || '<span style="color:var(--text3);font-size:0.85rem;">No tech stack detected.</span>'}</div>
    <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;margin-top:16px;">Generated Resume Bullets</div>
    ${bulletsHtml || '<p style="color:var(--text3);font-size:0.85rem;">No bullets generated.</p>'}
    <div style="font-size:0.78rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;margin-top:16px;">Extracted Skills</div>
    <div>${skillsHtml || '<span style="color:var(--text3);font-size:0.85rem;">No skills extracted.</span>'}</div>
    ${reposHtml}
  `;
}

// ===== NEW SAAS FEATURES (Authentication, Dashboard, Templates, Email) =====

// Routing / Views
function showView(viewId) {
  document.querySelectorAll('.view-section').forEach(v => v.style.display = 'none');
  const viewEl = document.getElementById('view-' + viewId);
  if (viewEl) viewEl.style.display = 'block';
  
  if (viewId === 'templates') renderTemplatePreview();
}

// Authentication functions removed


// Real-time suggestions on text area (Debounced)
let typingTimer;
const resumeTextEl = document.getElementById('resumeText');
if (resumeTextEl) {
  resumeTextEl.addEventListener('input', function() {
    clearTimeout(typingTimer);
    const text = this.value;
    typingTimer = setTimeout(() => {
      // Basic local check for passive voice or weak verbs
      const weakVerbs = ['helped', 'worked', 'did', 'made', 'responsible for'];
      let suggestions = [];
      weakVerbs.forEach(v => {
        if (text.toLowerCase().includes(v)) {
          suggestions.push(`Consider replacing "${v}" with a stronger action verb (e.g., spearheaded, developed, architected).`);
        }
      });
      let hintDiv = document.getElementById('realtime-hint');
      if (!hintDiv) {
        hintDiv = document.createElement('div');
        hintDiv.id = 'realtime-hint';
        hintDiv.style.fontSize = '0.85rem';
        hintDiv.style.color = 'var(--yellow)';
        hintDiv.style.marginTop = '8px';
        this.parentNode.insertBefore(hintDiv, this.nextSibling);
      }
      if (suggestions.length > 0) {
        hintDiv.innerHTML = `<i data-lucide="zap" style="width:14px;height:14px;display:inline-block;vertical-align:middle;margin-right:4px;"></i> ${suggestions[0]}`;
        if(window.lucide) window.lucide.createIcons();
      } else {
        hintDiv.innerHTML = '';
      }
    }, 800);
  });
}

// Full AI Rewrite Feature
async function improveFullResume() {
  if (!currentResumeText) {
    showError("Analyze a resume first.");
    return;
  }
  const btn = document.getElementById("improveFullBtn");
  const origHtml = btn.innerHTML;
  btn.innerHTML = "Rewriting...";
  btn.disabled = true;
  
  try {
    const res = await fetch(`${API_BASE}/improve-resume`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: currentResumeText })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    
    // Update the textarea with improved text
    const resumeTextArea = document.getElementById('resumeText');
    if(resumeTextArea) resumeTextArea.value = data.improved_resume;
    currentResumeText = data.improved_resume;
    alert("Resume has been successfully rewritten! You can now Re-Analyze it to see the new score.");
  } catch (e) {
    showError(e.message);
  } finally {
    btn.innerHTML = origHtml;
    btn.disabled = false;
  }
}

// Email Report Feature
async function emailReport() {
  const user = prompt("Enter your email address:");
  if (!user) {
    return;
  }
  
  const btn = document.getElementById("emailBtn");
  const origHtml = btn.innerHTML;
  btn.innerHTML = "Sending...";
  btn.disabled = true;
  
  try {
    const scoreEl = document.getElementById('scoreNum');
    const score = scoreEl ? scoreEl.textContent : "N/A";
    const res = await fetch(`${API_BASE}/send-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        email: user,
        report_html: "<h1>Your Resume Score is " + score + "</h1><p>Log in to your dashboard for full details.</p>"
      })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    alert("Report sent to " + user);
  } catch (e) {
    showError(e.message);
  } finally {
    btn.innerHTML = origHtml;
    btn.disabled = false;
  }
}

// Templates & PDF Export
let selectedTemplateName = 'modern';

function selectTemplate(name) {
  selectedTemplateName = name;
  document.querySelectorAll('.template-option').forEach(el => el.classList.remove('active'));
  if (event && event.target) {
    event.target.classList.add('active');
  }
  renderTemplatePreview();
}

function renderTemplatePreview() {
  const container = document.getElementById('templatePreview');
  if (!container) return;
  if (!currentResumeText) {
    container.innerHTML = '<p style="color: #666; text-align: center; margin-top: 200px;">Analyze a resume first to generate a preview.</p>';
    return;
  }
  
  // A very basic template rendering (in reality, we'd parse sections properly)
  const paragraphs = currentResumeText.split('\n\n').filter(p => p.trim());
  let html = '';
  
  if (selectedTemplateName === 'modern') {
    html = `<div style="font-family: 'Inter', sans-serif;">
      <h1 style="color: #2563eb; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Professional Resume</h1>
      ${paragraphs.map(p => `<p style="margin-bottom: 12px; line-height: 1.6;">${p.replace(/\n/g, '<br/>')}</p>`).join('')}
    </div>`;
  } else if (selectedTemplateName === 'minimal') {
    html = `<div style="font-family: 'Times New Roman', serif;">
      <h1 style="text-align: center; text-transform: uppercase; border-bottom: 1px solid #000; padding-bottom: 10px;">Resume</h1>
      ${paragraphs.map(p => `<p style="margin-bottom: 10px; line-height: 1.5;">${p.replace(/\n/g, '<br/>')}</p>`).join('')}
    </div>`;
  } else if (selectedTemplateName === 'ats') {
    html = `<div style="font-family: Arial, sans-serif;">
      <h2 style="text-transform: uppercase;">John Doe</h2>
      <hr style="border:none;border-top:1px solid #333;margin-bottom:12px;"/>
      ${paragraphs.map(p => `<p style="margin-bottom: 10px;">${p.replace(/\n/g, '<br/>')}</p>`).join('')}
    </div>`;
  }
  
  container.innerHTML = html;
}

function exportPDF() {
  const element = document.getElementById('templatePreview');
  if (!currentResumeText) {
    showError("Please analyze a resume first to generate a PDF.");
    return;
  }
  
  if (typeof html2pdf !== 'function') {
    showError("PDF library is still loading. Please try again in a moment.");
    return;
  }
  
  const opt = {
    margin:       10,
    filename:     'Optimized_Resume.pdf',
    image:        { type: 'jpeg', quality: 0.98 },
    html2canvas:  { scale: 2 },
    jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };
  
  html2pdf().set(opt).from(element).save();
}
