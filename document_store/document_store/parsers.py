import re
from typing import List

import docx2txt
from pypdf import PdfReader


def parse_docx(file: bytes) -> str:
    text = docx2txt.process(file)
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


def parse_pdf(file: bytes) -> List[str]:
    pdf = PdfReader(file)
    output = []
    for page in pdf.pages:
        text = page.extract_text()
        # Merge hyphenated words
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        # Fix newlines in the middle of sentences
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
        # Remove multiple newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)

        output.append(text)

    return output


def parse_txt(file: bytes) -> str:
    text = file.read().decode("utf-8")
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


def parse_file(file: bytes, file_name) -> str | List[str]:
    """Parses a file and returns a list of Documents."""
    if file_name.endswith(".pdf"):
        return parse_pdf(file)
    elif file_name.endswith(".docx"):
        return parse_docx(file)
    elif file_name.endswith(".txt"):
        return parse_txt(file)
    else:
        raise ValueError("File type not supported!")
