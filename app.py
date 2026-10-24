
import streamlit as st
import tempfile
from pathlib import Path

from rag_pipeline import (
    load_and_split_pdf,
    create_vector_store,
    answer_question,
    summarize_document,
)

st.set_page_config(
    page_title="PaperPilot AI",
    page_icon="📚",
    layout="wide",
)

# ---------- Session state ----------
defaults = {
    "vector_store": None,
    "messages": [],
    "pdf_name": None,
    "chunks": [],
    "summary": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- Sidebar ----------
with st.sidebar:
    st.title("📚 PaperPilot AI")
    st.caption("Your AI-powered PDF study assistant")

    st.divider()
    st.subheader("Upload Study Material")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        help=(
            "Upload books, textbooks, research papers, "
            "newspapers, notes, or other study material."
        ),
    )

    if uploaded_file is not None:
        st.caption(f"Selected: {uploaded_file.name}")

        if st.button(
            "⚙️ Process PDF",
            type="primary",
            use_container_width=True,
        ):
            temp_pdf_path = None

            try:
                with st.spinner(
                    "Processing your PDF... Please wait."
                ):
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf",
                    ) as temp_file:
                        temp_file.write(
                            uploaded_file.getvalue()
                        )
                        temp_pdf_path = temp_file.name

                    try:
                        chunks = load_and_split_pdf(
                            temp_pdf_path
                        )
                        new_vector_store = create_vector_store(
                            chunks
                        )
                    finally:
                        Path(temp_pdf_path).unlink(
                            missing_ok=True
                        )

                # Update the active document only after success
                st.session_state.vector_store = (
                    new_vector_store
                )
                st.session_state.chunks = chunks
                st.session_state.summary = None
                st.session_state.pdf_name = (
                    uploaded_file.name
                )
                st.session_state.messages = []

                st.success("PDF processed successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"PDF processing failed: {e}")

    st.divider()

    if st.session_state.vector_store is not None:
        st.subheader("Current Document")
        st.write(f"📄 {st.session_state.pdf_name}")
        st.success("Ready to study!")
        
        if st.button(
            "📝 Generate Summary",
            type="primary",
            use_container_width=True,
        ):
            
            try:
                progress_bar = st.progress(0)
                progress_status = st.empty()

                def update_summary_progress(message, fraction):
                    progress_bar.progress(
                        min(fraction, 1.0)
                    )
                    progress_status.caption(message)

                summary = summarize_document(
                    st.session_state.chunks,
                    progress_callback=update_summary_progress,
                )

                st.session_state.summary = summary
                st.rerun()

            except Exception as e:
                st.error(f"Summary generation failed: {e}")



        if st.button(
            "🧹 Clear Chat",
            use_container_width=True,
        ):
            st.session_state.messages = []
            st.rerun()

        if st.button(
            "🗑️ Remove Document",
            use_container_width=True,
        ):
            st.session_state.vector_store = None
            st.session_state.pdf_name = None
            st.session_state.messages = []
            st.session_state.chunks = []
            st.session_state.summary = None
            st.rerun()


# ---------- Main page ----------
st.title("📖 Your PDF Study Assistant")

st.write(
    "Learn from your PDFs with AI. Upload books, "
    "textbooks, research papers, newspapers, notes, "
    "or other educational reading material."
)

if st.session_state.vector_store is None:
    st.info(
        "👈 Upload a PDF from the sidebar and click "
        "**Process PDF** to get started."
    )

    st.markdown(
        """
        ### What you can do

        - 💬 Ask questions about your study material
        - 🧠 Understand difficult concepts and topics
        - ✨ Summarize Document
        - 📚 Get answers based on your PDF's content
        - 🔎 Check source pages to verify answers
        """
    )

else:
    st.caption(
        f"Active document: {st.session_state.pdf_name}"
    )
    
    
    if st.session_state.summary:
        st.subheader("📝 Document Summary")

        st.markdown(st.session_state.summary)

        with st.expander("📖 Summary source pages"):
            pages = sorted({
                doc.metadata.get("page", 0) + 1
                for doc in st.session_state.chunks
            })

            st.write(f"Document: {st.session_state.pdf_name}")
            st.write(
                "Pages included: "
                + ", ".join(str(page) for page in pages)
            )

        st.divider()


    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("📖 View Sources"):
                    for source in message["sources"]:
                        st.write(
                            f"**{source['file']}** — "
                            f"Page {source['page']}"
                        )

    # Question input
    question = st.chat_input(
        "Ask anything about your PDF..."
    )

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner(
                "Finding relevant information in your PDF..."
            ):
                try:
                    result = answer_question(
                        st.session_state.vector_store,
                        question,
                    )

                    answer = result["answer"]
                    sources = result["sources"]

                    # Display the original uploaded filename
                    for source in sources:
                        source["file"] = (
                            st.session_state.pdf_name
                        )

                    st.markdown(answer)

                    if sources:
                        with st.expander("📖 View Sources"):
                            for source in sources:
                                st.write(
                                    f"**{source['file']}** — "
                                    f"Page {source['page']}"
                                )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })

                except Exception as e:
                    st.error(
                        f"Could not generate answer: {e}"
                    )
