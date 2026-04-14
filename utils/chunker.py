from typing import List


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 150) -> List[str]:
    """
    Split text into overlapping chunks.
    chunk_size: target characters per chunk
    overlap: characters of overlap between consecutive chunks
    """
    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        # Try to break on a sentence boundary (. or \n) within last 300 chars
        if end < text_len:
            boundary = text.rfind("\n", start, end)
            if boundary == -1 or (end - boundary) > 300:
                boundary = text.rfind(". ", start, end)
            if boundary != -1 and boundary > start:
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start forward (accounting for overlap)
        start = end - overlap
        if start <= 0 or start >= text_len:
            break

    return chunks


def assemble_context(chunks: List[str], max_chars: int = 4000) -> str:
    """
    Assemble retrieved chunks into a single context string for the LLM.
    Truncates if total exceeds max_chars to stay within model context window.
    """
    context_parts = []
    total = 0
    for i, chunk in enumerate(chunks):
        header = f"--- Retrieved Chunk {i + 1} ---\n"
        block = header + chunk + "\n"
        if total + len(block) > max_chars:
            break
        context_parts.append(block)
        total += len(block)
    return "\n".join(context_parts)
