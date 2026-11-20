import json

from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from backend.models import db, User, Document, Quiz, QuizAttempt
from backend.pdf_service import extract_text_from_pdf, PDFServiceError
from ai.ai_service import generate_summary, generate_quiz, AIServiceError

# A Blueprint is just a group of routes. app.py plugs it into the app.
main = Blueprint("main", __name__)


# ---------- Helper for error JSON ----------

def error_response(message, status_code):
    return jsonify({"success": False, "error": message}), status_code


# ---------- Page routes ----------

@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard_page"))
    return redirect(url_for("main.login_page"))


@main.route("/login")
def login_page():
    return render_template("login.html")


@main.route("/register")
def register_page():
    return render_template("register.html")


@main.route("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html", username=current_user.username)


@main.route("/study/<int:document_id>")
@login_required
def study_page(document_id):
    # 404 if the document doesn't exist or belongs to another user
    document = Document.query.filter_by(
        id=document_id, user_id=current_user.id
    ).first_or_404()
    return render_template(
        "study.html",
        document_id=document.id,
        filename=document.filename,
    )


# ---------- Auth API ----------

@main.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username:
        return error_response("Username is required", 400)
    if len(password) < 6:
        return error_response("Password must be at least 6 characters", 400)
    if User.query.filter_by(username=username).first():
        return error_response("Username is already taken", 400)

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)  # user is logged in after registering
    return jsonify({"success": True, "message": "Account created"}), 201


@main.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return error_response("Invalid username or password", 401)

    login_user(user)
    return jsonify({"success": True, "username": user.username})


@main.route("/api/auth/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True})


# ---------- Documents API ----------

@main.route("/api/documents/upload", methods=["POST"])
@login_required
def upload_document():
    if "file" not in request.files:
        return error_response("No file was uploaded", 400)

    file = request.files["file"]
    if file.filename == "":
        return error_response("No file was selected", 400)
    if not file.filename.lower().endswith(".pdf"):
        return error_response("Only PDF files are allowed", 400)

    file_bytes = file.read()

    try:
        text = extract_text_from_pdf(file_bytes)
    except PDFServiceError as e:
        return error_response(str(e), 400)

    filename = secure_filename(file.filename) or "document.pdf"

    document = Document(
        user_id=current_user.id,
        filename=filename,
        extracted_text=text,
    )
    db.session.add(document)
    db.session.commit()

    return jsonify({
        "success": True,
        "document_id": document.id,
        "filename": document.filename,
        "message": "PDF uploaded successfully",
    })


@main.route("/api/documents", methods=["GET"])
@login_required
def list_documents():
    documents = (
        Document.query.filter_by(user_id=current_user.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    result = []
    for doc in documents:
        result.append({
            "document_id": doc.id,
            "filename": doc.filename,
            "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d %H:%M"),
        })

    return jsonify({"success": True, "documents": result})


# ---------- Summary API ----------

@main.route("/api/summaries/generate", methods=["POST"])
@login_required
def summary_endpoint():
    data = request.get_json(silent=True) or {}
    document_id = data.get("document_id")

    if not isinstance(document_id, int) or isinstance(document_id, bool):
        return error_response("document_id is required", 400)

    # Only the owner's documents are found; anything else is 404
    document = Document.query.filter_by(
        id=document_id, user_id=current_user.id
    ).first()
    if document is None:
        return error_response("Document not found", 404)

    # Already generated before? Return the saved one.
    if document.summary:
        return jsonify({"success": True, "summary": document.summary})

    try:
        summary = generate_summary(document.extracted_text)
    except AIServiceError as e:
        return error_response(str(e), 502)

    document.summary = summary
    db.session.commit()

    return jsonify({"success": True, "summary": summary})


# ---------- Quiz API ----------

@main.route("/api/quizzes/generate", methods=["POST"])
@login_required
def quiz_generate_endpoint():
    data = request.get_json(silent=True) or {}
    document_id = data.get("document_id")
    num_questions = data.get("num_questions", 5)
    difficulty = data.get("difficulty", "medium")

    if not isinstance(document_id, int) or isinstance(document_id, bool):
        return error_response("document_id is required", 400)

    if (
        not isinstance(num_questions, int)
        or isinstance(num_questions, bool)
        or not 1 <= num_questions <= 20
    ):
        return error_response("num_questions must be a number from 1 to 20", 400)

    if difficulty not in ("easy", "medium", "hard"):
        return error_response("difficulty must be easy, medium or hard", 400)

    document = Document.query.filter_by(
        id=document_id, user_id=current_user.id
    ).first()
    if document is None:
        return error_response("Document not found", 404)

    try:
        questions = generate_quiz(document.extracted_text, num_questions, difficulty)
    except AIServiceError as e:
        return error_response(str(e), 502)

    quiz = Quiz(
        document_id=document.id,
        questions_json=json.dumps(questions),
        difficulty=difficulty,
    )
    db.session.add(quiz)
    db.session.commit()

    return jsonify({"success": True, "quiz_id": quiz.id, "questions": questions})


@main.route("/api/quizzes/<int:quiz_id>/submit", methods=["POST"])
@login_required
def quiz_submit_endpoint(quiz_id):
    data = request.get_json(silent=True) or {}
    answers = data.get("answers")

    if not isinstance(answers, list):
        return error_response("answers must be a list", 400)

    # Only quizzes whose document belongs to this user are found
    quiz = (
        Quiz.query.join(Document, Quiz.document_id == Document.id)
        .filter(Quiz.id == quiz_id, Document.user_id == current_user.id)
        .first()
    )
    if quiz is None:
        return error_response("Quiz not found", 404)

    questions = json.loads(quiz.questions_json)

    if len(answers) != len(questions):
        return error_response(
            f"Expected {len(questions)} answers, got {len(answers)}", 400
        )

    score = 0
    results = []
    for question, selected in zip(questions, answers):
        is_correct = selected == question["correct_answer"]
        if is_correct:
            score += 1
        results.append({
            "question": question["question"],
            "selected": selected,
            "correct_answer": question["correct_answer"],
            "is_correct": is_correct,
            "explanation": question["explanation"],
        })

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=current_user.id,
        score=score,
        total=len(questions),
    )
    db.session.add(attempt)
    db.session.commit()

    return jsonify({
        "success": True,
        "attempt_id": attempt.id,
        "score": score,
        "total": len(questions),
        "results": results,
    })


@main.route("/api/quizzes/history", methods=["GET"])
@login_required
def quiz_history_endpoint():
    rows = (
        db.session.query(QuizAttempt, Document.filename)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .join(Document, Quiz.document_id == Document.id)
        .filter(QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.taken_at.desc())
        .all()
    )

    attempts = []
    for attempt, filename in rows:
        attempts.append({
            "attempt_id": attempt.id,
            "quiz_id": attempt.quiz_id,
            "filename": filename,
            "score": attempt.score,
            "total": attempt.total,
            "taken_at": attempt.taken_at.strftime("%Y-%m-%d %H:%M"),
        })

    return jsonify({"success": True, "attempts": attempts})