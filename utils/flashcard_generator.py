import json
import re
import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

SYSTEM_PROMPT = """You are an expert educational flashcard generator.
Generate flashcards strictly from the provided context.

Rules:
- Use ONLY the provided context.
- Generate 8-12 flashcards.
- Each flashcard needs: question, answer, topic, difficulty.
- difficulty must be exactly one of: Easy, Medium, Hard
- Output ONLY a valid JSON object. No explanation, no markdown, no extra text.

Required JSON format:
{
  "title": "Document Flashcards",
  "flashcards": [
    {
      "question": "What is X?",
      "answer": "X is ...",
      "topic": "Subject",
      "difficulty": "Easy"
    }
  ]
}"""


def generate_flashcards(context: str) -> dict:
    """
    Call the local Ollama model (gemma2:2b) using the chat messages API
    for better instruction-following and JSON output.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nGenerate the JSON flashcards now:"},
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 1024,
            "num_ctx": 4096,
        },
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is running (ollama serve)."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama request timed out. The model may be loading or the document is too large.")
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if e.response is not None:
            try:
                error_msg += f". Details: {e.response.json().get('error', e.response.text)}"
            except Exception:
                error_msg += f". Details: {e.response.text}"
        raise RuntimeError(f"Ollama API error: {error_msg}")

    resp_json = response.json()
    raw_text = resp_json.get("message", {}).get("content", "")

    # Extract JSON from response
    return _parse_json_response(raw_text)


def _parse_json_response(raw: str) -> dict:
    """Extract and validate the JSON flashcard object from the LLM response."""
    text = raw.strip()
    
    # Remove markdown code blocks if present
    if "```" in text:
        # Try to find content between ```json and ``` or just ``` and ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()

    # Try direct parse
    try:
        data = json.loads(text)
        return _validate_flashcards(data)
    except json.JSONDecodeError:
        pass

    # Find the outermost { } block
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidate = match.group()
        try:
            data = json.loads(candidate)
            return _validate_flashcards(data)
        except json.JSONDecodeError:
            # Try to fix common trailing noise like dots or extra text after }
            # by finding the last closing brace
            last_brace = candidate.rfind('}')
            if last_brace != -1:
                try:
                    data = json.loads(candidate[:last_brace+1])
                    return _validate_flashcards(data)
                except json.JSONDecodeError:
                    pass

    return {
        "title": "Document Flashcards",
        "flashcards": [],
        "error": "The model response was not in a valid JSON format. Try again or simplify the document.",
    }


def _validate_flashcards(data: dict) -> dict:
    """Ensure the flashcard structure is valid; strip bad entries."""
    valid_difficulties = {"Easy", "Medium", "Hard"}
    cards = data.get("flashcards", [])
    cleaned = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        q = card.get("question", "").strip()
        a = card.get("answer", "").strip()
        t = card.get("topic", "General").strip()
        d = card.get("difficulty", "Medium").strip()
        if not q or not a:
            continue
        if d not in valid_difficulties:
            d = "Medium"
        cleaned.append({"question": q, "answer": a, "topic": t, "difficulty": d})

    return {"title": "Document Flashcards", "flashcards": cleaned}
