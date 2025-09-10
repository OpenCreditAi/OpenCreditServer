# services/document_analysis.py

import io
import os
import tempfile

from PIL import Image as PILImage
from google.cloud import vision
from pdf2image import convert_from_bytes, convert_from_path
from pdf2image.exceptions import PDFPageCountError
from werkzeug.datastructures import FileStorage

from app.configs.document_analysis_config import (
    VISION_TIMEOUT_SECONDS,
    VISION_LANGUAGE_HINTS,
    DOC_LABEL_THRESHOLD,
    DOC_TEXT_THRESHOLD_CHARS,
    DOC_LABELS_ALLOWLIST,
    ALLOWED_IMAGE_MIMETYPES,
    ALLOWED_DOC_MIMETYPES,
    MAX_PAGES,
)
from app.services.document_analysis.utils import pdf_to_images, convert_to_pdf  # if you still use elsewhere

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "configs", "vision-key.json")

if not os.path.exists(CREDENTIALS_PATH):
    raise FileNotFoundError(f"Service account key not found at {CREDENTIALS_PATH}")

client = vision.ImageAnnotatorClient.from_service_account_file(CREDENTIALS_PATH)


def run_vision_on_image(pil_image: PILImage.Image):
    """Run OCR + label detection on a single Pillow image."""
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    content = buf.getvalue()

    img = vision.Image(content=content)

    # OCR
    ocr_response = client.document_text_detection(
        image=img,
        image_context=vision.ImageContext(language_hints=VISION_LANGUAGE_HINTS),
        timeout=VISION_TIMEOUT_SECONDS,
    )
    ocr_text = ocr_response.full_text_annotation.text if ocr_response.full_text_annotation else ""
    ocr_chars = len(ocr_text.strip())

    # Labels
    label_response = client.label_detection(image=img, timeout=VISION_TIMEOUT_SECONDS)
    best_doc_label_conf = max(
        (lab.score for lab in (label_response.label_annotations or [])
         if (lab.description or "").lower() in DOC_LABELS_ALLOWLIST),
        default=0.0
    )

    return ocr_chars, best_doc_label_conf


def _cap_last_page(default_cap: int = 3) -> int:
    """Respect MAX_PAGES if set; otherwise fallback to a small cap to save costs."""
    if isinstance(MAX_PAGES, int) and MAX_PAGES > 0:
        return min(MAX_PAGES, default_cap)
    return default_cap


def validate_file(file: FileStorage) -> bool:
    """
    Validate an uploaded file WITHOUT mutating or consuming the original stream.

    Strategy:
    - Read the upload into memory (bytes) and immediately rewind the original stream.
    - Validate strictly from that in-memory copy (images/PDFs).
    - For Office docs (docx/xlsx/pptx), write a TEMPORARY COPY only for conversion to PDF.
    """
    mimetype = (file.mimetype or "").lower()

    try:
        # 1) Read once, rewind original to avoid corruption for later save()
        try:
            file.stream.seek(0)
        except Exception:
            pass
        data = file.stream.read()
        try:
            file.stream.seek(0)
        except Exception:
            pass

        if not data:
            return False

        pages = []
        last_page = _cap_last_page(3)

        # 2) Branch by type — work from memory wherever possible
        if mimetype.startswith("image/"):
            # Validate image directly from memory
            try:
                im = PILImage.open(io.BytesIO(data))
                # verify() checks integrity; reopen for actual pixels/format if needed later
                im.verify()
                # Reopen a clean handle for Vision
                im2 = PILImage.open(io.BytesIO(data))
                pages = [im2]
            except Exception:
                return False

        elif mimetype == "application/pdf":
            # Use convert_from_bytes to avoid saving original anywhere
            try:
                pages = convert_from_bytes(
                    data,
                    dpi=200,
                    first_page=1,
                    last_page=last_page
                )
            except PDFPageCountError:
                return False
            except Exception:
                return False

        elif mimetype in {
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        }:
            # For Office docs, write ONLY a temp copy, then convert to PDF from that copy
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Preserve suffix if present
                    _, ext = os.path.splitext(file.filename or "")
                    suffix = ext if ext else ""
                    temp_in = os.path.join(tmpdir, f"in{suffix}")
                    with open(temp_in, "wb") as f:
                        f.write(data)

                    pdf_path = convert_to_pdf(temp_in, tmpdir)  # your util expects paths
                    pages = convert_from_path(
                        pdf_path,
                        dpi=200,
                        first_page=1,
                        last_page=last_page
                    )
            except PDFPageCountError:
                return False
            except Exception:
                return False
        else:
            # unknown/unsupported type — reject early
            return False

        # 3) Aggregate OCR + labels across pages
        total_ocr_chars = 0
        best_label_conf = 0.0

        for p in pages:
            try:
                ocr_chars, label_conf = run_vision_on_image(p)
                total_ocr_chars += ocr_chars
                best_label_conf = max(best_label_conf, label_conf)
            finally:
                try:
                    p.close()
                except Exception:
                    pass

        # 4) Final decision
        return (total_ocr_chars >= DOC_TEXT_THRESHOLD_CHARS) or (best_label_conf >= DOC_LABEL_THRESHOLD)

    except PDFPageCountError:
        return False
    except Exception as e:
        print(e)
        return False # Any unexpected failure means "invalid"
