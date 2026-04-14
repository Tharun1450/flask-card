import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from utils.file_parser import extract_text, allowed_file
from utils.chunker import chunk_text, assemble_context
from utils.rag_pipeline import index_document
from utils.vector_store import vector_db
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        return jsonify(
            {"error": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}
        ), 400

    # Save the file temporarily
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(filepath)

    # Check if OCR mode was requested
    ocr_mode = request.form.get("ocr_mode") == "true"

    try:
        raw_text = extract_text(filepath, ocr_mode=ocr_mode)
    except Exception as e:
        os.remove(filepath)
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file after extraction
        if os.path.exists(filepath):
            os.remove(filepath)

    if not raw_text or len(raw_text.strip()) < 50:
        return jsonify({"error": "Could not extract enough text from the file."}), 422

    chunks = chunk_text(raw_text)
    context = assemble_context(chunks)

    # --- RAG Indexing ---
    # Clear previous document from the vector store so we only query the new document
    vector_db.clear()
    # Index the new document chunks into ChromaDB
    index_document(chunks, filename)
    # --------------------

    return jsonify({
        "message": "File processed successfully.",
        "filename": filename,
        "chunk_count": len(chunks),
        "context": context,
    })
