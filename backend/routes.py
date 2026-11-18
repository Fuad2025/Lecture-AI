from flask import Blueprint, jsonify, redirect, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from backend.models import db, User

# A Blueprint is just a group of routes. app.py plugs it into the app.
main = Blueprint("main", __name__)


# ---------- Helper for error JSON ----------

def error_response(message, status_code):
    return jsonify({"success": False, "error": message}), status_code


# ---------- Page routes ----------
# TEMPORARY placeholders. When Peter's templates are ready, replace each
# return line with: return render_template("login.html")  (etc.)

@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard_page"))
    return redirect(url_for("main.login_page"))


@main.route("/login")
def login_page():
    return "<h1>Login page (placeholder)</h1>"


@main.route("/register")
def register_page():
    return "<h1>Register page (placeholder)</h1>"


@main.route("/dashboard")
@login_required
def dashboard_page():
    return "<h1>Dashboard (placeholder)</h1>"


@main.route("/study/<int:document_id>")
@login_required
def study_page(document_id):
    return f"<h1>Study page for document {document_id} (placeholder)</h1>"


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