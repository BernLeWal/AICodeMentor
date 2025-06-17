"""
Very small UI layer (Bootstrap + JS) to browse /api/files.
"""
from flask import Blueprint, render_template

frontend_bp = Blueprint("frontend", __name__, template_folder="../web/templates")

@frontend_bp.route("/files", methods=["GET"])
def files_page():
    """Render HTML container – JS inside fetches /api/files dynamically."""
    return render_template("files.html")

@frontend_bp.route("/history", methods=["GET"])
def history_page():
    """Render HTML container – JS inside fetches /api/log dynamically."""
    return render_template("history.html")


def register_frontend_routes(app):
    """Register the frontend routes with the Flask application."""
    app.register_blueprint(frontend_bp)
