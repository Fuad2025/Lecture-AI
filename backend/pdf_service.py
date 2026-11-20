import fitz  # PyMuPDF


class PDFServiceError(Exception):
    """Raised with a short readable message when a PDF cannot be used."""
    pass


def extract_text_from_pdf(file_bytes):
    """Takes the raw bytes of a PDF and returns all its text as one string."""
    try:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception:
        raise PDFServiceError("This file is not a valid PDF.")

    if pdf.needs_pass:
        pdf.close()
        raise PDFServiceError("This PDF is password protected.")

    pages = []
    for page in pdf:
        pages.append(page.get_text())
    pdf.close()

    text = "\n".join(pages).strip()

    if not text:
        raise PDFServiceError(
            "No text could be extracted. The PDF may be a scanned image."
        )

    return text