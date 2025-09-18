import json
import logging
import streamlit as st
import ollama

from extractors.pdf_extraction import extract_from_pdf
from extractors.excel_extraction import extract_from_excel
from langchain.schema import Document
from processing.qa_pipeline import create_vector_db, process_question_with_rag

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Financial Assistant RAG", page_icon="💰", layout="wide")

@st.cache_data(show_spinner=False)
def get_ollama_models():
    try:
        return [m["model"] for m in ollama.list().get("models", [])]
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return []

@st.cache_resource(show_spinner=True)
def cached_create_vector_db(docs_json, file_hash):
    docs = [Document(**d) for d in json.loads(docs_json)]
    logger.info(f"Creating vector DB with {len(docs)} documents")
    return create_vector_db(docs)

def main():
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("vector_db", None)
    st.session_state.setdefault("last_uploaded_filename", None)
    st.session_state.setdefault("processing_complete", False)
    st.session_state.setdefault("file_hash", None)

    st.sidebar.header("⚙️ Settings")
    
    models = get_ollama_models()
    selected_model = st.sidebar.selectbox("Local Ollama model", models, index=0) if models else None
    if not models:
        st.sidebar.warning("No local Ollama models detected.")

    if st.sidebar.button("🗑 Clear Vector DB"):
        try:
            cached_create_vector_db.clear()
            if st.session_state.get("vector_db"):
                try:
                    collection_name = st.session_state["vector_db"]._collection.name
                    st.session_state["vector_db"]._client.delete_collection(name=collection_name)
                    logger.info(f"Deleted collection: {collection_name}")
                except Exception as e:
                    logger.warning(f"Could not delete collection: {e}")
            
            st.session_state["vector_db"] = None
            st.session_state["messages"] = []
            st.session_state["last_uploaded_filename"] = None
            st.session_state["processing_complete"] = False
            st.session_state["file_hash"] = None
            
            st.sidebar.success("✅ Vector DB cleared successfully!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"❌ Clear failed: {e}")

    st.subheader("📊 Financial Assistant RAG", divider="gray")

    file = st.file_uploader(
        "Upload financial document",
        type=["pdf", "xlsx", "xls", "csv", "txt"],
        accept_multiple_files=False,
        key="file_uploader"
    )

    if file:
        file_hash = str(hash(file.read()))
        file.seek(0)
        
        if (st.session_state["last_uploaded_filename"] != file.name or 
            st.session_state["file_hash"] != file_hash):
            st.session_state["last_uploaded_filename"] = file.name
            st.session_state["file_hash"] = file_hash
            st.session_state["vector_db"] = None
            st.session_state["messages"] = []
            st.session_state["processing_complete"] = False
            
            cached_create_vector_db.clear()
            st.info(f"📁 New file detected: **{file.name}** ({file.size:,} bytes)")

        if not st.session_state["processing_complete"]:
            if st.button("🚀 Process Document", type="primary"):
                with st.spinner("🔎 Indexing document…"):
                    try:
                        ext = file.name.lower().split(".")[-1]
                        if ext == "pdf":
                            docs = extract_from_pdf(file)
                        elif ext in ["xlsx", "xls", "csv"]:
                            docs = extract_from_excel(file)
                        elif ext == "txt":
                            txt = file.read().decode("utf-8", errors="ignore")
                            docs = [Document(txt, metadata={"source": file.name, "type": "text"})]
                        else:
                            txt = file.read().decode("utf-8", errors="ignore")
                            docs = [Document(txt, metadata={"source": file.name, "type": "unknown"})]

                        if not docs:
                            st.error("No data extracted from the file!")
                            return

                        try:
                            docs_json = json.dumps([d.model_dump() for d in docs])
                        except AttributeError:
                            docs_json = json.dumps([d.dict() for d in docs])
                        
                        st.session_state["vector_db"] = cached_create_vector_db(docs_json, file_hash)
                        st.session_state["processing_complete"] = True
                        
                        st.success(f"✅ Successfully indexed {len(docs)} document chunks!")
                        
                        with st.expander("📊 Extraction Summary"):
                            st.write(f"**Total documents extracted:** {len(docs)}")
                            doc_types = {}
                            for doc in docs:
                                doc_type = doc.metadata.get('type', 'text')
                                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                            for doc_type, count in doc_types.items():
                                st.write(f"- {doc_type.title()}: {count}")
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Processing failed: {e}")
                        logger.error(f"Document processing error: {e}")
        else:
            st.success(f"✅ Document **{file.name}** is ready for chat!")

    else:
        if st.session_state["last_uploaded_filename"] is not None:
            st.session_state["last_uploaded_filename"] = None
            st.session_state["vector_db"] = None
            st.session_state["messages"] = []
            st.session_state["processing_complete"] = False
            st.session_state["file_hash"] = None
        
        st.info("👆 Please upload a document to get started")

    if st.session_state.get("vector_db"):
        st.divider()
        
        chat_box = st.container(height=450, border=True)

        for msg in st.session_state["messages"]:
            avatar = "🤖" if msg["role"] == "assistant" else "😎"
            with chat_box.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        user_q = st.chat_input("Ask your financial question…")
        if user_q:
            st.session_state["messages"].append({"role": "user", "content": user_q})
            chat_box.chat_message("user", avatar="😎").markdown(user_q)

            with chat_box.chat_message("assistant", avatar="🤖"):
                with st.spinner("💡 Thinking…"):
                    if not st.session_state["vector_db"]:
                        st.warning("Upload and process a file first.")
                        answer = None
                    elif not selected_model:
                        st.warning("Select an Ollama model.")
                        answer = None
                    else:
                        try:
                            answer = process_question_with_rag(
                                user_q, st.session_state["vector_db"], selected_model
                            )
                            st.markdown(answer or "No answer returned.")
                        except Exception as e:
                            st.error(f"Error generating answer: {e}")
                            answer = None

            if answer:
                st.session_state["messages"].append(
                    {"role": "assistant", "content": answer}
                )
    else:
        st.info("🤖 Upload and process a document to start chatting!")

if __name__ == "__main__":
    main()
