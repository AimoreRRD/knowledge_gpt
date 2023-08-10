import pandas as pd
import streamlit as st

from frontend.components.sidebar import sidebar
from frontend.utils.document_store import doc_to_store, load_embedder
from frontend.utils.llm import get_answer, load_llm
from frontend.utils.UI import is_valid

st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("📖KnowledgeGPT")
sidebar()

col1, col2, col3 = st.columns([0.3, 0.3, 1.0])
with col1:
    llm_name = st.selectbox(label="LLM", options=["OpenAI", "distilgpt2"], index=0)
    load_llm(llm_name, st.session_state.get("OPENAI_API_KEY"))
with col2:
    embedder_name = st.selectbox(label="Embedder", options=["OpenAI", "hkunlp/instructor-base"], index=1)
    load_embedder(embedder_name)


def clear_submit():
    st.session_state["submit"] = False


@st.cache_resource
def send_docs_to_store(uploaded_files):
    dfs = pd.DataFrame([])
    for uploaded_file in uploaded_files:
        print(f"uploaded_file: {uploaded_file}")
        df = pd.DataFrame({"document": [uploaded_file.name], "include": [True]})
        dfs = pd.concat([df, dfs])
        doc_to_store(uploaded_file)
        # text = parse_file(uploaded_file)
        # document_name = uploaded_file.name.split(".")[0]
        # doc_chunks = text_to_docs(text, document_name=document_name)
        # indexes[uploaded_file.name] = doc_to_store(doc_chunks)

    return dfs


def set_df(dfs):
    edited_df = st.data_editor(dfs, hide_index=True)
    return edited_df


# def get_selected_sources_with_scores(query="", documents_selected=[], k: int = 1) -> List:
#     sources_scores_list = []
#     for doc in documents_selected:
#         index = indexes.get(doc, dict())
#         sources_scores = index.similarity_search_with_score(query, k=k)
#         sources_scores = [(sources_score[0], 1 - sources_score[1]) for sources_score in sources_scores]
#         sources_scores_list.extend(sources_scores)

#     sources_scores_sorted = sorted(sources_scores_list, key=lambda x: x[1], reverse=True)

#     return sources_scores_sorted

edited_df = pd.DataFrame([], columns=["document"])

uploaded_files = st.file_uploader(
    "Upload a pdf, docx, or txt file",
    type=["pdf", "docx", "txt"],
    help="Scanned documents are not supported yet!",
    on_change=clear_submit,
    accept_multiple_files=True,
)

if len(uploaded_files) > 0:
    dfs = send_docs_to_store(uploaded_files)
    edited_df = set_df(dfs)


st.markdown("#### Query")
query = st.text_area("Ask a question about the document.", on_change=clear_submit, value="Who was Isaac?")

col1, col2, col3, col4 = st.columns([0.1, 0.12, 0.15, 1.0])

with col1:
    submit_button = st.button("Submit")
# with col2:
#     limit_sources_to_answer = st.number_input(
#         label="Answer sources",
#         min_value=1,
#         max_value=10,
#         value=3,
#         step=1,
#         help="Number of sources (passages) that the Language model will have available to answer the question.",
#     )
# with col3:
#     limit_sources_to_search = st.number_input(
#         label="Document sources",
#         min_value=1,
#         max_value=10,
#         value=3,
#         step=1,
#         help="Number of sources (passages) that the Embedder will retrieve per document.",
#     )

st.markdown("#### Answer")
if (submit_button or st.session_state.get("submit")) and len(edited_df):
    documents_selected = list(edited_df[edited_df["include"]]["document"])

    if is_valid(edited_df, query, documents_selected):
        with st.spinner(text="In progress..."):
            print(f"{documents_selected=}")
            answer, selected_sources_scores_sorted = get_answer(query, documents_selected)

        print(f"{answer=}")
        print(f"{selected_sources_scores_sorted=}")

        st.markdown(answer)
        st.markdown("#### Sources")

        for source, score in selected_sources_scores_sorted:
            print(f"{source=}")
            st.text(
                f"document_name: {source['metadata']['document_name']}"
                f"\npage: {source['metadata']['page']} / {source['metadata']['total_pages']}"
                f"\nchunk: {source['metadata']['chunk']} / {source['metadata']['total_chunks']}"
                f"\nsimilarity core: {100*score:.1f} %"
            )
            st.markdown(source['page_content'])
            st.markdown("---")
    else:
        st.stop()
