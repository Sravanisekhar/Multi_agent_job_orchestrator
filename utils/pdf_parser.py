import fitz # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts and returns plain text from a PDF file."""
    text = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text.append(page.get_text())
    return "\n".join(text)