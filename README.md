# FlashGen AI — Smart Flashcard Generator

FlashGen AI is a premium, RAG-powered web application that turns your study materials (PDF, DOCX, PPTX) into educational flashcards. It runs 100% locally using **Ollama** and the **phi3** model, ensuring your data stays private.

## ✨ Features
- **File Parsing**: Support for PDF, Word (.docx), and PowerPoint (.pptx).
- **RAG-Powered**: Uses intelligent text chunking and context assembly to ground flashcards in your documents.
- **Premium UI**: Modern dark-mode interface with glassmorphism and smooth animations.
- **Interactive Study**: Flip cards to reveal answers and filter by difficulty (Easy, Medium, Hard).
- **Export Utility**: Download your generated flashcards as a JSON file for backup or other tools.

## 🛠️ Prerequisites
- **Python 3.10+**
- **Ollama**: [Download and install Ollama](https://ollama.ai/)
- **Phi-3 Model**: Run `ollama pull phi3` to download the default model.

## 🚀 Setup & Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd flask-card
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure `.env`**:
    - Copy `.env.example` to `.env`.
    - Ensure `OLLAMA_BASE_URL` matches your local Ollama instance (default: `http://localhost:11434`).

## 🏃 Running the Application

1.  **Start Ollama**: Make sure `ollama serve` is running.
2.  **Start Flask**:
    ```bash
    python app.py
    ```
3.  **Open in browser**: Navigate to `http://localhost:5000`.

## 📁 Project Structure
- `app.py`: Flask entry point.
- `routes/`: API endpoints for upload and generation.
- `utils/`: Core logic for parsing, chunking, and AI generation.
- `static/`: CSS, Javascript, and assets.
- `templates/`: HTML frontend.
