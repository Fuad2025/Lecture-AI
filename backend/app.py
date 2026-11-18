import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, url_for
from flask_login import LoginManager

from backend.models import db, User
from backend.routes import main

# Project root = the Lecture-AI/ folder (one level above backend/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Read the .env file in the project root
load_dotenv(os.path.join(BASE_DIR, ".env"))

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    # Flask-Login calls this on every request to get the User from the session
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    # /api requests get JSON 401, page requests get sent to the login page
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Please log in first"}), 401
    return redirect(url_for("main.login_page"))


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
        static_folder=os.path.join(BASE_DIR, "frontend", "static"),
        instance_path=os.path.join(BASE_DIR, "instance"),
    )

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///lecture_ai.db"
    )

    # Make sure Lecture-AI/instance exists
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(main)

    # Create the tables if they don't exist yet
    with app.app_context():
        db.create_all()

    # TEMPORARY test route, we will remove it later
    @app.route("/api/health")
    def health():
        return jsonify({
            "success": True,
            "message": "Backend is running",
            "users": User.query.count(),
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)