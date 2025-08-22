import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(
    page_title="Financial Document Extractor",
    page_icon="💸",
    layout="wide"
)

if 'upload_result' not in st.session_state:
    st.session_state.upload_result = None
if 'pdf_id' not in st.session_state:
    st.session_state.pdf_id = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

UPLOAD_URL = "http://localhost:8001/api/upload"
ASK_PDF_URL = "http://localhost:8001/api/ask_pdf"

st.title("Financial Document Entity Extractor 💸")
st.markdown("Upload a financial document to automatically extract key entities. For PDFs, you can also ask follow-up questions.")

uploaded_file = st.file_uploader(
    "Upload a file (.txt, .pdf, .docx)",
    type=["txt", "pdf", "docx"],
    help="Upload your document here to begin extraction."
)

if uploaded_file:
    if st.button(f"Analyze {uploaded_file.name}", type="primary"):
        st.session_state.upload_result = None
        st.session_state.pdf_id = None
        st.session_state.error_message = None

        with st.spinner("Analyzing document... Please wait."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                response = requests.post(UPLOAD_URL, files=files, timeout=60)

                if response.status_code == 200:
                    st.session_state.upload_result = response.json()
                    if st.session_state.upload_result.get("file_type") == "pdf":
                        st.session_state.pdf_id = st.session_state.upload_result.get("pdf_id")
                else:
                    st.session_state.error_message = f"Error from backend: {response.status_code} - {response.text}"

            except requests.exceptions.RequestException as e:
                st.session_state.error_message = f"Connection Error: Could not connect to the backend at {UPLOAD_URL}. Please ensure the backend is running. Details: {e}"

if st.session_state.error_message:
    st.error(st.session_state.error_message)

if st.session_state.upload_result:
    result_data = st.session_state.upload_result
    entities = result_data.get("entities")

    if entities and isinstance(entities, dict):
        st.divider()
        st.subheader("📊 Extracted Information")

        col1, col2 = st.columns([2, 1])

        with col2:
            st.info(f"**Document Type:** `{result_data.get('document_type', 'N/A')}`")
            st.metric(label="Confidence Score", value=f"{result_data.get('confidence_score', 0.0):.0%}")

        with col1:
            def format_value(value):
                if isinstance(value, dict) or isinstance(value, list):
                    return f"```json\n{json.dumps(value, indent=2)}\n```"
                return value

            df_data = [(key, format_value(value)) for key, value in entities.items()]
            df = pd.DataFrame(df_data, columns=["Entity Type", "Extracted Value"])

            st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("Show Raw API Output"):
        st.json(result_data)

if st.session_state.pdf_id:
    st.divider()
    st.subheader("💬 Ask a Question about the PDF")

    question = st.text_input(
        "Enter your question here:",
        placeholder="e.g., What is the total amount due?",
        key="qa_question"
    )

    if st.button("Ask", key="qa_button"):
        if question:
            with st.spinner("Searching for the answer..."):
                try:
                    qa_params = {"pdf_id": st.session_state.pdf_id, "question": question}
                    qa_response = requests.post(ASK_PDF_URL, params=qa_params, timeout=60)

                    if qa_response.status_code == 200:
                        st.info(f"❓ Your Question: {question}")
                        answer = qa_response.json().get("answer", "No answer found.")
                        st.success(f"💡 Answer: {answer}")

                        with st.expander("Show Full Q&A Response (JSON)"):
                            st.json(qa_response.json())
                    else:
                        st.error(f"Error from Q&A backend: {qa_response.status_code} - {qa_response.text}")

                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: Could not reach the Q&A backend. Details: {e}")
        else:
            st.warning("Please enter a question before clicking 'Ask'.")
