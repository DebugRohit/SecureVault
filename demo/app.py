"""Flask entry point for the SecureVault recruiter demonstration."""

from __future__ import annotations

import os

from flask import Flask

from demo.api.routes import routes
from demo.config import DEBUG, HOST, PORT, STATIC_DIR, TEMPLATES_DIR


def create_app() -> Flask:
    """Create and configure the SecureVault demo application."""
    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_DIR),
        static_folder=str(STATIC_DIR),
        static_url_path="/static",
    )

    app.config.update(
        SECRET_KEY=os.environ.get(
            "SECUREVAULT_DEMO_SECRET",
            "securevault-recruiter-demo-local-only",
        ),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
    )

    app.register_blueprint(routes)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
    )