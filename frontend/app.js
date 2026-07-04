const API_BASE_URL = "http://127.0.0.1:5000";

const crawlForm = document.querySelector("#crawl-form");
const chatForm = document.querySelector("#chat-form");
const apiKeyInput = document.querySelector("#api-key");
const websiteUrlInput = document.querySelector("#website-url");
const questionInput = document.querySelector("#question-input");
const messages = document.querySelector("#messages");
const ingestStatus = document.querySelector("#ingest-status");
const activePill = document.querySelector("#active-pill");
const crawlButton = document.querySelector("#crawl-button");
const askButton = document.querySelector("#ask-button");

let activeWebsiteUrl = "";
let loadingMessage = null;

function setBusy(isBusy, label = "Working") {
  crawlButton.disabled = isBusy;
  askButton.disabled = isBusy;
  activePill.textContent = isBusy ? label : activeWebsiteUrl ? `Active: ${shortenUrl(activeWebsiteUrl)}` : "Inactive";
}

function setIngestStatus(message, type = "info") {
  ingestStatus.textContent = message;
  ingestStatus.classList.toggle("success", type === "success");
  ingestStatus.classList.toggle("error", type === "error");
}

function addMessage(role, text, sources = []) {
  const message = document.createElement("article");
  message.className = `message ${role === "user" ? "user-message" : "assistant-message"}`;

  const body = document.createElement("p");
  body.textContent = text;
  message.appendChild(body);

  if (sources.length) {
    const tags = document.createElement("div");
    tags.className = "source-tags";

    sources.slice(0, 5).forEach((source) => {
      const tag = document.createElement("span");
      tag.className = "source-tag";
      tag.textContent = source.url || source.title || "Source";
      tags.appendChild(tag);
    });

    message.appendChild(tags);
  }

  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
  return message;
}

function addLoadingMessage(text) {
  removeLoadingMessage();
  loadingMessage = addMessage("assistant", text);
  loadingMessage.classList.add("loading-dots");
}

function removeLoadingMessage() {
  if (loadingMessage) {
    loadingMessage.remove();
    loadingMessage = null;
  }
}

function addErrorMessage(text) {
  const message = addMessage("assistant", text);
  message.classList.add("error-message");
}

async function postJson(path, payload) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || data.message || "Request failed.");
  }

  return data;
}

crawlForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const apiKey = apiKeyInput.value.trim();
  const url = websiteUrlInput.value.trim();

  if (!apiKey) {
    setIngestStatus("Groq API key is required", "error");
    return;
  }

  if (!url) {
    setIngestStatus("Website URL is required", "error");
    return;
  }

  try {
    setBusy(true, "Crawling");
    setIngestStatus("Ingesting website...");
    addLoadingMessage(`Ingesting ${url}`);

    const data = await postJson("/crawl", {
      api_key: apiKey,
      url,
    });

    activeWebsiteUrl = url;
    removeLoadingMessage();
    setIngestStatus(
      data.message || `Ingested successfully (${data.document_count || 0} pages, ${data.chunk_count || 0} chunks)`,
      "success"
    );
    addMessage("assistant", data.message || "Website ingested successfully. Ask a question now.", data.sources || []);
  } catch (error) {
    removeLoadingMessage();
    setIngestStatus(error.message, "error");
    addErrorMessage(error.message);
  } finally {
    setBusy(false);
  }
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const apiKey = apiKeyInput.value.trim();
  const question = questionInput.value.trim();
  const url = activeWebsiteUrl || websiteUrlInput.value.trim();

  if (!apiKey) {
    addErrorMessage("Groq API key is required before asking questions.");
    return;
  }

  if (!question) {
    return;
  }

  addMessage("user", question);
  questionInput.value = "";

  try {
    setBusy(true, "Answering");
    addLoadingMessage("Searching the website context");

    const data = await postJson("/chat", {
      api_key: apiKey,
      url,
      question,
    });

    removeLoadingMessage();
    addMessage("assistant", data.answer || data.message || "No answer returned.", data.sources || []);
  } catch (error) {
    removeLoadingMessage();
    addErrorMessage(error.message);
  } finally {
    setBusy(false);
  }
});

function shortenUrl(url) {
  try {
    return new URL(url).hostname;
  } catch {
    return url.slice(0, 24);
  }
}
