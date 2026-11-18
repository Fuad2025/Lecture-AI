# Lecture AI – Smart Academic Intelligence

An AI-powered study assistant that helps university students learn from their own course materials. Students upload lecture PDFs, get AI-generated summaries, and practise with automatically generated multiple-choice quizzes.

**Course:** CSE 4104 – Software Development III
**Section:** 7A
**Team:** CSE4104-7A-T04
**Institution:** Northern University of Business & Technology Khulna

---

## Table of Contents

1. [Project Description](#1-project-description)
2. [Project Objectives](#2-project-objectives)
3. [Features](#3-features)
4. [Technology Stack](#4-technology-stack)
5. [System Architecture](#5-system-architecture)
6. [Project Structure](#6-project-structure)
7. [Getting Started](#7-getting-started)
8. [API Overview](#8-api-overview)
9. [Team](#9-team)
10. [Development Status](#10-development-status)
11. [Future Enhancements](#11-future-enhancements)

---

## 1. Project Description

University students often have to study lengthy lecture notes and PDF documents, and preparing for examinations from them is time-consuming.

**Lecture AI** is a web application where students upload their own academic PDFs and use AI to understand them faster. The system extracts the text of each document, generates a summary, and creates multiple-choice quizzes that students can take, submit and review. The goal is a simple, organised platform that supports more efficient and interactive learning.

## 2. Project Objectives

- Help students understand lengthy academic documents more efficiently.
- Automatically generate summaries from uploaded PDF materials.
- Generate multiple-choice quizzes with a chosen number of questions and difficulty.
- Provide automatic quiz evaluation, score calculation and explanations.
- Keep a personal library of uploaded documents and a history of quiz attempts.

## 3. Features

### First working prototype

| Area | Feature |
|---|---|
| Authentication | Student registration, login and logout with secure password hashing |
| Documents | Upload PDF files (max 16 MB), personal document library |
| Text extraction | Readable text extracted from PDFs; PDFs with no extractable text (e.g. scanned images) are rejected with a clear message |
| AI summary | Summary generated from the extracted text and saved for reuse |
| AI quiz | Multiple-choice questions with a chosen number (1–20) and difficulty (easy / medium / hard) |
| Quiz taking | Answer, submit, and see the score, correct answers and explanations |
| History | Every quiz attempt is saved and listed on the dashboard |

### Not part of the first prototype

Chat with lecture, weak-topic tracker, "explain it differently", audio and voice features, live recording. See [Future Enhancements](#11-future-enhancements).

## 4. Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, Bootstrap, JavaScript (fetch) |
| Backend | Python, Flask |
| Authentication | Flask-Login (sessions), Werkzeug password hashing |
| Database | SQLite (configurable via `DATABASE_URL`, PostgreSQL/Supabase planned) |
| ORM | SQLAlchemy via Flask-SQLAlchemy |
| AI | Google Gemini API (`google-genai`) |
| PDF text extraction | PyMuPDF |
| Version control | Git and GitHub |
| Development environment | Visual Studio Code, Windows, Python virtual environment |

## 5. System Architecture

The application follows a client-server architecture.

- **Frontend:** HTML templates and JavaScript served by Flask. JavaScript talks to the backend with same-origin `fetch()` requests.
- **Backend:** Flask handles authentication, PDF processing, database access, and calls the AI service.
- **AI service:** `ai/ai_service.py` is the only module that talks to Gemini. The backend calls `generate_summary()` and `generate_quiz()`.
- **Database:** Stores users, documents (with extracted text and summary), quizzes and quiz attempts.

### Basic workflow

1. A student registers or logs in.
2. The student uploads a PDF and the backend extracts its text.
3. The student requests a summary or generates a quiz.
4. The backend sends the extracted text to the AI service and saves the result.
5. The student takes the quiz and submits answers.
6. The backend calculates the score, saves the attempt and returns detailed results.

## 6. Project Structure

```text
Lecture-AI/
├── backend/
│   ├── __init__.py
│   ├── app.py            # Flask app setup, config, login manager
│   ├── models.py         # Database models
│   ├── routes.py         # Page routes and API endpoints
│   └── pdf_service.py    # PDF text extraction (PyMuPDF)
├── ai/
│   ├── __init__.py
│   └── ai_service.py     # Gemini integration (summary and quiz generation)
├── frontend/
│   ├── templates/        # base, login, register, dashboard, study
│   └── static/
│       ├── css/
│       ├── js/           # auth.js, dashboard.js, study.js
│       └── images/
├── instance/             # SQLite database (not committed)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 7. Getting Started

These steps are for Windows (PowerShell) with Python 3 installed.

### 1. Clone the repository

```
git clone https://github.com/Fuad2025/Lecture-AI.git
cd Lecture-AI
```

### 2. Create and activate a virtual environment

```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your own values:

```
copy .env.example .env
```

| Variable | Description |
|---|---|
| `SECRET_KEY` | Random secret used to sign session cookies |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `GEMINI_MODEL` | Gemini model name used by the AI service |
| `DATABASE_URL` | Database connection string (default `sqlite:///lecture_ai.db`) |

Generate a secret key with:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

The `.env` file is listed in `.gitignore`. Never commit real keys.

### 5. Run the application

Always run from the project root with the virtual environment active:

```
python -m backend.app
```

Open `http://127.0.0.1:5000` in your browser. The database file is created automatically in `instance/` on first run.

If you change a database model during development, stop the server and delete `instance/lecture_ai.db` so it is recreated.

## 8. API Overview

All responses are JSON and contain `"success": true` or `false`. Errors look like `{"success": false, "error": "Readable message"}`. Every endpoint except register and login requires a logged-in user and returns JSON `401` otherwise. Users can only access their own data.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create an account (and log in) |
| POST | `/api/auth/login` | Log in |
| POST | `/api/auth/logout` | Log out |
| POST | `/api/documents/upload` | Upload a PDF (multipart field `file`) |
| GET | `/api/documents` | List the user's documents |
| POST | `/api/summaries/generate` | Generate or fetch a document summary |
| POST | `/api/quizzes/generate` | Generate a quiz from a document |
| POST | `/api/quizzes/<quiz_id>/submit` | Submit answers, get score and results |
| GET | `/api/quizzes/history` | List the user's quiz attempts |

HTTP codes: `400` bad input, `401` not logged in, `404` not found, `500` server error, `502` AI service failed.

### Pages

| Route | Page |
|---|---|
| `/` | Redirects to `/dashboard` if logged in, otherwise `/login` |
| `/login`, `/register` | Authentication pages |
| `/dashboard` | Upload form, document library, quiz history |
| `/study/<document_id>` | Summary, quiz generation, quiz taking and results |

## 9. Team

**Team:** CSE4104-7A-T04 | **Section:** 7A

| Name | Student ID | Role |
|---|---|---|
| Md. Ashikur Reza | 11230321219 | Team Leader & Backend Developer |
| Md. Tareq Imroj | 11230321233 | AI Integration & Testing |
| Imtiaj Ahmed Sami | 11230321217 | QA & Documentation |
| Peter Pranto Sarkar | 11240121668 | Frontend Development & Deployment |

## 10. Development Status

**Current phase:** Prototype development (backend foundation complete).

- [x] Project planning, SRS and initial diagrams
- [x] Backend skeleton, configuration and database connection
- [x] User model and authentication (register, login, logout)
- [ ] PDF upload and text extraction
- [ ] Document library endpoint
- [ ] AI summary and quiz generation
- [ ] Quiz submission, scoring and history
- [ ] Frontend pages
- [ ] Testing and deployment

## 11. Future Enhancements

- Chat with a selected document (document-grounded answers).
- Weak-topic tracker and "explain it differently".
- Deleting uploaded documents.
- OCR support for scanned PDFs.
- Audio lecture upload and transcription.
- Flashcard generation.
- Personalised study recommendations and progress tracking.
- Switching the database to Supabase PostgreSQL.

---

**Lecture AI – Smart Academic Intelligence**
CSE 4104 – Software Development III | CSE4104-7A-T04 | Section 7A

Repository: https://github.com/Fuad2025/Lecture-AI
