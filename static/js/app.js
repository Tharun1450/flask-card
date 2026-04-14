/* =========================================================
   FlashGen AI — app.js
   Handles upload → generate → render → flip → export
   ========================================================= */

'use strict';

// ── DOM refs ────────────────────────────────────────────────
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const fileInfo = document.getElementById('fileInfo');
const fileChipName = document.getElementById('fileChipName');
const removeFileBtn = document.getElementById('removeFileBtn');
const generateBtn = document.getElementById('generateBtn');

const progressSection = document.getElementById('progressSection');
const progressTitle = document.getElementById('progressTitle');

const errorBanner = document.getElementById('errorBanner');
const errorMsg = document.getElementById('errorMsg');
const errorClose = document.getElementById('errorClose');

const resultsSection = document.getElementById('resultsSection');
const resultsCount = document.getElementById('resultsCount');
const cardsGrid = document.getElementById('cardsGrid');
const exportBtn = document.getElementById('exportBtn');
const resetBtn = document.getElementById('resetBtn');
const filterBtns = document.querySelectorAll('.filter-btn');

const chatbotSection = document.getElementById('chatbotSection');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');

// ── State ───────────────────────────────────────────────────
let selectedFile = null;
let flashcardsData = [];

// ── File selection ──────────────────────────────────────────
browseBtn.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('click', (e) => {
  if (e.target === uploadZone || e.target.classList.contains('upload-icon') ||
    e.target.classList.contains('upload-title') || e.target.classList.contains('upload-sub') ||
    e.target.classList.contains('upload-formats')) {
    fileInput.click();
  }
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) selectFile(fileInput.files[0]);
});

// Drag-and-drop
uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) selectFile(file);
});

function selectFile(file) {
  const allowed = ['application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation'];
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['pdf', 'docx', 'ppt', 'pptx'].includes(ext)) {
    showError('Unsupported file type. Please upload PDF, DOCX, PPT, or PPTX.');
    return;
  }
  selectedFile = file;
  fileChipName.textContent = file.name;
  uploadZone.style.display = 'none';
  fileInfo.style.display = 'flex';
  hideError();
}

removeFileBtn.addEventListener('click', resetUpload);

function resetUpload() {
  selectedFile = null;
  fileInput.value = '';
  uploadZone.style.display = '';
  fileInfo.style.display = 'none';
  hideError();
}

// ── Generate ────────────────────────────────────────────────
generateBtn.addEventListener('click', async () => {
  if (!selectedFile) return;
  generateBtn.disabled = true;
  hideError();
  showProgress('Extracting text from your document…');

  try {
    // Step 1 — Upload & extract
    const formData = new FormData();
    formData.append('file', selectedFile);

    // Check OCR toggle
    const ocrToggle = document.getElementById('ocrToggle');
    if (ocrToggle && ocrToggle.checked) {
      formData.append('ocr_mode', 'true');
      setProgress('Running OCR extraction… (This may take a while)');
    }

    const uploadRes = await fetch('/api/upload', { method: 'POST', body: formData });
    const uploadData = await uploadRes.json();

    if (!uploadRes.ok) {
      throw new Error(uploadData.error || 'Upload failed.');
    }

    // Step 2 — Generate flashcards
    setProgress('Generating flashcards with gemma2:2b… (this may take a minute)');

    const genRes = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context: uploadData.context }),
    });
    const genData = await genRes.json();

    if (!genRes.ok) {
      throw new Error(genData.error || 'Flashcard generation failed.');
    }

    if (genData.error) {
      throw new Error(genData.error);
    }

    if (!genData.flashcards || genData.flashcards.length === 0) {
      throw new Error('No flashcards were generated. The document may not contain enough educational content.');
    }

    flashcardsData = genData.flashcards;
    hideProgress();
    renderResults(flashcardsData);

    // Show Chatbot
    chatbotSection.style.display = 'block';
    chatSendBtn.disabled = false;
    chatInput.value = '';

  } catch (err) {
    hideProgress();
    showError(err.message || 'An unexpected error occurred.');
    generateBtn.disabled = false;
  }
});

// ── Render results ──────────────────────────────────────────
function renderResults(cards) {
  cardsGrid.innerHTML = '';
  resultsCount.textContent = `${cards.length} flashcard${cards.length !== 1 ? 's' : ''} generated`;

  cards.forEach((card, i) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'flashcard-wrapper';
    wrapper.style.setProperty('--i', i);
    wrapper.dataset.difficulty = card.difficulty;

    wrapper.innerHTML = `
      <div class="flashcard">
        <div class="flashcard-front">
          <div class="card-meta">
            <span class="card-topic" title="${escHtml(card.topic)}">${escHtml(card.topic)}</span>
            <span class="card-difficulty diff-${card.difficulty}">${card.difficulty}</span>
          </div>
          <div class="card-question">${escHtml(card.question)}</div>
          <div class="card-hint">Click to reveal answer</div>
        </div>
        <div class="flashcard-back">
          <div class="card-meta">
            <span class="card-topic" title="${escHtml(card.topic)}">${escHtml(card.topic)}</span>
            <span class="card-difficulty diff-${card.difficulty}">${card.difficulty}</span>
          </div>
          <div class="card-answer-label">Answer</div>
          <div class="card-answer">${escHtml(card.answer)}</div>
          <div class="card-flip-back">Click to flip back</div>
        </div>
      </div>`;

    wrapper.addEventListener('click', () => wrapper.classList.toggle('flipped'));
    cardsGrid.appendChild(wrapper);
  });

  resultsSection.style.display = '';
  // Reset filter
  filterBtns.forEach(b => b.classList.remove('active'));
  document.querySelector('[data-diff="all"]').classList.add('active');

  // Smooth scroll to results
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Filter ──────────────────────────────────────────────────
filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const diff = btn.dataset.diff;
    document.querySelectorAll('.flashcard-wrapper').forEach(w => {
      if (diff === 'all' || w.dataset.difficulty === diff) {
        w.classList.remove('hidden');
      } else {
        w.classList.add('hidden');
      }
    });
  });
});

// ── Export ──────────────────────────────────────────────────
exportBtn.addEventListener('click', () => {
  if (!flashcardsData.length) return;
  const blob = new Blob([JSON.stringify({ title: 'Document Flashcards', flashcards: flashcardsData }, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'flashcards.json';
  a.click(); URL.revokeObjectURL(url);
});

// ── Reset ───────────────────────────────────────────────────
resetBtn.addEventListener('click', () => {
  flashcardsData = [];
  cardsGrid.innerHTML = '';
  resultsSection.style.display = 'none';
  chatbotSection.style.display = 'none';
  resetUpload();
  generateBtn.disabled = false;
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ── Chatbot ─────────────────────────────────────────────────
async function handleChatSend() {
  const query = chatInput.value.trim();
  if (!query) return;

  // Append user message
  const userMsg = document.createElement('div');
  userMsg.className = 'chat-message user';
  userMsg.textContent = query;
  chatMessages.appendChild(userMsg);

  chatInput.value = '';
  chatInput.disabled = true;
  chatSendBtn.disabled = true;

  // Append thinking indicator
  const botMsg = document.createElement('div');
  botMsg.className = 'chat-message bot thinking';
  botMsg.textContent = 'Thinking...';
  chatMessages.appendChild(botMsg);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: query }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Chat error');

    botMsg.classList.remove('thinking');
    botMsg.textContent = data.answer;
  } catch (err) {
    botMsg.classList.remove('thinking');
    botMsg.textContent = 'Error: ' + err.message;
  } finally {
    chatInput.disabled = false;
    chatSendBtn.disabled = false;
    chatInput.focus();
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

chatSendBtn.addEventListener('click', handleChatSend);
chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') handleChatSend();
});

// ── Helpers ─────────────────────────────────────────────────
function showProgress(msg) {
  progressTitle.textContent = msg;
  progressSection.style.display = '';
  resultsSection.style.display = 'none';
  document.getElementById('uploadCard').style.display = 'none';
}
function setProgress(msg) {
  progressTitle.textContent = msg;
}
function hideProgress() {
  progressSection.style.display = 'none';
  document.getElementById('uploadCard').style.display = '';
}
function showError(msg) {
  errorMsg.textContent = msg;
  errorBanner.style.display = 'flex';
}
function hideError() {
  errorBanner.style.display = 'none';
}
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

errorClose.addEventListener('click', hideError);
