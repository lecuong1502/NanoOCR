# Contributing to NanoOCR

Thank you for taking the time to contribute! 🎉  
NanoOCR is an internal document OCR system and we welcome contributions of all kinds — bug fixes, new features, documentation improvements, and more.

Please read this guide before submitting any changes.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful and constructive environment for everyone. Be kind, be patient, and assume good intent.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/NanoOCR.git
   cd NanoOCR
   ```
3. **Add the upstream remote** so you can sync future changes:
   ```bash
   git remote add upstream https://github.com/lecuong1502/NanoOCR.git
   ```
4. Follow the [Development Setup](#development-setup) steps below.

---

## Project Structure

```
NanoOCR/
├── backend/       # FastAPI app, Qwen3-VL-4B-Instruct service, database models
├── frontend/      # React + TypeScript UI
├── docker-compose.yml
├── .env.example
├── README.md
└── CONTRIBUTING.md
```

For a detailed breakdown, refer to the [Project Structure](README.md#project-structure) section in the README.

---

## Development Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### Run locally

```bash
# Copy environment config
cp .env.example .env

# Start all services with Docker
docker compose up -d

# Apply database migrations
docker compose exec backend alembic upgrade head
```

Or run each service without Docker — see [Local Setup](README.md#local-setup-without-docker) in the README.

---

## Branching Strategy

We follow a simple **feature-branch workflow**:

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready code |
| `develop` | Integration branch for ongoing work |
| `feature/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `docs/<name>` | Documentation updates |
| `chore/<name>` | Refactoring, dependency updates |

**Always branch off from `develop`**, not `main`:

```bash
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

---

## Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <short description>
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, missing semicolons, etc. (no logic change) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Build process, dependency updates, tooling |

### Examples

```bash
git commit -m "feat(ocr): add confidence threshold filter"
git commit -m "fix(api): handle empty file upload gracefully"
git commit -m "docs(readme): update installation steps"
git commit -m "refactor(db): normalize ocr_results table"
git commit -m "test(ocr): add unit tests for markdown_service"
```

---

## Pull Request Process

1. **Sync your branch** with the latest `develop` before opening a PR:
   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

2. **Ensure all tests pass** (see [Testing](#testing) below)

3. **Open a Pull Request** against the `develop` branch — not `main`

4. Fill in the PR template:
   - What does this PR do?
   - How was it tested?
   - Any breaking changes?
   - Screenshots (for UI changes)

5. Request a review from at least **one maintainer**

6. Address all review comments before merging

7. PRs are merged using **Squash and Merge** to keep the history clean

> ⚠️ PRs submitted directly against `main` will be rejected unless they are hotfixes.

---

## Coding Standards

### Backend (Python)

- Follow [PEP 8](https://pep8.org/) style guide
- Use **type hints** for all function signatures
- Use `black` for formatting and `ruff` for linting:
  ```bash
  black app/
  ruff check app/
  ```
- Keep business logic in `services/`, not in route handlers
- All new endpoints must have a corresponding Pydantic schema in `schemas/`

### Frontend (TypeScript / React)

- Use **functional components** with hooks only — no class components
- Follow the existing component folder structure: `ComponentName/index.tsx`
- Use **TailwindCSS** utility classes for styling — avoid inline styles
- Run ESLint before committing:
  ```bash
  npm run lint
  ```
- Avoid `any` types — define proper TypeScript interfaces in `types/`

### General

- Keep functions small and single-purpose
- Write self-documenting code; add comments only when the *why* is not obvious
- Do not commit `.env` files, secrets, or model weights

---

## Testing

### Backend

```bash
cd backend
pytest tests/ -v
```

- Unit tests live in `backend/tests/`
- Use `pytest` with `httpx` for API integration tests
- Aim for coverage on all service-layer functions (`ocr_service`, `markdown_service`, etc.)

### Frontend

```bash
cd frontend
npm run test
```

- Use **Vitest** + **React Testing Library** for component tests
- Test user interactions, not implementation details

### Before submitting a PR, make sure

- [ ] All existing tests pass
- [ ] New functionality has accompanying tests
- [ ] No linting errors

---

## Reporting Bugs

Open a [GitHub Issue](https://github.com/lecuong1502/NanoOCR/issues) and include:

- **Summary** — A clear description of the bug
- **Steps to reproduce** — Minimal steps to reliably trigger the issue
- **Expected behavior** — What should happen
- **Actual behavior** — What actually happens
- **Environment** — OS, Python version, Node version, GPU/CPU, Docker version
- **Logs / Screenshots** — Attach any relevant output

---

## Requesting Features

Open a [GitHub Issue](https://github.com/lecuong1502/NanoOCR/issues) with the label `enhancement` and describe:

- **Problem** — What use case or pain point does this address?
- **Proposed solution** — How you envision it working
- **Alternatives considered** — Other approaches you thought about
- **Additional context** — Mockups, examples, or references

---

## Questions?

If you have any questions about contributing, feel free to open a [Discussion](https://github.com/lecuong1502/NanoOCR/discussions) or reach out via the issue tracker.

---

<div align="center">
  Thank you for helping make <strong>NanoOCR</strong> better! 🚀
</div>
