# 📄 NanoOCR — Internal Document OCR System

> An internal Optical Character Recognition (OCR) system powered by **GLM-OCR**, featuring a FastAPI backend, PostgreSQL database, async task processing, and a React frontend that renders recognized text as structured **Markdown**.

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

NanoOCR is built to digitize, store, and retrieve internal organization documents from images or PDFs. Users upload a file, the system processes it through the **GLM-OCR** model, and returns the recognized content structured as **Markdown**. All processing history is persisted in the database for future retrieval and search.

### Key Features

| Feature | Description |
|---|---|
| 📤 File Upload | Supports images (JPG, PNG, TIFF, WebP) and PDF |
| 🤖 Automatic OCR | Processed by the GLM-OCR model |
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
           │                        │
┌──────────▼──────────┐   ┌─────────▼────────────────────┐
│   GLM-OCR Engine    │   │   PostgreSQL Database         │
│  (Model Inference)  │   │   documents / ocr_results     │
└─────────────────────┘   └──────────────────────────────┘
```

---

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** — REST API framework
- **GLM-OCR** — Character recognition model (based on ChatGLM)
- **SQLAlchemy** — ORM
- **Alembic** — Database migrations
- **Celery + Redis** — Async task queue for OCR processing
- **MinIO / AWS S3** — Original file storage

### Frontend
- **React 18 + TypeScript**
- **Vite** — Build tool
- **TailwindCSS** — Styling
- **react-markdown** — Renders OCR output as Markdown
- **react-dropzone** — Drag-and-drop file upload
- **Axios** — HTTP client

### Database
- **PostgreSQL 15** — Primary database
- **Redis** — Cache & task queue broker

---

## Project Structure

```
NanoOCR/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── documents.py     # Document CRUD endpoints
│   │   │   │   │   ├── ocr.py           # OCR processing endpoints
│   │   │   │   │   └── search.py        # Full-text search
│   │   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py                # App configuration
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── migrations/
│   │   ├── models/
│   │   │   ├── document.py              # Document ORM model
│   │   │   └── ocr_result.py            # OCR result ORM model
│   │   ├── schemas/
│   │   │   ├── document.py              # Pydantic schemas
│   │   │   └── ocr_result.py
│   │   ├── services/
│   │   │   ├── ocr_service.py           # GLM-OCR inference logic
│   │   │   ├── storage_service.py       # File upload & storage
│   │   │   └── markdown_service.py      # Markdown formatting
│   │   ├── tasks/
│   │   │   └── ocr_tasks.py             # Celery async tasks
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUploader/            # File upload area
│   │   │   ├── DocumentViewer/          # Markdown output viewer
│   │   │   ├── DocumentList/            # Document list & management
│   │   │   └── StatusBadge/             # OCR status indicator
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── DocumentDetail.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── api/
│   │   │   └── client.ts                # Axios API client
│   │   ├── hooks/
│   │   │   └── useOCR.ts
│   │   └── types/
│   │       └── document.ts
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

Stores metadata for each uploaded document.

```sql
CREATE TABLE documents (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(255) NOT NULL,           -- Original file name
    file_path     TEXT NOT NULL,                   -- File path on storage
    file_type     VARCHAR(50) NOT NULL,             -- File type: image / pdf
    file_size     BIGINT,                           -- File size in bytes
    status        VARCHAR(50) DEFAULT 'pending',    -- pending | processing | done | failed
    uploaded_by   VARCHAR(100),                    -- Uploader identifier
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
```

**`status` values:**

| Value | Description |
|---|---|
| `pending` | Queued, awaiting processing |
| `processing` | OCR in progress |
| `done` | Successfully completed |
| `failed` | Processing error occurred |

---

### Table: `ocr_results`

Stores the OCR output for each document.

```sql
CREATE TABLE ocr_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    raw_text        TEXT,                           -- Raw recognized text
    markdown_output TEXT,                           -- Formatted Markdown output
    confidence      FLOAT,                          -- Overall confidence score (0.0 – 1.0)
    language        VARCHAR(20) DEFAULT 'en',       -- Detected language
    page_count      INTEGER DEFAULT 1,              -- Number of pages (for PDFs)
    model_version   VARCHAR(50),                    -- GLM-OCR model version used
    processing_time FLOAT,                          -- Processing duration in seconds
    error_message   TEXT,                           -- Error details if failed
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Table Relationship

```
documents (1) ──── (1) ocr_results
     │
     └── id (UUID) → document_id in ocr_results
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
| `POST` | `/ocr/process/{document_id}` | Trigger OCR for a document |
| `GET` | `/ocr/result/{document_id}` | Retrieve OCR result |
| `GET` | `/ocr/status/{document_id}` | Check processing status |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/search?q={query}` | Full-text search across OCR results |

---

### Example Request / Response

**Upload a file:**
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

file: [binary]
```

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "contract_2024.pdf",
  "status": "pending",
  "created_at": "2024-01-15T08:30:00Z"
}
```

**OCR result:**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "markdown_output": "# Employment Contract\n\n**Date:** January 15, 2024\n\n...",
  "confidence": 0.97,
  "language": "en",
  "processing_time": 2.34
}
```

---

## Frontend UI

### Main Screen — Upload & OCR

The interface is split into two panels:

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

- **Left panel** — File upload area with drag-and-drop, image/PDF preview, and the OCR trigger button
- **Right panel** — OCR output rendered as full Markdown with headings, tables, lists, and bold text

### Dashboard Screen

Displays:
- Total number of processed documents
- OCR task queue status
- Recent documents list with filtering and sorting
- CRUD actions — view, rename, delete

---

## Installation

### Requirements

- Docker & Docker Compose
- Python 3.11+ (for local setup without Docker)
- Node.js 18+ (for local setup without Docker)
- GPU recommended for GLM-OCR (CUDA 11.8+)

### Quick Start with Docker

```bash
# 1. Clone the repository
git clone https://github.com/lecuong1502/NanoOCR.git
cd NanoOCR

# 2. Copy the environment config
cp .env.example .env

# 3. Edit .env with your settings
nano .env

# 4. Start all services
docker compose up -d

# 5. Run database migrations
docker compose exec backend alembic upgrade head
```

Access the app:
- Frontend: http://localhost:3000
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc

### Local Setup (without Docker)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Environment Variables

Create a `.env` file from `.env.example`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ocr_db

# Redis (Celery broker)
REDIS_URL=redis://localhost:6379/0

# Storage (MinIO or S3)
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=ocr-documents

# GLM-OCR Model
GLM_OCR_MODEL_PATH=./models/glm-ocr
GLM_OCR_DEVICE=cuda          # or cpu

# App
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000
```

---

## Usage

### 1. Upload a Document

Go to the home page → drag and drop or click to select a file (JPG, PNG, PDF, TIFF) → click **"Run OCR"**.

### 2. View the Result

Once processed (typically 2–10 seconds), the result appears in the **right panel** rendered as formatted Markdown.

### 3. Manage Documents

Navigate to the **"Documents"** tab to browse history, search content, reload results, or delete documents.

### 4. Search Content

Use the search bar to perform a full-text search across all previously processed documents.

---

## Markdown Output Format

The GLM-OCR model combined with `markdown_service` automatically structures the output:

````markdown
# Document Title

**Document Type:** Employment Contract
**Date:** January 15, 2024
**Department:** Human Resources

---

## I. Party Information

**Party A (Employer):**
Company name: ...
Address: ...

**Party B (Employee):**
Full name: ...
Date of birth: ...

---

## II. Contract Terms

1. Job position: ...
2. Contract duration: ...
3. Salary: ...

---

## III. Appendix Table

| No. | Item        | Value   |
|-----|-------------|---------|
| 1   | Base salary | $2,000  |
| 2   | Allowance   | $300    |

---

> ⚠️ **OCR Note:** Confidence: 97% — Language: English
````

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'feat: add feature X'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## License

This project is distributed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">
  Made with ❤️ by <strong>lecuong1502</strong>
</div>
