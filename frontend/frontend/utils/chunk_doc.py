from typing import List

import streamlit as st
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


@st.cache_data(show_spinner="text_to_docs...⏳")
def text_to_docs(text: str | List[str], document_name=None) -> List[Document]:
    chunk_size = 500
    """Converts a string or list of strings to a list of Documents with metadata."""
    if isinstance(text, str):
        # Take a single string as one page
        text = [text]
    page_docs = [Document(page_content=page) for page in text]

    # Add page numbers as metadata
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    # Split pages into chunks
    doc_chunks = []
    for doc in page_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            chunk_overlap=0,
        )
        chunks = text_splitter.split_text(doc.page_content)

        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "document_name": document_name,
                    "page": doc.metadata["page"],
                    "chunk": i,
                    "total_pages": len(text),
                    "total_chunks": len(chunks),
                },
            )
            # Add sources a metadata
            doc.metadata["source"] = f"{doc.metadata['document_name']}-{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc_chunks.append(doc)
    return doc_chunks
