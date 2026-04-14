import os
from unstructured.partition.auto import partition


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def extract_text(filepath: str, ocr_mode: bool = False) -> str:
    """
    Extract text using the unstructured library.
    It automatically detects if it's PDF, DOCX, or PPTX.
    
    If ocr_mode is True, uses 'hi_res' strategy which runs OCR via Tesseract.
    If False, uses 'fast' strategy (text-only, fast, no system deps).
    """
    try:
        strategy = "hi_res" if ocr_mode else "fast"
        
        # unstructured.partition auto-detects the file type
        elements = partition(filename=filepath, strategy=strategy)
        
        # Join all extracted text elements cleanly
        text_parts = [str(el).strip() for el in elements if str(el).strip()]
        return "\n\n".join(text_parts)
        
    except Exception as e:
        raise RuntimeError(f"Text extraction failed: {e}")
