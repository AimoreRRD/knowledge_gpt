import base64

import streamlit as st

st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("📖KnowledgeGPT")


def displayPDF(file):
    # Opening file from file path
    base64_pdf = base64.b64encode(file).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}"
    width="700" height="1000" type="application/pdf"></iframe>"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


uploaded_files = st.file_uploader(
    "Upload a pdf, docx, or txt file",
    type=["pdf", "docx", "txt"],
    help="Scanned documents are not supported yet!",
    accept_multiple_files=True,
)

displayPDF(uploaded_files[0].getbuffer())
