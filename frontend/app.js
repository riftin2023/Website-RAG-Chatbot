const API_BASE_URL = "http://127.0.0.1:5000";

const crawlForm = document.querySelector("#crawl-form");
const chatForm = document.querySelector("#chat-form");
const websiteUrlInput = document.querySelector("#website-url");
const questionInput = document.querySelector("#question-input");
const answerWindow = document.querySelector("#answer-window");
const sourcesList = document.querySelector("#sources-list");
const statusPill = document.querySelector("#status-pill");
const spinner = document.querySelector("#loading-spinner");
const crawlButton = document.querySelector("#crawl-button");
const askButton = document.querySelector("#ask-button");

let activeWebsiteUrl = "";

function setLoading(isLoading, label = "Working") {
  spinner.classList.toggle("is-visible", isLoading);
  crawlButton.disabled = isLoading;
  askButton.disabled = isLoading;
  statusPill.textContent = isLoading ? label : "Ready";
}

function showError(message) {
  answerWindow.innerHTML = `<p class="error">${escapeHtml(message)}</p>`;
  statusPill.textContent = "Error";
}

function showAnswer(answer) {
  answerWindow.textContent = answer || "No answer returned.";
}

function showSources(sources = []) {
  if (!sources.length) {
    sourcesList.innerHTML = `<p class="placeholder">No sources returned.</p>`;
    return;
  }

  sourcesList.innerHTML = sources.map((source, index) => {
    const title = escapeHtml(source.title || `Source ${index + 1}`);
    const url = escapeHtml(source.url || "");
    const text = escapeHtml((source.text || "").slice(0, 220));
    const score = typeof source.score === "number" ? `Score: ${source.score.toFixed(4)}` : "";

    return `
      <article class="source-item">
        <h3>${index + 1}. ${title}</h3>
        ${url ? `<a href="${url}" target="_blank" rel="noreferrer">${url}</a>` : ""}
        ${score ? `<p>${score}</p>` : ""}
        ${text ? `<p>${text}</p>` : ""}
      </article>
    `;
  }).join("");
}

async function postJson(path, payload) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Request failed.");
  }

  return data;
}

crawlForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const url = websiteUrlInput.value.trim();

  if (!url) {
    showError("Enter a website URL first.");
    return;
  }

  try {
    setLoading(true, "Crawling");
    answerWindow.innerHTML = `<p class="placeholder">Crawling and indexing ${escapeHtml(url)}...</p>`;
    sourcesList.innerHTML = `<p class="placeholder">Waiting for retrieved sources.</p>`;

    const data = await postJson("/crawl", { url });
    activeWebsiteUrl = url;
    statusPill.textContent = "Indexed";
    showAnswer(data.message || "Website indexed successfully. Ask a question next.");
    showSources(data.sources || []);
  } catch (error) {
    showError(error.message);
  } finally {
    setLoading(false);
  }
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = questionInput.value.trim();

  if (!question) {
    showError("Enter a question first.");
    return;
  }

  try {
    setLoading(true, "Answering");
    answerWindow.innerHTML = `<p class="placeholder">Searching the website context...</p>`;

    const data = await postJson("/chat", {
      url: activeWebsiteUrl || websiteUrlInput.value.trim(),
      question,
    });

    showAnswer(data.answer || data.message || "No answer returned.");
    showSources(data.sources || []);
  } catch (error) {
    showError(error.message);
  } finally {
    setLoading(false);
  }
});

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
