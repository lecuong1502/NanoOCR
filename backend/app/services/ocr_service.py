from __future__ import annotations

import io
import time

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration
from qwen_vl_utils import process_vision_info
from pdf2image import convert_from_bytes

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Model singleton ────────────────────────────────────────
_processor: AutoProcessor | None = None
_model: Qwen3VLForConditionalGeneration | None = None


def _load_model() -> tuple[AutoProcessor, Qwen3VLForConditionalGeneration]:
    global _processor, _model
    if _model is None:
        logger.info(f"Loading model: {settings.OCR_MODEL_NAME} ...")
        _processor = AutoProcessor.from_pretrained(
            settings.OCR_MODEL_NAME,
            cache_dir=settings.OCR_MODEL_PATH,
        )
        _model = Qwen3VLForConditionalGeneration.from_pretrained(
            settings.OCR_MODEL_NAME,
            cache_dir=settings.OCR_MODEL_PATH,
            torch_dtype=torch.float16 if settings.OCR_DEVICE == "cuda" else torch.float32,
            device_map=settings.OCR_DEVICE,
        )
        _model.eval()
        logger.info("Model loaded successfully.")
    return _processor, _model 


# ── OCR Prompt ─────────────────────────────────────────────
OCR_PROMPT = (
    "You are an expert OCR engine. "
    "Extract ALL text from the image exactly as it appears. "
    "Preserve the original structure: headings, paragraphs, tables, bullet points. "
    "Return the result formatted as clean Markdown. "
    "Do NOT add any commentary or explanation — only output the Markdown text."
)


def _build_prompt() -> str:
    """
    Build prompt manually using Qwen3-VL's ChatML format:
 
    <|im_start|>system
    You are a helpful assistant.<|im_end|>
    <|im_start|>user
    <|vision_start|><|image_pad|><|vision_end|>
    {user message}<|im_end|>
    <|im_start|>assistant
    """
    return (
        "<|im_start|>system\n"
        "You are a helpful assistant.<|im_end|>\n"
        "<|im_start|>user\n"
        "<|vision_start|><|image_pad|><|vision_end|>\n"
        f"{OCR_PROMPT}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


# ── Core Inference ─────────────────────────────────────────

def _run_inference(image: Image.Image) -> str:
    """Run Qwen3-VL on a single PIL image and return Markdown text."""
    processor, model, tokenizer = _load_model()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text",  "text": OCR_PROMPT},
            ],
        }
    ]

    # Build prompt manually — chuẩn ChatML format của Qwen3-VL
    text_input = _build_prompt()

    # Extract image tensors via qwen_vl_utils
    image_inputs, video_inputs = process_vision_info(messages)

    # Build model inputs
    inputs = processor(
        text=[text_input],
        images=image_inputs,
        videos=video_inputs,
        return_tensors="pt",
        padding=True,
    )

    inputs = {
        k: v.to(settings.OCR_DEVICE) if isinstance(v, torch.Tensor) else v 
        for k, v in inputs.items()
    }

    # Generate
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=settings.OCR_MAX_NEW_TOKENS,
            do_sample=False,
        )

    # Trim prompt tokens, decode output only
    generated_ids_trimmed = [
        out_ids[len(in_ids):]
        for in_ids, out_ids in zip(inputs.input_ids, output_ids)
    ]
    return processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0].strip()


# ── Output dataclass ───────────────────────────────────────

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


# ── Public API ─────────────────────────────────────────────

def process_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> OcrOutput:
    """OCR a single image and return structured output."""
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
    """Convert PDF pages to images then OCR each page."""
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
    """Naive language detection based on Unicode character ranges."""
    sample = text[:500]
    vietnamese_chars = sum(1 for c in sample if "\u00c0" <= c <= "\u1ef9")
    if vietnamese_chars > 10:
        return "vi"
    return "en"