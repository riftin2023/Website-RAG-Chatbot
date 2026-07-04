const BACKEND_URL = 'http://127.0.0.1:5000';

// DOM Elements
const apiKeyInput = document.getElementById('groq-api-key');
const urlInput = document.getElementById('website-url');
const ingestBtn = document.getElementById('btn-ingest');
const ingestStatus = document.getElementById('ingest-status');
const activeUrlBadge = document.getElementById('active-url-badge');

const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('btn-send');

// State
let activeUrl = null;

// Event Listeners
ingestBtn.addEventListener('click', handleIngest);
sendBtn.addEventListener('click', handleSend);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
});

// Input handling to enable/disable button based on text
chatInput.addEventListener('input', () => {
    sendBtn.disabled = chatInput.value.trim().length === 0;
});

async function handleIngest() {
    const url = urlInput.value.trim();
    if (!url) {
        showStatus('Please enter a website URL.', 'error');
        return;
    }

    // UI Loading state
    setIngestLoading(true);
    showStatus('Ingesting website. This may take a minute...', 'success'); // using success color just for neutral info
    
    try {
        const response = await fetch(`${BACKEND_URL}/crawl`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to ingest website');
        }
        
        // Success
        activeUrl = data.url;
        activeUrlBadge.textContent = `Active: ${new URL(activeUrl).hostname}`;
        activeUrlBadge.classList.remove('hidden');
        activeUrlBadge.classList.add('active');
        
        showStatus(`Ingested successfully! (${data.document_count} pages, ${data.chunk_count} chunks)`, 'success');
        
        // Enable chat
        chatInput.disabled = false;
        addSystemMessage(`Website ingested successfully! You can now ask questions about ${activeUrl}.`);
        
    } catch (error) {
        showStatus(error.message, 'error');
    } finally {
        setIngestLoading(false);
    }
}

async function handleSend() {
    const question = chatInput.value.trim();
    if (!question) return;
    
    const apiKey = apiKeyInput.value.trim();
    
    // Add user message to UI
    addUserMessage(question);
    
    // Clear input
    chatInput.value = '';
    chatInput.disabled = true;
    sendBtn.disabled = true;
    
    // Add temporary loading message for AI
    const loadingId = addAILoadingMessage();
    
    try {
        const response = await fetch(`${BACKEND_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                question: question,
                api_key: apiKey
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to get answer');
        }
        
        // Replace loading message with actual answer
        replaceAILoadingMessage(loadingId, data.answer, data.sources);
        
    } catch (error) {
        replaceAILoadingMessage(loadingId, `Error: ${error.message}`);
    } finally {
        chatInput.disabled = false;
        chatInput.focus();
    }
}

// UI Helpers
function setIngestLoading(isLoading) {
    const btnText = ingestBtn.querySelector('.btn-text');
    const loader = ingestBtn.querySelector('.loader');
    
    ingestBtn.disabled = isLoading;
    urlInput.disabled = isLoading;
    
    if (isLoading) {
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
    } else {
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

function showStatus(message, type) {
    ingestStatus.textContent = message;
    ingestStatus.className = `status-message ${type}`;
    ingestStatus.classList.remove('hidden');
}

function addUserMessage(text) {
    const html = `
        <div class="message user-message">
            <div class="message-content">${escapeHTML(text)}</div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
}

function addSystemMessage(text) {
    const html = `
        <div class="message system-message">
            <div class="message-content">${escapeHTML(text)}</div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
}

function addAILoadingMessage() {
    const id = 'msg-' + Date.now();
    const html = `
        <div id="${id}" class="message ai-message">
            <div class="message-content">
                <div class="loader"></div>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
    return id;
}

function replaceAILoadingMessage(id, text, sources = null) {
    const msgElement = document.getElementById(id);
    if (!msgElement) return;
    
    let contentHtml = `<p>${formatMarkdown(text)}</p>`;
    
    if (sources && sources.length > 0) {
        // Unique sources
        const uniqueUrls = [...new Set(sources.filter(s => s.url).map(s => s.url))];
        if (uniqueUrls.length > 0) {
            contentHtml += `<div class="sources">`;
            uniqueUrls.forEach(url => {
                const urlObj = new URL(url);
                contentHtml += `<a href="${url}" target="_blank" class="source-badge">${urlObj.pathname || urlObj.hostname}</a>`;
            });
            contentHtml += `</div>`;
        }
    }
    
    msgElement.querySelector('.message-content').innerHTML = contentHtml;
    scrollToBottom();
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Extremely basic markdown and html escaping for safety and basic formatting
function escapeHTML(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatMarkdown(str) {
    const escaped = escapeHTML(str);
    return escaped
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}
