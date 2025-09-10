import os
import platform
import subprocess
from pdf2image import convert_from_path

# --- Detect platform ---
IS_WINDOWS = platform.system() == "Windows"

# --- Paths for Windows ---
WINDOWS_SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
WINDOWS_POPPLER_PATH = r"C:\poppler-25.07.0-0\Library\bin"   # <-- adjust to your install


def convert_to_pdf(input_path: str, output_dir: str) -> str:
    """
    Convert Office docs (docx, xlsx, pptx, etc.) to PDF using LibreOffice.
    Works on both Windows and Linux.
    """
    soffice_cmd = WINDOWS_SOFFICE_PATH if IS_WINDOWS else "soffice"

    subprocess.run([
        soffice_cmd, "--headless", "--convert-to", "pdf", "--outdir", output_dir, input_path
    ], check=True)

    filename = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    return os.path.join(output_dir, filename)


def pdf_to_images(pdf_path: str, max_pages: int = 3):
    """
    Convert first N pages of a PDF into images.
    Works on both Windows and Linux.
    """
    if IS_WINDOWS:
        return convert_from_path(
            pdf_path,
            dpi=200,
            first_page=1,
            last_page=max_pages,
            poppler_path=WINDOWS_POPPLER_PATH  # Windows needs explicit path
        )
    else:
        return convert_from_path(
            pdf_path,
            dpi=200,
            first_page=1,
            last_page=max_pages
            # Linux: poppler-utils from apt-get makes it available globally
        )
