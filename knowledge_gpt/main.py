import streamlit as st
import copy
import pandas as pd
from openai.error import OpenAIError

from knowledge_gpt.components.sidebar import sidebar
from knowledge_gpt.utils.expert import embed_docs, get_answer, load_embeddings, load_model
from knowledge_gpt.utils.parsers import parse_file
from knowledge_gpt.utils.chunk_doc import text_to_docs
from knowledge_gpt.utils.UI import is_valid

from typing import List

api_flag = False


documents_selected = []

def clear_submit():
    st.session_state["submit"] = False


st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("📖KnowledgeGPT")

indexes = dict()

embeddings = load_embeddings()

edited_df = pd.DataFrame([], columns=['document'])

uploaded_files = st.file_uploader(
    "Upload a pdf, docx, or txt file",
    type=["pdf", "docx", "txt"],
    help="Scanned documents are not supported yet!",
    on_change=clear_submit,
    accept_multiple_files=True
)

@st.cache_resource
def index_doc(uploaded_files):
    print("index_doc")
    dfs = pd.DataFrame([])
    for uploaded_file in uploaded_files:
        df = pd.DataFrame({"document": [uploaded_file.name], "include": [False]})
        dfs = pd.concat([dfs, df])

        text = parse_file(uploaded_file)
        document_name = uploaded_file.name.split('.')[0]
        doc_chunks = text_to_docs(text, document_name=document_name)
        indexes[uploaded_file.name] = embed_docs(doc_chunks, embeddings)
    return dfs, indexes

import base64
@st.cache_data
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

show_pdf()

def set_df(dfs):
    edited_df = st.data_editor(dfs, hide_index=True)
    return edited_df

print(f"{uploaded_files=}")

if uploaded_files is not None:
    dfs, indexes = index_doc(uploaded_files)
    edited_df = set_df(dfs)

def get_selected_sources_with_scores(query, documents_selected, k) -> List:
    sources_scores_list = []
    for doc in documents_selected: 
        index = indexes.get(doc)
        sources_scores = index.similarity_search_with_score(query, k=k)        
        sources_scores_list.extend(sources_scores)

    sources_scores_sorted = sorted(sources_scores_list, key=lambda x: x[1], reverse=True)
    
    return sources_scores_sorted[:k]

st.markdown("#### Query")
query = st.text_area("Ask a question about the document.", on_change=clear_submit)
button = st.button("Submit")
st.markdown("#### Answer")

#? Continue only if there are documents selected and there is a question.
if (button or st.session_state.get("submit")) and len(edited_df):

    documents_selected = list(edited_df[edited_df['include'] == True]['document'])

    if is_valid(indexes, query, documents_selected):
        model = load_model()

        selected_sources_scores_sorted = get_selected_sources_with_scores(query, documents_selected, k=3)
        selected_sources_sorted = [x[0] for x in selected_sources_scores_sorted]
        answer = get_answer(selected_sources_sorted, query, model)        

        st.markdown(answer["output_text"])
        st.markdown("#### Sources")

        for source, score in selected_sources_scores_sorted:
            st.text(f"document_name: {source.metadata['document_name']}" \
                    f"\npage: {source.metadata['page']} / {source.metadata['total_pages']}"  \
                    f"\nchunk: {source.metadata['chunk']} / {source.metadata['total_chunks']}" \
                    f"\nssimilarity core: {100*score:.1f} %"
                    )
            st.markdown(source.page_content)
            st.markdown("---")
    else:
        st.stop()