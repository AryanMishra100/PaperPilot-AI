
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


# Local model configuration
LLM_MODEL = "qwen2.5:1.5b"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_and_split_pdf(pdf_path: str):
    """Load a PDF and split its text into smaller chunks."""

    if not Path(pdf_path).is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
    )

    chunks = splitter.split_documents(pages)

    if not chunks:
        raise ValueError("No readable text found in this PDF.")

    print(f"Pages loaded: {len(pages)}")
    print(f"Chunks created: {len(chunks)}")

    return chunks


def create_vector_store(chunks):
    """Convert document chunks into embeddings and store them in FAISS."""

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    print("FAISS vector store created successfully.")
    return vector_store


def answer_question(vector_store, question: str):
    """Answer a question using relevant PDF content."""

    retrieved_docs = vector_store.similarity_search(
        question,
        k=4,
    )

    context_parts = []
    sources = []

    for doc in retrieved_docs:
        page_number = doc.metadata.get("page", 0) + 1
        filename = Path(
            doc.metadata.get("source", "Unknown PDF")
        ).name

        context_parts.append(
            f"[Source: {filename}, Page: {page_number}]\n"
            f"{doc.page_content}"
        )

        sources.append(
            {
                "file": filename,
                "page": page_number,
            }
        )

    context = "\n\n".join(context_parts)

    prompt = ChatPromptTemplate.from_template(
        """
You are PaperPilot AI, a helpful assistant that helps students
understand and study PDF documents.

The document may be a textbook, book, research paper, newspaper,
class notes, study material, or another type of document.

Answer the user's question using only the provided context.

Instructions:
- Give a clear, relevant answer in student-friendly language.
- Use only information supported by the provided context.
- If the answer is not available in the context, clearly say that
  the information was not found in the provided document.
- Do not invent facts or unsupported citations.
- Refer to the document as a document or PDF, not automatically
  as a research paper.
- Include relevant page references when useful.

Document context:
{context}

User's question:
{question}

Answer:
"""
    )

    llm = ChatOllama(
        model=LLM_MODEL,
        temperature=0,
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    return {
        "answer": response.content,
        "sources": sources,
    }





def summarize_document(chunks, progress_callback=None):
    """Generate a structured, student-friendly PDF summary."""

    if not chunks:
        raise ValueError(
            "No document text is available to summarize."
        )

    llm = ChatOllama(
        model=LLM_MODEL,
        temperature=0,
        num_predict=450,
    )

    batch_size = 12
    reduce_group_size = 8

    total_chunks = len(chunks)
    partial_summaries = []

    initial_batches = (
        total_chunks + batch_size - 1
    ) // batch_size

    # Calculate the number of LLM calls.
    total_calls = initial_batches
    remaining = initial_batches

    while remaining > 4:
        remaining = (
            remaining + reduce_group_size - 1
        ) // reduce_group_size
        total_calls += remaining

    total_calls += 1
    completed_calls = 0

    def report_progress(message):
        nonlocal completed_calls
        completed_calls += 1

        if progress_callback is not None:
            progress_callback(
                message,
                min(completed_calls / total_calls, 1.0),
            )

    # Step 1: Summarize each batch of document excerpts.
    for batch_number, start in enumerate(
        range(0, total_chunks, batch_size),
        start=1,
    ):
        batch = chunks[start:start + batch_size]
        batch_parts = []

        for doc in batch:
            page_number = doc.metadata.get("page", 0) + 1

            batch_parts.append(
                f"[Page {page_number}]\n{doc.page_content}"
            )

        batch_text = "\n\n".join(batch_parts)

        prompt = f"""
You are PaperPilot AI, a helpful study assistant.

Summarize the following excerpts from a PDF document.

Write 4-6 informative bullet points. Include the main
concepts, definitions, facts, and useful examples.

Rules:
- Use only information present in the excerpts.
- Preserve important details and page references.
- Avoid repeating the same idea.
- Do not add unsupported facts.
- Use clear, simple language.
- Write complete sentences.

Document excerpts:
{batch_text}

Summary:
"""

        response = llm.invoke(prompt)
        partial_summaries.append(response.content.strip())

        report_progress(
            f"Summarizing batch {batch_number} of {initial_batches}"
        )

    # Step 2: Combine summaries when there are many batches.
    reduction_round = 0

    while len(partial_summaries) > 4:
        reduction_round += 1
        reduced_summaries = []

        groups = [
            partial_summaries[i:i + reduce_group_size]
            for i in range(
                0,
                len(partial_summaries),
                reduce_group_size,
            )
        ]

        for group_number, group in enumerate(groups, start=1):
            combined_text = "\n\n".join(group)

            prompt = f"""
You are combining summaries of the same PDF document.

Create one concise summary of the information below.

Rules:
- Keep distinct, important facts and concepts.
- Remove repeated information.
- Do not invent facts or add outside knowledge.
- Preserve useful page references.
- Use complete sentences and concise bullet points.

Existing summaries:
{combined_text}

Combined summary:
"""

            response = llm.invoke(prompt)
            reduced_summaries.append(response.content.strip())

            report_progress(
                f"Combining summaries: round {reduction_round}, "
                f"group {group_number} of {len(groups)}"
            )

        partial_summaries = reduced_summaries

    # Step 3: Produce the final study summary.
    combined_text = "\n\n".join(partial_summaries)

    final_llm = ChatOllama(
    model=LLM_MODEL,
    temperature=0,
    num_predict=700,
    )
    
    final_prompt = f"""
You are PaperPilot AI, helping students study PDF documents.

Create a useful, well-organized summary of the document
using only the information in the supplied summaries.

Use these headings:

## Overview
Explain the main topic in 2-3 sentences.

## Key Points
Cover the most important concepts, facts, and ideas.
Combine related points and avoid duplication.

## Important Details
Include useful definitions, examples, names, and dates
that add information not already covered.

## Quick Revision Notes
Provide a short list of the most important takeaways.

Rules:
- Include only information supported by the summaries.
- Do not invent new topics, facts, or examples.
- Do not repeat definitions under multiple headings.
- Keep the summary concise but informative.
- Preserve relevant [Page N] references.
- Omit headings that have no relevant information.
- Write complete sentences and bullet points.
- Prefer a shorter complete summary over an unfinished one.

Supplied summaries:
{combined_text}

Final summary:
"""

    response = final_llm.invoke(final_prompt)
    summary = response.content.strip()

    report_progress("Summary complete")

    return summary


if __name__ == "__main__":
    pdf_path = input(
        "Enter the PDF path: "
    ).strip().strip('"')

    chunks = load_and_split_pdf(pdf_path)
    vector_store = create_vector_store(chunks)

    print(
        "\nPaperPilot AI is ready! "
        "Type 'exit' to quit."
    )

    while True:
        question = input("\nYour question: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        result = answer_question(
            vector_store,
            question,
        )

        print("\nAnswer:\n")
        print(result["answer"])

        print("\nSources:")

        for source in result["sources"]:
            print(
                f"- {source['file']}, "
                f"Page {source['page']}"
            )
