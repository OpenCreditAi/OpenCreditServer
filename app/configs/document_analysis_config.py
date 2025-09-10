# config/document_analysis_config.py

# OCR text length threshold: if OCR detects more than this many chars,
# we consider it likely a document.
DOC_TEXT_THRESHOLD_CHARS = 25

# Minimum confidence for document-related labels like "Document", "Paper", etc.
DOC_LABEL_THRESHOLD = 0.70

# Which labels from Google Vision we consider as indicators of "documentness".
ALLOWED_IMAGE_MIMETYPES = {
    "image/jpeg", "image/png", "image/gif",
    "image/bmp", "image/webp", "image/tiff"
}
ALLOWED_DOC_MIMETYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation"
}


# Language hints for OCR (for Hebrew detection, use "he")
VISION_LANGUAGE_HINTS = ["he"]

# Timeout for Vision requests (in seconds)
VISION_TIMEOUT_SECONDS = 10

# --- constants ---
DOC_LABELS_ALLOWLIST = {"document", "paper", "receipt", "invoice", "text", "book", "page"}
MAX_PAGES = 3  # process up to 3 pages
