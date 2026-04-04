# 📄 NanoOCR — Internal Document OCR System

> An internal Optical Character Recognition (OCR) system powered by **Qwen3-VL-4B-Instruct** via **Ollama**, featuring a FastAPI backend, PostgreSQL database, Celery async task processing, and a React frontend that renders recognized text as structured **Markdown**.

---

## 🗂️ Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Backend API](#backend-api)
- [Frontend UI](#frontend-ui)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Markdown Output Format](#markdown-output-format)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

NanoOCR is built to digitize, store, and retrieve internal organization documents from images or PDFs. Users upload a file, the system processes it through the **Qwen3-VL-4B-Instruct** model served via **Ollama**, and returns the recognized content structured as **Markdown**. All processing history is persisted in the database for future retrieval and search.

### Key Features

| Feature | Description |
|---|---|
| 📤 File Upload | Supports images (JPG, PNG, TIFF, WebP) and PDF |
| 🤖 Automatic OCR | Processed by Qwen3-VL-4B-Instruct via Ollama |
| 📝 Markdown Output | Results returned as structured, formatted Markdown |
| 🗃️ Full CRUD | Create, read, update, and delete documents |
| 🔍 Full-text Search | Search across all OCR-recognized content |
| 📊 Dashboard | Document statistics and processing queue status |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                   │
│   Upload UI  │  Markdown Viewer  │  Document Manager    │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP / REST API
┌──────────────────────────▼──────────────────────────────┐
│                   BACKEND (FastAPI)                      │
│   /upload  │  /ocr  │  /documents CRUD  │  /search      │
└──────────┬──────────────────────────────────────────────┘
           │                         │
┌──────────▼──────────┐   ┌──────────▼───────────────────┐
│   Celery Worker     │   │   PostgreSQL Database         │
│  + Redis Broker     │   │   documents / ocr_results     │
│         │           │   └──────────────────────────────┘
│         ▼           │
│  Ollama API         │
│  Qwen3-VL-4B        │
│  (via /api/chat)    │
└─────────────────────┘
```

---

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** — REST API framework
- **Ollama** — Local LLM server serving Qwen3-VL-4B-Instruct
- **SQLAlchemy** — ORM
- **Alembic** — Database migrations
- **Celery + Redis** — Async task queue for OCR processing
- **MinIO** — S3-compatible file storage
- **pdf2image + Pillow** — PDF to image conversion
- **httpx** — Async HTTP client for Ollama API

### Frontend
- **React 18 + TypeScript**
- **Vite** — Build tool
- **TailwindCSS** — Styling
- **react-markdown + remark-gfm** — Renders OCR output as Markdown
- **react-dropzone** — Drag-and-drop file upload
- **Axios** — HTTP client

### Database
- **PostgreSQL 15** — Primary database
- **Redis** — Cache & task queue broker

### Infrastructure (Docker)
- **Ollama** — Model serving (`localhost:11434`)
- **PostgreSQL** — Database (`localhost:5433`)
- **Redis** — Broker (`localhost:6380`)
- **MinIO** — Storage (`localhost:9000`)

---

## Project Structure

```
NanoOCR/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── documents.py     # Document CRUD endpoints
│   │   │       │   ├── ocr.py           # OCR trigger & status endpoints
│   │   │       │   └── search.py        # Full-text search
│   │   │       └── router.py
│   │   ├── core/
│   │   │   ├── config.py                # App configuration (pydantic-settings)
│   │   │   ├── dependencies.py          # FastAPI dependencies
│   │   │   ├── exceptions.py            # Custom HTTP exceptions
│   │   │   ├── logging.py               # Logging setup
│   │   │   └── security.py              # JWT helpers
│   │   ├── db/
│   │   │   ├── base.py                  # SQLAlchemy DeclarativeBase
│   │   │   ├── session.py               # Engine & get_db dependency
│   │   │   └── migrations/              # Alembic migration files
│   │   ├── models/
│   │   │   ├── document.py              # Document ORM model
│   │   │   └── ocr_result.py            # OCR result ORM model
│   │   ├── schemas/
│   │   │   ├── document.py              # Pydantic request/response schemas
│   │   │   └── ocr_result.py
│   │   ├── services/
│   │   │   ├── ocr_service.py           # Ollama API inference logic
│   │   │   ├── storage_service.py       # MinIO file upload/download
│   │   │   ├── document_service.py      # Document CRUD logic
│   │   │   └── ocr_result_service.py    # OCR result persistence
│   │   ├── tasks/
│   │   │   ├── celery_app.py            # Celery instance & config
│   │   │   └── ocr_tasks.py             # OCR Celery task (run_ocr)
│   │   └── main.py                      # FastAPI app entrypoint
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUploader/            # Drag-and-drop upload
│   │   │   ├── DocumentViewer/          # Markdown output viewer
│   │   │   ├── DocumentList/            # Document list & management
│   │   │   └── StatusBadge/             # OCR status indicator
│   │   ├── pages/
│   │   │   ├── Home.tsx                 # Upload + OCR split view
│   │   │   ├── DocumentDetail.tsx       # Single document view
│   │   │   └── Dashboard.tsx            # All documents dashboard
│   │   ├── api/client.ts                # Axios API client
│   │   ├── hooks/useOCR.ts              # Upload + polling hook (2min timeout)
│   │   └── types/document.ts            # TypeScript interfaces
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Database Schema

### Table: `documents`

```sql
CREATE TABLE documents (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(255) NOT NULL,
    file_path     TEXT NOT NULL,
    file_type     VARCHAR(50) NOT NULL,             -- image | pdf
    file_size     BIGINT,
    mime_type     VARCHAR(100),
    status        VARCHAR(50) DEFAULT 'pending',    -- pending | processing | done | failed
    uploaded_by   VARCHAR(100),
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### Table: `ocr_results`

```sql
CREATE TABLE ocr_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    raw_text        TEXT,
    markdown_output TEXT,
    confidence      FLOAT,
    language        VARCHAR(20) DEFAULT 'en',
    page_count      INTEGER DEFAULT 1,
    model_version   VARCHAR(50),
    processing_time FLOAT,
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Backend API

Base URL: `http://localhost:8000/api/v1`

### Documents — CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/documents` | List all documents (paginated) |
| `GET` | `/documents/{id}` | Get a single document |
| `POST` | `/documents/upload` | Upload a new document |
| `PUT` | `/documents/{id}` | Update document metadata |
| `DELETE` | `/documents/{id}` | Delete a document |

### OCR

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ocr/process/{document_id}` | Enqueue OCR task via Celery |
| `GET` | `/ocr/result/{document_id}` | Retrieve OCR result |
| `GET` | `/ocr/status/{document_id}` | Check processing status |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/search?q={query}` | Full-text search across OCR results |

---

## Frontend UI

### Main Screen — Upload & OCR

```
┌─────────────────────┬─────────────────────────────────┐
│    📤 INPUT PANEL   │      📄 OUTPUT PANEL             │
│                     │                                  │
│  ┌───────────────┐  │   # Document Title               │
│  │  Drag & drop  │  │                                  │
│  │  file here or │  │   **Field:** Value               │
│  │  click to     │  │                                  │
│  │  browse       │  │   ## Section 1                   │
│  └───────────────┘  │   Recognized content here...     │
│                     │                                  │
│  Supported formats: │   > Note: ...                    │
│  JPG PNG PDF TIFF   │                                  │
│                     │   | Col 1  | Col 2  |            │
│  [Run OCR ▶]        │   |--------|--------|            │
│                     │   | Data   | Data   |            │
└─────────────────────┴─────────────────────────────────┘
```

---

## Installation

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Ollama with Qwen3-VL-4B-Instruct model

### Step 1 — Pull Qwen3-VL model into Ollama

```bash
docker exec ollama ollama pull adelnazmy2002/Qwen3-VL-4B-Instruct:Q4_K_M
# or any Qwen3-VL variant available in your Ollama instance
```

Verify the model is available:

```bash
docker exec ollama ollama list
```

### Step 2 — Start infrastructure services

```bash
cd NanoOCR
docker compose up -d db redis minio
```

Wait until all are healthy:

```bash
docker ps | grep -E "nanoocr_db|nanoocr_redis|nanoocr_minio"
```

### Step 3 — Configure environment

```bash
# Copy and edit the backend .env
cp .env.example backend/.env
nano backend/.env
```

Key values to set (see [Environment Variables](#environment-variables)):
- `DATABASE_URL` — use `localhost` with the mapped port
- `STORAGE_ENDPOINT` — use `http://localhost:9000`
- `REDIS_URL` / `CELERY_BROKER_URL` — use `localhost` with the mapped port
- `OLLAMA_BASE_URL` — `http://localhost:11434`
- `OCR_MODEL_NAME` — exact model name from `ollama list`

### Step 4 — Run database migrations

```bash
cd backend
source ../.venv/bin/activate   # activate your virtual environment
alembic upgrade head
```

### Step 5 — Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 6 — Start backend services

Open **3 separate terminals**, all from the `backend/` directory:

**Terminal 1 — FastAPI:**
```bash
cd NanoOCR/backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Celery worker:**
```bash
cd NanoOCR/backend
celery -A app.tasks.celery_app worker --loglevel=info -Q ocr --concurrency=1
```

### Step 7 — Start frontend

**Terminal 3:**
```bash
cd NanoOCR/frontend
npm install
npm run dev
```

### Access the app

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |

---

## Environment Variables

Create `backend/.env` with the following (use `localhost` for all services when running locally):

```env
# PostgreSQL
POSTGRES_USER=ocr_user
POSTGRES_PASSWORD=ocr_pass
POSTGRES_DB=ocr_db
DATABASE_URL=postgresql://ocr_user:ocr_pass@localhost:5433/ocr_db

# Redis
REDIS_URL=redis://localhost:6380/0
CELERY_BROKER_URL=redis://localhost:6380/0
CELERY_RESULT_BACKEND=redis://localhost:6380/1

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=ocr-documents

# Ollama OCR
OLLAMA_BASE_URL=http://localhost:11434
OCR_MODEL_NAME=adelnazmy2002/Qwen3-VL-4B-Instruct:Q4_K_M
OCR_MAX_NEW_TOKENS=2048

# App
SECRET_KEY=change-me-in-production
```

> ⚠️ **Important:** Do NOT use Docker service hostnames (`db`, `minio`, `redis`) in `backend/.env` when running locally. Always use `localhost` with the mapped host ports.

---

## Usage

### 1. Upload a Document

Go to `http://localhost:3000` → drag and drop or click to select a file (JPG, PNG, PDF, TIFF) → click **"Run OCR"**.

### 2. View the Result

Once processed (typically 3–10 seconds), the result appears in the **right panel** rendered as formatted Markdown.

### 3. Manage Documents

Navigate to the **"Documents"** tab to browse history, search content, reload results, or delete documents.

### 4. Search Content

Use the search bar to perform a full-text search across all previously OCR-processed documents.

---

## Markdown Output Format

Qwen3-VL-4B-Instruct returns structured Markdown output:

````markdown
# Document Title

**Document Type:** Employment Contract
**Date:** January 15, 2024

---

## I. Party Information

**Party A:** Company name ...
**Party B:** Full name ...

---

## II. Contract Terms

1. Job position: ...
2. Salary: ...

---

## III. Table

| No. | Item        | Value  |
|-----|-------------|--------|
| 1   | Base salary | $2,000 |
| 2   | Allowance   | $300   |
````

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<div align="center">
  Made with ❤️ by <strong>lecuong1502</strong>
</div>