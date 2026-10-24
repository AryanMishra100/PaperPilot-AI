\# 📖 PaperPilot AI — Your PDF Study Assistant



PaperPilot AI is a local AI-powered study assistant that helps students understand and revise PDF documents using conversational question answering and automatic document summarization.



Upload textbooks, books, research papers, newspapers, notes, or other educational PDFs and interact with their content using AI.



\## ✨ Features



\- \*\*PDF Question Answering:\*\* Ask questions about the uploaded document in natural language.

\- \*\*Retrieval-Augmented Generation (RAG):\*\* Retrieves relevant document content to help generate context-based answers.

\- \*\*Source Citations:\*\* View source page references to help verify answers against the original PDF.

\- \*\*Document Summarization:\*\* Generate structured summaries with headings, key points, important details, and revision notes.

\- \*\*Local LLM Support:\*\* Uses Ollama to run a language model locally.

\- \*\*Semantic Search:\*\* Uses sentence-transformer embeddings and FAISS for document retrieval.

\- \*\*Chat Management:\*\* Clear conversation history or remove the current document.

\- \*\*Student-Friendly Interface:\*\* Simple web interface built with Streamlit.



\## 🛠️ Tech Stack



| Technology | Purpose |

|---|---|

| Python | Core programming language |

| Streamlit | User interface |

| LangChain | LLM and RAG pipeline integration |

| Ollama | Local language model execution |

| Qwen 2.5 1.5B | Local language model |

| Sentence Transformers | Text embeddings |

| FAISS | Vector storage and similarity search |

| PyPDF | PDF text extraction |



\## 🧠 How It Works



1\. \*\*Upload PDF:\*\* The user uploads a study document.

2\. \*\*Extract and Split Text:\*\* Text is extracted from the PDF and divided into smaller chunks.

3\. \*\*Generate Embeddings:\*\* Text chunks are converted into vector representations.

4\. \*\*Create Vector Store:\*\* FAISS stores the vectors for similarity-based retrieval.

5\. \*\*Ask Questions:\*\* Relevant chunks are retrieved for the user's question.

6\. \*\*Generate Answers:\*\* The local LLM uses the retrieved context to answer questions.

7\. \*\*Generate Summary:\*\* The summarization pipeline creates a structured overview of the document.



\## 📂 Project Structure



```text

Paper\_PilotAI/

├── app.py

├── rag\_pipeline.py

├── requirements.txt

├── .gitignore

└── README.md

```



\- `app.py` — Streamlit application and user interface.

\- `rag\_pipeline.py` — PDF processing, vector retrieval, question answering, and summarization.

\- `requirements.txt` — Python dependencies.

\- `.gitignore` — Files and folders excluded from Git.



\## ⚙️ Prerequisites



Install the following before running the project:



\- Python 3.10 or a compatible Python version

\- Git

\- Ollama

\- The required Python packages listed in `requirements.txt`



\## 🚀 Installation and Setup



\### 1. Clone the repository



```bash

git clone YOUR\_GITHUB\_REPOSITORY\_URL

cd Paper\_PilotAI

```



Replace `YOUR\_GITHUB\_REPOSITORY\_URL` with the URL of your GitHub repository.



\### 2. Create a virtual environment



\*\*Windows PowerShell:\*\*



```powershell

python -m venv venv

.\\venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```powershell

python -m pip install -r requirements.txt

```



\### 4. Set up Ollama



Install Ollama from \[ollama.com](https://ollama.com/), then download the model:



```powershell

ollama pull qwen2.5:1.5b

```



Make sure the Ollama service is running before starting the application.



\### 5. Run the application



```powershell

streamlit run app.py

```



Streamlit will provide a local URL, usually `http://localhost:8501`.



\## 🔒 Privacy and Offline Usage



PaperPilot AI is designed to use a locally running language model through Ollama. After the required models and dependencies have been downloaded, core functionality can work without an internet connection, provided the application does not require any external services.



Actual offline behavior depends on model availability, local caches, and the application configuration.



\## ⚠️ Limitations



\- Answer quality depends on the selected language model and the retrieved document content.

\- Scanned PDFs may require OCR, which is not currently guaranteed.

\- Very large documents can take longer to process and summarize.

\- Source references help verification but do not guarantee that every answer is correct.

\- The project is intended as a learning and portfolio project, not a production-grade document management system.



\## 🔮 Future Improvements



\- Support OCR for scanned PDFs.

\- Improve summary quality and reduce repetition.

\- Add downloadable summaries and study notes.

\- Improve document history and multi-document support.

\- Add automated evaluation for answer relevance and citation accuracy.



\## 🎯 Project Objective



PaperPilot AI explores how Retrieval-Augmented Generation, semantic search, local language models, and document summarization can be combined to create a practical AI-powered learning assistant.



\---



\*\*Built with Python, LangChain, Streamlit, FAISS, and Ollama.\*\*

