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
    # >>> NEW: classification config
    ACCEPTED_DOC_TYPES,           # e.g., {"invoice","bank_statement","paystub","real_estate_contract",...}
    DOC_CLASSIFY_THRESHOLD,       # e.g., 3.0
    FINRE_KW,                     # keyword dict from config (financial + real-estate)
    FINRE_REGEX,                  # compiled regex dict from config
)
from app.services.document_analysis.utils import pdf_to_images, convert_to_pdf  # if you still use elsewhere

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "configs", "vision-key.json")

if not os.path.exists(CREDENTIALS_PATH):
    raise FileNotFoundError(f"Service account key not found at {CREDENTIALS_PATH}")

client = vision.ImageAnnotatorClient.from_service_account_file(CREDENTIALS_PATH)


def run_vision_on_image(pil_image: PILImage.Image):
    """Run OCR + label detection on a single Pillow image. Returns (text, chars, best_label_conf)."""
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
    ocr_text = ocr_text or ""
    ocr_chars = len(ocr_text.strip())

    # Labels
    label_response = client.label_detection(image=img, timeout=VISION_TIMEOUT_SECONDS)
    best_doc_label_conf = max(
        (lab.score for lab in (label_response.label_annotations or [])
         if (lab.description or "").lower() in DOC_LABELS_ALLOWLIST),
        default=0.0
    )

    return ocr_text, ocr_chars, best_doc_label_conf


def _cap_last_page(default_cap: int = 3) -> int:
    """Respect MAX_PAGES if set; otherwise fallback to a small cap to save costs."""
    if isinstance(MAX_PAGES, int) and MAX_PAGES > 0:
        return min(MAX_PAGES, default_cap)
    return default_cap


# ---- NEW: tiny rules-based classifier that uses config-provided keywords/regex ----
def _kw_score(category: str, text: str) -> float:
    s = 0.0
    lower = text.lower()
    # English keywords
    for w in FINRE_KW.get(category, {}).get("en", []):
        if w in lower:
            s += 0.8
    # Hebrew keywords (keep case)
    for w in FINRE_KW.get(category, {}).get("he", []):
        if w and w in text:
            s += 0.8
    return s


def classify_document(text: str, label_conf: float):
    cats = list(FINRE_KW.keys())
    score = {c: 0.0 for c in cats}
    lower = text.lower()

    # Keyword base
    def kw(cat):
        s = 0.0
        for w in FINRE_KW.get(cat, {}).get("en", []):
            if w in lower:
                s += 0.7
        for w in FINRE_KW.get(cat, {}).get("he", []):
            if w and w in text:
                s += 0.8
        return s

    for c in cats:
        score[c] += kw(c)

    # Feature counts
    def cm(key):
        p = FINRE_REGEX.get(key)
        return len(p.findall(text)) if p else 0

    amounts    = cm("money_amount")
    dates      = cm("dates")
    has_tbl_en = FINRE_REGEX["table_headers_en"].search(text) is not None
    has_tbl_he = FINRE_REGEX["table_headers_he"].search(text) is not None
    bank_table = has_tbl_en or has_tbl_he
    debitcred  = cm("debit_credit_he")
    acct_hits  = cm("acct_no")
    iban_hits  = cm("iban_any") + cm("iban_il")

    inv_hdr_he = FINRE_REGEX["invoice_headers_he"].search(text) is not None
    inv_hdr_en = FINRE_REGEX["invoice_headers_en"].search(text) is not None
    inv_no     = cm("invoice_no") > 0
    invoiceish = inv_hdr_he or inv_hdr_en or inv_no

    # after you compute amounts/dates/bank_table/etc.
    is_letter_open = bool(FINRE_REGEX["letter_openers_he"].search(text))
    is_letter_close = bool(FINRE_REGEX["formal_closing_he"].search(text))
    bank_name_hit = bool(FINRE_REGEX["bank_name_he"].search(text) or FINRE_REGEX["bank_name_en"].search(text))
    il_triplet = FINRE_REGEX["il_account_triplet"].search(text) is not None
    has_url = FINRE_REGEX["has_url"].search(text) is not None

    # ---- Financial boosts ----
    if "invoice" in score:
        score["invoice"] += (1.0 if invoiceish else 0.0)
        score["invoice"] += min(3, amounts) * 0.3

    if "bank_statement" in score:
        # Signature: transaction table OR lots of rows that look like movement + account id
        signature = (bank_table or ((amounts >= 6 and dates >= 4) and (acct_hits >= 1 or iban_hits >= 1)))
        if signature:
            score["bank_statement"] += 1.4
        score["bank_statement"] += min(3, amounts) * 0.2
        score["bank_statement"] += min(3, dates) * 0.2
        score["bank_statement"] += min(2, debitcred) * 0.5
        # Strong penalty when it looks like a product/quote sheet (what fooled your example)
        if invoiceish and not bank_table:
            score["bank_statement"] -= 1.2
        # If it looks like a letter and lacks a transaction table, dampen bank_statement
        if (is_letter_open or is_letter_close or bank_name_hit) and not bank_table and amounts <= 2:
            score["bank_statement"] -= 0.8

    if "paystub" in score:
        if ("paystub" in lower) or ("תלוש שכר" in text):
            score["paystub"] += 1.5
        score["paystub"] += min(2, amounts) * 0.3

    # ---- Real-estate boosts ----
    tabu   = FINRE_REGEX["israeli_tabu"].search(text) is not None
    parcel = cm("parcel_block") + cm("lot_block_en")
    mortgage = cm("mortgage")
    lien  = cm("lien")

    if "real_estate_deed" in score:
        score["real_estate_deed"] += (1.6 if tabu else 0.0)
        score["real_estate_deed"] += min(3, parcel) * 0.6
        # If deed signatures exist, reduce bank-statement drift
        if tabu or parcel:
            score["bank_statement"] -= 0.8

    if "real_estate_contract" in score:
        # Contracts often mention parties/roles; keyword list already helps.
        score["real_estate_contract"] += min(2, parcel) * 0.3

    if "loan_agreement" in score:
        score["loan_agreement"] += (1.2 if mortgage else 0.0)
        score["loan_agreement"] += (0.8 if lien else 0.0)

    if "appraisal" in score:
        score["appraisal"] += (1.2 if FINRE_REGEX["appraisal_terms"].search(text) else 0.0)
        score["appraisal"] += (1.2 if FINRE_REGEX["appraisal_he"].search(text) else 0.0)

    if "account_confirmation" in score:
        # Strong positive cues
        score["account_confirmation"] += (1.2 if is_letter_open else 0.0)
        score["account_confirmation"] += (0.6 if is_letter_close else 0.0)
        score["account_confirmation"] += (0.8 if bank_name_hit else 0.0)
        score["account_confirmation"] += (0.8 if il_triplet else 0.0)
        score["account_confirmation"] += (0.3 if has_url else 0.0)
        # Letters rarely have transaction tables — give a small bonus when tables are absent
        if not bank_table and amounts <= 2:
            score["account_confirmation"] += 0.5
    if "building_permit" in score:
        if FINRE_REGEX["building_permit_he"].search(text):
            score["building_permit"] += 1.5
        if FINRE_REGEX["building_law_he"].search(text):
            score["building_permit"] += 0.8
        # Bonus for presence of "ועדה מקומית לתכנון ובניה"
        if "ועדה מקומית" in text:
            score["building_permit"] += 1.0
        # These permits list גוש/חלקה too, so piggyback on that
        score["building_permit"] += min(2, cm("parcel_block")) * 0.4

    # ---- Vision label bonus (capped, smaller) ----
    bonus = min(0.6, label_conf)
    for c in cats:
        score[c] += bonus

    # Choose best
    best_type = max(score, key=score.get)
    return best_type, score[best_type], {"score": score}


def validate_file(file: FileStorage) -> bool:
    """
    Validate an uploaded file WITHOUT mutating or consuming the original stream.

    Strategy:
    - Read the upload into memory (bytes) and immediately rewind the original stream.
    - Validate strictly from that in-memory copy (images/PDFs).
    - For Office docs (docx/xlsx/pptx), write a TEMPORARY COPY only for conversion to PDF.
    - After OCR, classify text; accept only configured financial/real-estate types.
    """
    mimetype = (file.mimetype or "").lower()

    try:
        # 1) Read once, rewind original to avoid corruption for later save()
        try:
            file.stream.seek(0)
        except Exception as e:
            print(e)
            pass
        data = file.stream.read()
        try:
            file.stream.seek(0)
        except Exception as e:
            print(e)
            pass

        if not data:
            return False

        pages = []
        last_page = _cap_last_page(3)

        # 2) Branch by type — work from memory wherever possible
        if mimetype.startswith("image/"):
            try:
                im = PILImage.open(io.BytesIO(data))
                im.verify()
                im2 = PILImage.open(io.BytesIO(data))
                pages = [im2]
            except Exception as e:
                print(e)
                return False

        elif mimetype == "application/pdf":
            try:
                pages = convert_from_bytes(
                    data,
                    dpi=200,
                    first_page=1,
                    last_page=last_page
                )
            except PDFPageCountError:
                return False
            except Exception as e:
                print(e)
                return False

        elif mimetype in {
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        }:
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    _, ext = os.path.splitext(file.filename or "")
                    suffix = ext if ext else ""
                    temp_in = os.path.join(tmpdir, f"in{suffix}")
                    with open(temp_in, "wb") as f:
                        f.write(data)

                    pdf_path = convert_to_pdf(temp_in, tmpdir)
                    pages = convert_from_path(
                        pdf_path,
                        dpi=200,
                        first_page=1,
                        last_page=last_page
                    )
            except PDFPageCountError:
                return False
            except Exception as e:
                print(e)
                return False
        else:
            return False

        # 3) OCR + label aggregation
        total_ocr_chars = 0
        best_label_conf = 0.0
        page_texts = []

        for p in pages:
            try:
                text, ocr_chars, label_conf = run_vision_on_image(p)
                total_ocr_chars += ocr_chars
                best_label_conf = max(best_label_conf, label_conf)
                if text:
                    page_texts.append(text)
            finally:
                try:
                    p.close()
                except Exception:
                    pass

        # Fail fast on empty/near-empty content (keeps your old behavior)
        if total_ocr_chars < max(64, DOC_TEXT_THRESHOLD_CHARS // 4):
            return False

        # 4) Classification gate (financial + real-estate)
        joined = "\n".join(page_texts)
        doc_type, doc_score, _dbg = classify_document(joined, best_label_conf)

        # Accept only targeted types above threshold
        if (doc_type in ACCEPTED_DOC_TYPES) and (doc_score >= DOC_CLASSIFY_THRESHOLD):
            return True

        # Otherwise, reject (even if it had text)
        return False

    except PDFPageCountError:
        return False
    except Exception as e:
        print(e)
        return False  # Any unexpected failure means "invalid"
