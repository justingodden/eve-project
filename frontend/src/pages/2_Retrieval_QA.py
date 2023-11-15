import os

import streamlit as st
from langserve import RemoteRunnable

URL = os.environ["BACKEND_SERVICE_URL"]

remote_qa = RemoteRunnable(f"http://{URL}/qa/")

st.set_page_config(page_title="Retrieval QA", page_icon="🦜️")

st.title("🦜️ Retrieval QA")
st.write("Use this application to ask questions about the LangChain Python library.")

query = st.chat_input("Ask your question here.")

if query:
    with st.chat_message("user"):
        st.write(query)

    resp = remote_qa.invoke({"query": query}).get("result")
    with st.chat_message("assistant"):
        st.write(resp)
