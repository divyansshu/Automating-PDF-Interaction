---
title: PDF AI Interaction Backend
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 📄 PDF AI Assistant

A full-stack application that allows users to upload PDF documents and interact with them using natural language. Built with **FastAPI**, **React**, **LangChain**, and **Hugging Face**.

## 🚀 Features

- **PDF Upload & Processing**: Automatically extracts text, chunks it, and generates vector embeddings.
- **RAG Pipeline**: Uses Retrieval-Augmented Generation to answer questions based *only* on the PDF content.
- **LLM Integration**: Powered by **Meta LLaMA 3.1 8B Instruct** (via Hugging Face API) for high-quality responses.
- **Vector Search**: Efficient similarity search using **FAISS** (with in-memory fallback).
- **Interactive Chat UI**:
  - Real-time chat interface.
  - **Markdown Support**: Renders lists, code blocks, and bold text properly.
  - **Auto-scroll**: Keeps the latest message in view.
  - **Persistence**: Chat history is saved locally so you don't lose progress on refresh.
- **Responsive Design**: Beautiful, modern UI with gradient styling.

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **LLM Orchestration**: LangChain
- **Model Provider**: Hugging Face Inference API
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (Local)
- **Vector Store**: FAISS (Facebook AI Similarity Search)

### Frontend
- **Library**: React.js
- **Styling**: CSS3 (Custom gradients & animations)
- **HTTP Client**: Axios
- **Rendering**: `react-markdown`

## 📋 Prerequisites

- Python 3.8+
- Node.js & npm
- A [Hugging Face Account](https://huggingface.co/) & API Token.
- Access to `meta-llama/Meta-Llama-3.1-8B-Instruct` (Accept license on HF model page).

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/divyansshu/Automating-PDF-Interaction.git
cd "Automating PDF Interaction"
```

### 2. Backend Setup
Navigate to the backend folder and install dependencies:
```bash
cd backend
# Create virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**Configure Environment Variables:**
Create a `.env` file in `backend/app/.env`:
```env
HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
```

**Run the Server:**
```bash
cd app
uvicorn main:app --reload
```
The backend will start at `http://localhost:8000`.

### 3. Frontend Setup
Open a new terminal and navigate to the frontend folder:
```bash
cd frontend
npm install
npm start
```
The app will open at `http://localhost:3000`.

## 💡 Usage

1.  Open the web app.
2.  Click **"Upload PDF"** and select a document.
3.  Wait for the processing (extraction & embedding generation).
4.  Once done, you will be redirected to the chat screen.
5.  Ask any question about your PDF!
6.  Use the **"Upload New PDF"** button to reset and start over.

## 🛡️ License

This project is open-source and available under the MIT License.
