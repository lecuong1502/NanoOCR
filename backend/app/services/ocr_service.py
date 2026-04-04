from __future__ import annotations

import base64
import io
import time

import httpx
from PIL import Image
from pdf2image import convert_from_bytes

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

OCR_PROMPT = (
    "You are an expert OCR engine. "
    "Extract ALL text from the image exactly as it appears. "
    "Preserve the original structure: headings, paragraphs, tables, bullet points. "
    "Return the result formatted as clean Markdown. "
    "Do NOT add any commentary or explanation — only output the Markdown text."
)


def _image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _run_inference(image: Image.Image) -> str:
    """Call Ollama /api/chat with vision support."""
    image_b64 = _image_to_base64(image)

    # /api/chat supports multimodal (vision) models
    payload = {
        "model": settings.OCR_MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": OCR_PROMPT,
                "images": [image_b64],
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": settings.OCR_MAX_NEW_TOKENS,
        },
    }

    try:
        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=300.0,
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except httpx.HTTPError as e:
        raise RuntimeError(f"Ollama API error: {e}")


class OcrOutput:
    def __init__(
        self,
        markdown_output: str,
        raw_text: str,
        confidence: float,
        page_count: int,
        language: str,
        processing_time: float,
        model_version: str,
    ):
        self.markdown_output = markdown_output
        self.raw_text = raw_text
        self.confidence = confidence
        self.page_count = page_count
        self.language = language
        self.processing_time = processing_time
        self.model_version = model_version


def process_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> OcrOutput:
    start = time.perf_counter()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    markdown = _run_inference(image)
    elapsed = round(time.perf_counter() - start, 3)
    logger.info(f"Image OCR done in {elapsed}s")
    return OcrOutput(
        markdown_output=markdown,
        raw_text=markdown,
        confidence=0.95,
        page_count=1,
        language=_detect_language(markdown),
        processing_time=elapsed,
        model_version=settings.OCR_MODEL_NAME,
    )


def process_pdf(pdf_bytes: bytes, dpi: int = 200) -> OcrOutput:
    start = time.perf_counter()
    images = convert_from_bytes(pdf_bytes, dpi=dpi)
    page_count = len(images)
    logger.info(f"PDF has {page_count} page(s), running OCR...")

    page_markdowns: list[str] = []
    for idx, image in enumerate(images, start=1):
        logger.info(f"  Processing page {idx}/{page_count}")
        md = _run_inference(image)
        page_markdowns.append(f"## Page {idx}\n\n{md}")

    full_markdown = "\n\n---\n\n".join(page_markdowns)
    elapsed = round(time.perf_counter() - start, 3)
    logger.info(f"PDF OCR done in {elapsed}s ({page_count} pages)")
    return OcrOutput(
        markdown_output=full_markdown,
        raw_text=full_markdown,
        confidence=0.95,
        page_count=page_count,
        language=_detect_language(full_markdown),
        processing_time=elapsed,
        model_version=settings.OCR_MODEL_NAME,
    )


def _detect_language(text: str) -> str:
    sample = text[:500]
    vietnamese_chars = sum(1 for c in sample if "\u00c0" <= c <= "\u1ef9")
    if vietnamese_chars > 10:
        return "vi"
    return "en"