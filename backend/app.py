from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.get("/")
def health_check():
    return jsonify(
        {
            "message": "Website RAG Chatbot API is running.",
            "endpoints": ["POST /crawl", "POST /chat"],
        }
    )


@app.post("/crawl")
def crawl_website():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "url is required."}), 400

    return jsonify(
        {
            "message": "Hello World from /crawl",
            "url": url,
            "document_count": 0,
            "chunk_count": 0,
            "sources": [],
        }
    )


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "question is required."}), 400

    return jsonify(
        {
            "message": "Hello World from /chat",
            "question": question,
            "answer": "Hello World",
            "sources": [],
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
