"""
PDF text extraction.

Thin wrapper around pypdf — the rest of the pipeline (chunking, embedding)
works on the plain string this returns.
"""

from pypdf import PdfReader

_MIN_TEXT_CHARS = 50


def extract_text_from_pdf(path: str) -> str:
    """Extract and concatenate text from every page of a PDF.

    Pages are joined with a blank line between them. Raises ValueError if the
    result is too short to be real text — this catches scanned/image-only
    PDFs that pypdf can't read.
    """
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(pages)

    if len(text.strip()) < _MIN_TEXT_CHARS:
        raise ValueError("PDF appears to have no extractable text")

    return text
