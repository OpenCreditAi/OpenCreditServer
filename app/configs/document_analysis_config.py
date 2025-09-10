# config/document_analysis_config.py
import re

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


# --- Accepted types ---
ACCEPTED_DOC_TYPES = {
    "invoice",
    "bank_statement",
    "paystub",
    "real_estate_contract",
    "real_estate_deed",       # נסח טאבו / deeds / ownership cert
    "loan_agreement",
    "appraisal",
    "account_confirmation",   # אישור ניהול חשבון (often required in Israel)
}

DOC_CLASSIFY_THRESHOLD = 3.2   # slightly stricter after adding bonuses/penalties

# --- Keywords (multilingual) ---
FINRE_KW = {
    # Bank statements
    "bank_statement": {
        "en": [
            "bank statement", "statement date", "statement period",
            "opening balance", "beginning balance", "closing balance",
            "account summary", "transactions", "deposits", "withdrawals",
            "account number", "routing", "iban", "available balance"
        ],
        "he": [
            "דוח חשבון", "דף חשבון", "יתרת פתיחה", "יתרת סגירה", "תקופת הדוח",
            "מספר חשבון", "IBAN", "אסמכתא", "תאריך ערך", "תאריך פעולה",
            "תנועות", "זכות", "חובה", "יתרה", "סיכום חשבון"
        ],
    },

    # Invoices / quotes
    "invoice": {
        "en": [
            "invoice", "tax invoice", "invoice number", "vat", "subtotal",
            "total due", "supplier", "customer", "quote", "pro forma"
        ],
        "he": [
            "חשבונית", "חשבונית מס", "מספר חשבונית", "מע\"מ",
            "סה\"כ לתשלום", "ספק", "לקוח", "הצעת מחיר"
        ],
    },

    # Real-estate deed / ownership
    "real_estate_deed": {
        "en": [
            "deed", "title deed", "property deed", "land registry",
            "parcel", "lot", "block", "ownership certificate", "cadastre"
        ],
        "he": [
            "נסח טאבו", "נסח מקרקעין", "לשכת רישום המקרקעין",
            "גוש", "חלקה", "תת חלקה", "שטר בעלות", "בעלות",
            "הערות", "מדינת ישראל", "מקרקעין"
        ],
    },

    # Real-estate contracts
    "real_estate_contract": {
        "en": [
            "purchase agreement", "sale agreement", "lease agreement",
            "property address", "seller", "buyer", "landlord", "tenant",
            "escrow", "closing date"
        ],
        "he": [
            "חוזה מכר", "הסכם מכר", "חוזה שכירות", "הסכם שכירות",
            "כתובת הנכס", "מוכר", "קונה", "משכיר", "שוכר", "נאמן", "פיקדון"
        ],
    },

    # Loan / mortgage
    "loan_agreement": {
        "en": [
            "loan agreement", "mortgage", "principal", "interest rate",
            "repayment", "collateral", "security", "lien"
        ],
        "he": [
            "הסכם הלוואה", "משכנתא", "קרן", "ריבית", "החזר",
            "בטוחה", "שיעבוד", "שעבוד", "ערבות"
        ],
    },

    # Appraisal / zero-report
    "appraisal": {
        "en": [
            "appraisal", "valuation", "market value", "appraiser", "comparables",
            "subject property", "as-is value", "cap rate"
        ],
        "he": [
            "שמאות", "דו\"ח שמאי", "הערכת שווי", "שווי שוק",
            "דוח אפס", "דוח אפס", "נכסים להשוואה", "נכס נשוא"
        ],
    },

    # Paystub
    "paystub": {
        "en": ["pay stub", "salary", "gross", "net pay", "earnings", "deductions"],
        "he": ["תלוש שכר", "ברוטו", "נטו", "ניכויים", "מעסיק", "עובד"],
    },

    # Account confirmation letter (אישור ניהול חשבון)
    "account_confirmation": {
        "en": [
            "account confirmation", "account ownership confirmation",
            "bank letter", "to whom it may concern", "this letter certifies"
        ],
        "he": [
            "אישור ניהול חשבון", "אישור בעלות על חשבון",
            "לאשר כי", "הרינו לאשר", "הבנק מאשר", "מספר חשבון"
        ],
    },
}

# --- Regex (precompiled) ---
import re
FINRE_REGEX = {
    # Common finance
    "currency_symbol": re.compile(r"(?:\$|€|₪|£|\bUSD\b|\bEUR\b|\bILS\b|\bNIS\b)"),
    "money_amount":    re.compile(r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})\b"),
    "dates":           re.compile(r"\b(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}[./-]\d{1,2}[./-]\d{1,2})\b"),
    "iban_any":        re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
    "iban_il":         re.compile(r"\bIL\d{2}\d{19}\b"),
    "acct_no":         re.compile(r"(?:account\s*(?:no\.?|number)?|מס(?:פר)?\s*חשבון)\s*[:#]?\s*[A-Z0-9\-]{3,}", re.I),

    # Bank-statement table cues (English + Hebrew)
    "table_headers_en": re.compile(r"\bDate\s+Description\s+(?:Debit|Credit|Amount)\b", re.I),
    "table_headers_he": re.compile(r"\bתאריך(?:\s+פעולה|\s+ערך)?\s+תיאור\s+(?:חובה|זכות|סכום|יתרה)\b"),
    "debit_credit_he":  re.compile(r"\b(?:חובה|זכות)\b"),

    # Invoice/quote table cues (to penalize bank_statement when these dominate)
    "invoice_headers_he": re.compile(r"\bתיאור\s+מק\"ט|\bתיאור\s+כמות|\bמחיר\s+ליחידה"),
    "invoice_headers_en": re.compile(r"\bItem\s+Code|\bUnit\s+Price|\bQuantity", re.I),
    "invoice_no":        re.compile(r"\b(?:invoice\s*(?:no\.?|number)?|חשבונית(?:\s*מס)?)\s*[:#]?\s*[A-Z0-9\-]{3,}\b", re.I),

    # Real-estate cues
    "israeli_tabu":     re.compile(r"\bלשכת רישום המקרקעין|\bנסח\s*(?:טאבו|מקרקעין)"),
    "parcel_block":     re.compile(r"\bגוש\s*\d+\s*חלקה\s*\d+(?:\s*תת\s*חלקה\s*\d+)?"),
    "lot_block_en":     re.compile(r"\b(?:Lot|Block)\s+\d+\b", re.I),

    # Mortgage / loan
    "mortgage":         re.compile(r"\bmortgage\b|\bמשכנת[אה]\b", re.I),
    "lien":             re.compile(r"\blien\b|\bשעבוד\b|\bשיעבוד\b", re.I),

    # Appraisal / zero report
    "appraisal_terms":  re.compile(r"\bappraisal|valuation|cap rate|comparables\b", re.I),
    "appraisal_he":     re.compile(r"\bשמאות|\bדו\"ח\s*שמאי|\bדוח\s*אפס|\bהערכת\s*שווי"),
}


FINRE_KW["account_confirmation"]["he"] += [
    "לבקשתך", "הננו לאשר", "הרינו לאשר", "לאשר כי",
    "סניף", "מספר חשבון", "בכבוד רב"
]
FINRE_KW["account_confirmation"]["en"] += [
    "to whom it may concern", "we hereby confirm", "this letter certifies",
    "branch", "account number", "sincerely"
]

# Common Israeli bank names (helps boosts & also avoids bank_statement drift)
BANK_NAMES_HE = [
    "הבנק הבינלאומי", "בנק לאומי", "בנק הפועלים", "בנק מזרחי", "דיסקונט",
    "אגוד", "מרכנתיל", "ירושלים", "הפועלים", "אוצר החייל"
]
BANK_NAMES_EN = [
    "First International Bank", "Leumi", "Hapoalim", "Mizrahi", "Discount",
    "Mercantile", "Bank of Jerusalem"
]

# Extra regex for letters vs. statements
FINRE_REGEX.update({
    "letter_openers_he": re.compile(r"(?:לבקשתך[, ]? הננו לאשר|הרינו לאשר|לאשר כי)"),
    "formal_closing_he": re.compile(r"(?:בכבוד רב)"),
    "bank_name_he":      re.compile("|".join(map(re.escape, BANK_NAMES_HE))),
    "bank_name_en":      re.compile("|".join(map(re.escape, BANK_NAMES_EN)), re.I),
    # Israeli account formats often shown as bank-branch-account (loosely match)
    "il_account_triplet": re.compile(r"\b\d{2}-\d{3}-\d{1,9}\b"),
    # URLs sometimes appear on headed paper
    "has_url":           re.compile(r"https?://[^\s]+", re.I),
})