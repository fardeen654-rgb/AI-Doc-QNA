# 📄 AI Document Q&A System (Multi-User RAG Platform)

A production-grade AI application that allows users to upload PDF documents and ask natural language questions, powered by **Retrieval Augmented Generation (RAG)**.

---

## 🚀 Project Highlights
- **Multi-user Authentication**: Secure login/signup with role-based access (Admin/User).
- **Data Isolation**: Files and vector indexes are siloed per user to ensure privacy.
- **Semantic Search**: Powered by **FAISS** and **Sentence-Transformers** for lightning-fast retrieval.
- **High-Speed Inference**: Powered by **Groq (LLaMA-3)** for near-instant AI responses.
- **SaaS Features**: Daily rate limiting, usage analytics, and automated email notifications.
- **Data Ownership**: Export chat history to **CSV** or **PDF** and manage your uploaded files.

---

## 🖼️ System Architecture
The system follows a modular RAG pipeline designed for scalability and data privacy:



1. **Ingestion**: PDF → Text Extraction (PyMuPDF) → Cleaning → Chunking.
2. **Indexing**: Chunks → Embeddings (Sentence-Transformers) → FAISS Vector Store.
3. **Retrieval**: Query → Embedding → Similarity Search in FAISS.
4. **Generation**: Context + Query → Groq LLM (LLaMA-3) → User Response.

---

## 🏗️ Tech Stack

### **Backend & Database**
- **Python/Flask**: Core application logic.
- **Flask-SQLAlchemy**: ORM for managing Users, History, and Analytics.
- **SQLite**: Local relational database.
- **Flask-Login**: Session management and security.

### **AI & Vector Search**
- **Groq Cloud API**: LLaMA-3-8b for high-speed generation.
- **FAISS**: Local vector database for semantic search.
- **Sentence-Transformers**: `all-MiniLM-L6-v2` for generating text embeddings.

### **Frontend**
- **Bootstrap 5**: Responsive, mobile-friendly UI.
- **Jinja2**: Dynamic template rendering.

---

## ✨ Features Roadmap (Development Journey)

| Phase | Milestone | Features |
|:---:|:---|:---|
| **1** | **Foundations** | Flask setup, PDF extraction, Text cleaning |
| **2** | **AI Core** | Chunking strategy, Embeddings, FAISS integration |
| **3** | **RAG Pipeline** | Context-aware prompting, Groq LLM integration |
| **4** | **Auth & Privacy** | Multi-user support, Password hashing, Folder isolation |
| **5** | **Admin & Analytics** | Global usage tracking, User management, Admin Dash |
| **6** | **Productivity** | CSV/PDF exports, Rate limiting, Email SMTP alerts |

---

## 📌 Resume-Ready Bullet Points

- **Full-Stack RAG Development**: Built a production-ready AI Q&A platform using Flask and FAISS, enabling users to query private PDF documents with LLaMA-3.
- **System Security**: Implemented per-user document isolation and password hashing (Werkzeug) to ensure 100% data privacy in a multi-user environment.
- **Scalability**: Designed an analytics and rate-limiting system using SQLAlchemy to manage API costs and prevent system abuse.
- **Data Portability**: Developed automated export features (ReportLab/CSV) for chat history, ensuring user data transparency and compliance.

---

## 🧪 How to Run Locally

1. **Clone the repo**
2. **Setup Environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt