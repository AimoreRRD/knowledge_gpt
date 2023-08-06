import streamlit as st


def is_valid(edited_df, query, documents_selected) -> bool:
    # if not st.session_state.get("OPENAI_API_KEY"):
    # st.error("Please configure your OpenAI API key!")
    # return False
    if len(edited_df) == 0:
        st.error("Please upload a document!")
        return False
    if not query:
        st.error("Please enter a question!")
        return False
    if len(documents_selected) <= 0:
        st.error("Please select at least one document!")
        return False
    return True
