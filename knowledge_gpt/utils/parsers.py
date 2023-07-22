import re
from io import BytesIO
from typing import List

import docx2txt
import streamlit as st
from pypdf import PdfReader


@st.cache_data()
def parse_docx(file: BytesIO) -> str:
    text = docx2txt.process(file)
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


@st.cache_data()
def parse_pdf(file: BytesIO) -> List[str]:
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


@st.cache_data()
def parse_txt(file: BytesIO) -> str:
    text = file.read().decode("utf-8")
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text




@st.cache_data()
def parse_file(file: BytesIO) -> str | List[str]:
    """Parses a file and returns a list of Documents."""
    if file.name.endswith(".pdf"):
        return parse_pdf(file)
    elif file.name.endswith(".docx"):
        return parse_docx(file)
    elif file.name.endswith(".txt"):
        return parse_txt(file)
    else:
        raise ValueError("File type not supported!")
