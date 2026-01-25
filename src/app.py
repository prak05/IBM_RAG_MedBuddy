import streamlit as st
import os
from rag_engine import initialize_settings, process_and_index_docs

st.set_page_config(page_title="MedBuddy RAG", page_icon="🩺", layout="wide")
st.title("🩺 MedBuddy: Medical RAG Chatbot")

# Load Secrets
try:
    creds = st.secrets["ibm"]
    initialize_settings(creds["WATSONX_API_KEY"], creds["WATSONX_PROJECT_ID"], creds["WATSONX_URL"])
except Exception as e:
    st.error(f"Credential Error: {e}")
    st.stop()

# Sidebar Data Ingestion
with st.sidebar:
    st.header("📂 Data Ingestion")
    uploaded_file = st.file_uploader("Upload Medical PDF", type=['pdf'])
    if st.button("Process & Index") and uploaded_file:
        os.makedirs("data", exist_ok=True)
        with open(os.path.join("data", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.query_engine = process_and_index_docs("data")
        st.success("Indexing Complete!")

# Chat Interface
if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Ask a clinical question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    if "query_engine" in st.session_state:
        with st.chat_message("assistant"):
            response = st.session_state.query_engine.query(prompt)
            st.markdown(str(response))
            st.session_state.messages.append({"role": "assistant", "content": str(response)})
    else:
        st.warning("Upload a textbook first!")
