
import fitz
import re
from typing import List


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    # YO WHATR dUHQOUQH DH SH OI ILY FITZ
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    doc.close()
    return "\n\n".join(pages)


def clean_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n ', '\n', text)
    return text.strip()


def chunk_into_segments(text: str, max_chars: int = 3000) -> List[str]:
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    current = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) > max_chars and current:
            chunks.append('\n\n'.join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para)

    if current:
        chunks.append('\n\n'.join(current))

    return [c for c in chunks if len(c) > 100]


def parse_pdf(pdf_bytes: bytes) -> List[str]:
    raw = extract_text_from_pdf(pdf_bytes)
    cleaned = clean_text(raw)
    return chunk_into_segments(cleaned)
