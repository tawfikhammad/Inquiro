# 🧠 Inquiro — Research Assistant API

**Inquiro** is an intelligent research assistant built with **FastAPI**, designed to simplify the management, summarization, and understanding of academic papers. With seamless integration of **LLMs** (OpenAI, Cohere, Gemini) and **vector databases** (Qdrant), Inquiro allows you to:

- Upload and organize research papers by project
- Automatically generate intelligent summaries
- Chat with the paper content for deeper understanding
- Manage data with MongoDB and Qdrant

---

## Features

- **File Upload**: Upload and validate PDF research papers by project.
- **Auto Summarization**: Extract content and summarize using LLMs.
- **Paper Chat**: Ask questions and receive answers from paper content.
- **Markdown Editing**: View, edit, and update summaries in `.md` format.
- **Modular Architecture**: Clean separation of routes, controllers, models.
- **MongoDB Integration**: Store project, paper, and summary metadata.
- **Qdrant Vector DB**: Efficient document embedding and retrieval.

---

## Project Structure
```
backend/
├── main.py # FastAPI app entry
├── routes/ # API endpoints 
├── controllers/ # Business logic
├── models/ # DB models and schemas
├── AI/
│ ├── LLM/ # LLM providers (OpenAI, Cohere, Gemini)
│ └── VectorDB/ # Vector DB (Qdrant)
├── utils/ # Utilities for PDFs, paths, enums
├── assets/ # Uploaded PDFs and summaries
└── config/ # App settings and environment
```

## Tech Stack

- **Backend**: FastAPI
- **Database**: MongoDB (via Motor)
- **LLMs**: OpenAI / Cohere / Gemini
- **Vector DB**: Qdrant
- **PDF Processing**: PyMuPDF
- **Async File Handling**: Aiofiles

---

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/tawfikhammad/inquiro.git
cd inquiro/backend
```
### 2. Create your .env file
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Run the app
```bash
uvicorn main:app --reload
```
---

## 🤝 Contributions
PRs are welcome! If you want to contribute or report a bug, please open an issue or submit a pull request.

# This Project is Under Active Developing 
