from flask import Blueprint, request, jsonify
from utils.flashcard_generator import generate_flashcards

flashcards_bp = Blueprint("flashcards", __name__)


@flashcards_bp.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data or "context" not in data:
        return jsonify({"error": "No context provided."}), 400

    context = data["context"].strip()
    if not context:
        return jsonify({"error": "Context is empty."}), 400

    try:
        result = generate_flashcards(context)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

    return jsonify(result)
