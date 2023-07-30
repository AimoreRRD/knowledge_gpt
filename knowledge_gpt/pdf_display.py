import streamlit as st
import pandas as pd
import base64
from knowledge_gpt.components.sidebar import sidebar
from knowledge_gpt.utils.expert import embed_docs, get_answer, load_embeddings, load_model
from knowledge_gpt.utils.parsers import parse_file
from knowledge_gpt.utils.chunk_doc import text_to_docs
from knowledge_gpt.utils.UI import is_valid

from typing import List


st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("📖KnowledgeGPT")


def displayPDF(file):
    # Opening file from file path
    base64_pdf = base64.b64encode(file).decode('utf-8')
    
    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Upload a pdf, docx, or txt file",
    type=["pdf", "docx", "txt"],
    help="Scanned documents are not supported yet!",    
    accept_multiple_files=True
)

displayPDF(uploaded_files[0].getbuffer())