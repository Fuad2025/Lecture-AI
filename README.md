
# Lecture AI – Smart Academic Intelligence

An AI-powered academic learning assistant that helps university students understand their study materials through PDF summarization, document-based question answering, and automatically generated quizzes.

**Course:** CSE 4104 – Software Development III  
**Section:** 7A  
**Team:** T04  
**Institution:** Northern University of Business & Technology Khulna

---

## 1. Project Description

University students often have to study lengthy lecture notes, PDF documents, and other academic materials. Understanding large amounts of information and preparing for examinations can be time-consuming.

**Lecture AI – Smart Academic Intelligence** aims to make this process easier by providing an AI-powered web application where students can upload their academic PDF documents and interact with their study materials.

The system uses Artificial Intelligence to generate document summaries, answer questions based on uploaded materials, and create multiple-choice quizzes for practice.

The main goal is to provide students with a simple and organized platform that supports more efficient and interactive learning.

## 2. Project Objectives

- Help students understand lengthy academic documents more efficiently.
- Automatically generate summaries from uploaded PDF materials.
- Allow students to ask questions about their own study documents.
- Generate multiple-choice quizzes using AI.
- Provide automatic quiz evaluation and score calculation.
- Maintain a personal library of uploaded academic documents.
- Improve students' study experience through AI-assisted learning.

## 3. Proposed Features

### User Authentication
- Student registration.
- Secure login and logout.
- Personal student accounts.

### PDF Document Management
- Upload academic PDF documents.
- Extract readable text from uploaded PDFs.
- Maintain a personal document library.
- View and delete uploaded documents.

### AI-Powered Learning Assistant
- Generate summaries of uploaded documents.
- Ask questions about selected documents.
- Receive AI-generated answers based on document content.

### AI Quiz Generator
- Generate multiple-choice questions from uploaded documents.
- Display questions with answer options.
- Allow students to attempt and submit quizzes.
- Automatically calculate quiz scores.
- View previous quiz results and history.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, Bootstrap, JavaScript |
| Backend | Python, Flask |
| Database | SQLite |
| Database ORM | SQLAlchemy |
| AI Integration | Google Gemini API |
| PDF Text Extraction | PyMuPDF |
| Version Control | Git and GitHub |
| Development Environment | Visual Studio Code |

## 5. System Architecture

The application follows a client-server architecture.

- **Frontend:** Provides the web interface through which students interact with the application.
- **Backend:** Flask handles authentication, document processing, AI integration, and quiz operations.
- **Database:** SQLite stores user information, document records, summaries, conversations, quizzes, and quiz results.
- **PDF Processing:** PyMuPDF extracts readable text from uploaded PDF documents.
- **AI Service:** Google Gemini API processes relevant document content to generate summaries, answers, and quiz questions.

### Basic System Workflow

1. A student registers or logs in.
2. The student uploads an academic PDF document.
3. The backend extracts text from the uploaded document.
4. The extracted content is used for AI-powered operations.
5. The student requests a summary, asks a question, or generates a quiz.
6. The backend communicates with the Gemini API and returns the generated result.
7. Quiz attempts and results are stored in the database.

## 6. Repository Structure

The following is the planned project structure. It may be updated as development progresses.

```text
Lecture-AI/
│
├── app/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── services/
│   └── models/
│
├── uploads/
│
├── tests/
│
├── config.py
├── run.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 7. Team Information

**Team Code:** T04  
**Section:** 7A

| Name | Designation |
|---|---|
| Md. Ashikur Reza | Team Leader |
| Md. Tareq Imroj | Team Member |
| Imtiaj Ahmed Sami | Team Member |
| Peter Pranto Sarkar | Team Member |

## 8. Development Status

**Current Phase:** Requirements Analysis and Initial System Design

The project is being developed as part of the Software Development III course.

Current development activities include:

- Project planning and requirement analysis.
- Preparation of the Software Requirements Specification (SRS).
- Initial Use Case Diagram.
- Initial Entity Relationship (ER) Diagram.
- Initial System Architecture Diagram.
- Development environment setup and repository preparation.

The application features are proposed and will be implemented and tested during the development process.

## 9. Future Enhancements

Possible future improvements include:

- Audio lecture upload and transcription.
- OCR support for scanned PDF documents.
- Flashcard generation.
- Personalized study recommendations.
- Advanced learning progress tracking.
- Support for additional document formats.

## 10. Repository

GitHub Repository:  
https://github.com/Fuad2025/Lecture-AI

---

**Lecture AI – Smart Academic Intelligence**  
CSE 4104 – Software Development III  
Team T04 | Section 7A
