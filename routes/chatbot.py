from flask import Blueprint, request, jsonify
from utils.rag_pipeline import answer_question

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/api/chat", methods=["POST"])
def chat():
    """
    Accepts a user question, retrieves chunks from the vector store, 
    and generates an answer via Ollama.
    """
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "No question provided."}), 400

    query = data["question"].strip()
    if not query:
        return jsonify({"error": "Question is empty."}), 400

    try:
        # Call the RAG pipeline to get answer and reference chunks
        answer, context_chunks = answer_question(query)
        
        return jsonify({
            "answer": answer,
            "context": context_chunks
        })
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
