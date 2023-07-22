import streamlit as st
import copy
import pandas as pd
from openai.error import OpenAIError

from knowledge_gpt.components.sidebar import sidebar
from knowledge_gpt.utils.expert import embed_docs, get_answer, get_sources
from knowledge_gpt.utils.parsers import parse_file
from knowledge_gpt.utils.chunk_doc import text_to_docs
from knowledge_gpt.utils.UI import is_valid


def clear_submit():
    st.session_state["submit"] = False


st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("📖KnowledgeGPT")

sidebar()

uploaded_files = st.file_uploader(
    "Upload a pdf, docx, or txt file",
    type=["pdf", "docx", "txt"],
    help="Scanned documents are not supported yet!",
    on_change=clear_submit,
    accept_multiple_files=True
)

# TODO: Save each session. 
indexes = dict()
text = None
documents_selected = []

api_flag = False # TODO: 

if uploaded_files is not None:
    dfs = pd.DataFrame([])

    for uploaded_file in uploaded_files:
        df = pd.DataFrame({"document": [uploaded_file.name], "include": [False]})
        dfs = pd.concat([dfs, df])

        text = parse_file(uploaded_file)
        document_name = uploaded_file.name.split('.')[0]
        doc = text_to_docs(text, document_name=document_name)
        try:
            with st.spinner("Indexing document... This may take a while⏳"):
                indexes[uploaded_file.name] = embed_docs(doc, api_flag)
        except OpenAIError as e:
            st.error(e._message)

    edited_df = st.data_editor(dfs, num_rows="dynamic", hide_index=True)
# print(indexes[uploaded_file.name])
# indexes[uploaded_file.name].merge_from(indexes[uploaded_file.name])
uploaded_files = None

# TODO: Save each session. 
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Query")
    query = st.text_area("Ask a question about the document", on_change=clear_submit)
    button = st.button("Submit")

    # if button or st.session_state.get("submit"):
    if button:
        documents_selected = list(edited_df[edited_df['include'] == True]['document'])
        if not is_valid(indexes, query) or len(documents_selected) == 0:
            st.stop()

        try:
            merged_index = None

            for doc in documents_selected: 
                index = indexes[doc]
                if not merged_index:
                    merged_index = index
                else:
                    merged_index.merge_from(index)

            sources = merged_index.similarity_search(query, k=3)

            with col2:
                st.markdown("#### Answer")
                answer = get_answer(sources, query)
                st.markdown(answer["output_text"].split("SOURCES: ")[0])

            with col3:
                st.markdown("#### Sources")
                sources = get_sources(answer, sources)
                for source in sources:
                    st.markdown(source.page_content)
                    st.markdown(source.metadata["source"])
                    st.markdown(source.metadata["document_name"])
                    st.markdown("---")

        except OpenAIError as e:
            st.error(e._message)