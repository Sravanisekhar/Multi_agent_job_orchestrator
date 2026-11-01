import docx

def extract_text_from_docx(docx_path: str) -> str:
    """Extracts and returns plain text from a DOCX file."""
    doc = docx.Document(docx_path)
    text = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(text)