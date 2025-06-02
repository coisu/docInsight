import streamlit as st
import requests
import time
import logging

st.set_page_config(page_title="docInsight", layout="wide")
st.title("📚 docInsight")

backend_url = "http://backend:8000"

for _ in range(10):
    try:
        r = requests.get(f"{backend_url}/health")
        if r.status_code == 200:
            break
    except requests.exceptions.ConnectionError:
        time.sleep(1)
else:
    st.error("❌ Cannot connect to the backend API. Please make sure it is running.")
    st.stop()

if "files" not in st.session_state:
    st.session_state.files = []

# File uploader
st.subheader("1️⃣ Upload your PDF files")
uploaded_files = st.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("Uploading and processing files..."):
        files = [("files", (f.name, f, "application/pdf")) for f in uploaded_files]
        response = requests.post(f"{backend_url}/upload/", files=files)
        if response.status_code == 200:
            new_files = [f["filename"] for f in response.json()["uploaded_files_info"]]
            st.session_state["files"].extend(f for f in new_files if f not in st.session_state["files"])
            st.success(f"Uploaded and indexed: {', '.join(new_files)}")
        else:
            st.error(f"Upload failed: {response.text}")

# uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], accept_multiple_files=False)

# if uploaded_file:
#     with st.spinner("Uploading and processing file..."):
#         files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
#         response = requests.post(f"{backend_url}/upload/", files=files)
#         if response.status_code == 200:
#             st.success(f"Uploaded and indexed: {response.json()['filename']}")
#         else:
#             st.error(f"Upload failed: {response.text}")



st.subheader("2️⃣ Select documents to search")
selected_files = st.multiselect("✅ Choose documents", st.session_state["files"], default=st.session_state["files"])

if st.button("Clear all data"):
    response = requests.post(f"{backend_url}/clear/")
    if response.status_code == 200:
        st.session_state["files"] = []
        st.success("Cleared all data successfully!")
    else:
        st.error(f"Failed to clear data: {response.text}")


# Query interface
st.subheader("2️⃣ Ask a question about your selected documents")
query = st.text_input("Type your question here")

if query and selected_files:
    with st.spinner("Searching and generating answer..."):
        # res = requests.post(f"{backend_url}/query/", data={"query": query}, files={"files": selected_files})
        data = [("query", query)] + [("files", f) for f in selected_files]
        response = requests.post(f"{backend_url}/query/", data=data)
        if response.status_code == 200:
            result = response.json()
            query_type = result.get("query_type", "normal")
            st.markdown("### ✅ Answer")
            st.write(result["answer"])
            st.text(f">> Query type: {query_type}")
            # print(f"\n\n>>  Query type: {query_type}\n\n")
            st.markdown("### 📄 Sources")
            for i, src in enumerate(result["sources"], 1):
                st.markdown(f"**{i}. {src['filename']}**")
                if query_type == "summary":
                    st.markdown("#### Summary")
                    st.code(src["chunk"], language="markdown")
                    
                    if "original_chunks" in src:
                        with st.expander("Show original source from documents"):
                            for j, chunk in enumerate(src["original_chunks"], 1):
                                st.markdown(f"**{j}.**")
                                st.code(chunk, language="markdown")

                elif query_type == "comparison":
                    if "chunk" in src:
                        st.markdown("#### Comparison")
                        st.code(src["chunk"], language="markdown")
                    if "original_chunks" in src:
                        with st.expander("Show original source from documents"):
                            for j, chunk in enumerate(src["original_chunks"], 1):
                                st.markdown(f"**{j}.**")
                                st.code(chunk, language="markdown")
                
                else:
                    if "chunk" in src:
                        st.markdown("#### Context")
                        st.code(src["chunk"], language="markdown")

        else:
            st.error(f"Error: {response.text}")
else:
    st.warning("Type a question and select documents to search.")