# Website RAG Chatbot

A professional Retrieval-Augmented Generation (RAG) chatbot that crawls a website, converts its content into searchable embeddings, stores those embeddings in a vector database, and answers user questions using retrieved website context.

The project is built as a learning and engineering workflow for a hackathon-style RAG system. It includes scraping, preprocessing, chunking, embeddings, vector storage, retrieval, an LLM response layer, a Flask API, and a browser-based chatbot frontend.

## What It Does

1. Accepts a website URL from the frontend.
2. Crawls the website using BeautifulSoup.
3. Cleans and preprocesses the page text.
4. Splits the text into chunks.
5. Generates embeddings using Sentence Transformers.
6. Stores chunks and embeddings in ChromaDB.
7. Retrieves the most relevant chunks for a user question.
8. Sends the retrieved context and question to Groq.
9. Displays the answer and source links in the chatbot UI.

## Tech Stack

### Frontend

- HTML
- CSS
- JavaScript
- Fetch API

### Backend

- Python
- Flask
- Flask-CORS
- BeautifulSoup4
- Requests
- Sentence Transformers
- ChromaDB
- Groq API

### RAG Components

- Scraper: BeautifulSoup-based website crawler
- Preprocessing: HTML, URL, email, whitespace, and symbol cleanup
- Chunking: fixed-size overlapping text chunks
- Embeddings: MiniLM sentence-transformer model
- Vector DB: ChromaDB
- Retrieval: top-k semantic search
- LLM: Groq chat completion API

## Project Structure

```text
Website-RAG-Chatbot/
+-- backend/
¦   +-- app.py                    # Flask API for frontend integration
¦   +-- scraper.py                # Website crawler
¦   +-- preprocessing.py          # Text cleaning
¦   +-- pipeline.py               # Scraper + preprocessing pipeline
¦   +-- chunking.py               # Text chunking
¦   +-- embeddings.py             # Embedding generation
¦   +-- vector_stores/            # ChromaDB / FAISS implementations
¦   +-- retriever.py              # Retrieval logic
¦   +-- groq_generator.py         # Groq answer generation
¦   +-- full_rag_pipeline.py      # End-to-end terminal pipeline
¦   +-- test_queries.py           # Multi-query testing script
+-- frontend/
¦   +-- index.html                # Chatbot UI
¦   +-- styles.css                # Frontend styling
¦   +-- app.js                    # Frontend API calls and chat behavior
+-- docs/                         # Module notes and experiment documentation
+-- requirements.txt              # Python dependencies
+-- .gitignore
+-- README.md
```

## Setup Instructions

### 1. Clone the Repository

```powershell
git clone https://github.com/YOUR_USERNAME/Website-RAG-Chatbot.git
cd Website-RAG-Chatbot
```

If you already have the project locally:

```powershell
cd "C:\Users\Lenovo -PC\OneDrive\Documents\GitHub\Website-RAG-Chatbot"
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Get a Groq API Key

Create a free Groq API key from:

```text
https://console.groq.com/keys
```

You can paste this key directly into the frontend UI when running the app.

## Run Locally

### 1. Start the Flask Backend

From the project root:

```powershell
python backend/app.py
```

The backend should run at:

```text
http://127.0.0.1:5000
```

To check if it is working, open:

```text
http://127.0.0.1:5000/
```

You should see a JSON response saying the API is running.

### 2. Open the Frontend

Open this file in your browser:

```text
frontend/index.html
```

Or open it from the full local path:

```text
C:\Users\Lenovo -PC\OneDrive\Documents\GitHub\Website-RAG-Chatbot\frontend\index.html
```

If the browser loads an older version, hard refresh:

```text
Ctrl + F5
```

### 3. Use the Chatbot

1. Paste your Groq API key.
2. Enter a website URL.
3. Click **Ingest Website**.
4. Wait for the ingestion success message.
5. Ask questions about the website in the chat box.

## API Endpoints

### GET `/`

Health check endpoint.

### POST `/crawl`

Crawls and indexes a website.

Request body:

```json
{
  "url": "https://example.com"
}
```

Response includes:

- URL
- document count
- chunk count
- ingestion status

### POST `/chat`

Answers a question using the indexed website content.

Request body:

```json
{
  "question": "What is this website about?",
  "api_key": "your_groq_api_key"
}
```

Response includes:

- answer
- sources
- whether the LLM was used

## Terminal Testing

You can test the full RAG pipeline without the frontend:

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
python backend/full_rag_pipeline.py "https://example.com" "What is this website about?"
```

After a website is loaded into ChromaDB, test multiple queries:

```powershell
python backend/test_queries.py "What is this website about?" "What contact information is available?"
```

## Notes

- The Flask frontend integration uses ChromaDB as the active vector database.
- The selected embedding model is MiniLM because it was more efficient during experimentation.
- The selected LLM provider is Groq because it is practical for free-tier hackathon use.
- The crawler follows internal website links based on the configured crawl depth.
- Generated vector database files are stored under `artifacts/`, which is ignored by Git.

## Common Issues

### `Failed to fetch`

The frontend cannot reach Flask. Start the backend first:

```powershell
python backend/app.py
```

### API key error

Make sure the Groq API key is valid and pasted correctly in the frontend.

### Website answers seem old

Run **Ingest Website** again. The backend resets the ChromaDB collection during ingestion so the newest website replaces the previous indexed content.

### Crawling is slow

Some websites have many internal links or slow responses. Start with a small site first, then increase crawl depth later if needed.

## Git Workflow Used

The project was developed using feature and experiment branches, including:

- `experiment/MiniLM`
- `experiment/BGE-Small`
- `experiment/FAISS`
- `experiment/ChromaDB`
- `experiment/Gemini`
- `experiment/Groq`
- `feature/frontend`
- `feature/flask`

The final working stack is merged into `main`.
