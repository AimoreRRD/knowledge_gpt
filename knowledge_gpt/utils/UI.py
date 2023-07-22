import streamlit as st


def is_valid(index, query):
    # if not st.session_state.get("OPENAI_API_KEY"):
        # st.error("Please configure your OpenAI API key!")
        # return False
    if len(index) == 0:
        st.error("Please upload a document!")
        return False
    if not query:
        st.error("Please enter a question!")
        return False
    return True
