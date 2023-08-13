import pandas as pd
import streamlit as st

from frontend.components.sidebar import sidebar
from frontend.utils.document_store import doc_to_store, load_embedder
from frontend.utils.llm import get_answer, load_llm
from frontend.utils.UI import is_valid

st.set_page_config(page_title="Resolution AI", page_icon="⚖️", layout="wide")
st.header("⚖️Resolution AI")
sidebar()

col1, col2, col3, col4 = st.columns([0.3, 0.3, 0.8, 1.0])
with col1:
    llm_name = st.selectbox(label="LLM", options=["OpenAI", "distilgpt2"], index=1)
    device = st.selectbox(label="device", options=["cpu", "cuda"], index=0)
    load_llm(llm_name, st.session_state.get("OPENAI_API_KEY"), device)
with col2:
    embedder_name = st.selectbox(label="Embedder", options=["OpenAI", "hkunlp/instructor-base"], index=1)
    load_embedder(embedder_name)


@st.cache_resource
def send_docs_to_store(uploaded_file):
    print(f"uploaded_file: {uploaded_file}")
    document_metadata = doc_to_store(uploaded_file)
    total_chunks = document_metadata["total_chunks"]
    total_pages = document_metadata["total_pages"]
    df = pd.DataFrame(
        {
            "include": [True],
            "document": [uploaded_file.name],
            "total_pages": [total_pages],
            "total_chunks": [total_chunks],
        }
    )

    st.session_state["df"] = pd.concat([df, st.session_state["df"]])


def clear_submit():
    st.session_state["submit"] = False
    # df = st.data_editor(st.session_state["df"])


with col4:
    uploaded_files = st.file_uploader(
        label="Upload a pdf, docx, or txt file",
        key="file_uploader",
        type=["pdf", "docx", "txt"],
        help="Scanned documents are not supported yet!",
        on_change=clear_submit,
        accept_multiple_files=True,
    )
    for uploaded_file in uploaded_files:
        send_docs_to_store(uploaded_file)


with col3:
    if "df" not in st.session_state:
        st.session_state["df"] = pd.DataFrame(columns=["include", "document", "total_pages", "total_chunks"])
    table = st.data_editor(st.session_state["df"], hide_index=True)


st.markdown("#### Query")
query = st.text_area("Ask a question about the document.", on_change=clear_submit, value="Who was Isaac?")

col1, col2, col3, col4 = st.columns([0.1, 0.12, 0.15, 1.0])

with col1:
    submit_button = st.button("Submit")
with col2:
    limit_sources_to_answer = st.number_input(
        label="Answer sources",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
        help="Number of sources (passages) that the Language model will have available to answer the question.",
    )

st.markdown("#### Answer")
if len(table):
    if submit_button or st.session_state.get("submit"):
        documents_selected = list(table[table["include"]]["document"])

        if is_valid(table, query, documents_selected):
            with st.spinner(text="In progress..."):
                print(f"{documents_selected=}")
                answer, selected_sources_scores_sorted = get_answer(query, documents_selected, limit_sources_to_answer)
            if answer:
                print(f"> {answer=}")
                print(f"> {selected_sources_scores_sorted=}")
                st.markdown(f"{llm_name} - {answer}")

                st.markdown("#### Sources")

                for source, score in selected_sources_scores_sorted:
                    col_anwer_1, col_anwer_2 = st.columns([0.3, 1.0])
                    # print(f"{source=}")
                    with col_anwer_1:
                        st.text(
                            f"document_name: {source['metadata']['document_name']}"
                            f"\npage: {source['metadata']['page']} / {source['metadata']['total_pages']}"
                            f"\nchunk: {source['metadata']['chunk']} / {source['metadata']['total_chunks']}"
                            f"\nsimilarity core: {100*score:.1f} %"
                        )
                    with col_anwer_2:
                        st.markdown(source["page_content"])
                    st.markdown("---")
            else:
                st.markdown(f"Couldn't get an answer for the query: {query}")

        else:
            st.stop()
else:
    st.error("Please upload at least one document")
