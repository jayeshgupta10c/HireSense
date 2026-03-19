"""
app.py — HireSense AI  |  Flask application entry point
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from routes.resume_routes import resume_bp

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    # ── CORS (allow Angular dev server on :4200 and any localhost) ────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Register Blueprints ───────────────────────────────────────────────────
    app.register_blueprint(resume_bp)

    # ── Root ping ─────────────────────────────────────────────────────────────
    @app.get("/")
    def root():
        return {"message": "HireSense AI Backend — Running ✓"}, 200

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    print(f"\n🚀 HireSense AI Backend starting on http://localhost:{port}\n")
    application.run(host="0.0.0.0", port=port, debug=debug)