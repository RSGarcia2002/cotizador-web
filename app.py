from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask import abort, request, session
from flask_login import LoginManager
from db import init_pool
from init_db import init_db
from routes.main import bp as main_bp
from routes.auth import bp as auth_bp
from services.auth_service import cargar_usuario
import os
import secrets


def create_app():
    app = Flask(__name__)
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY es obligatorio en variables de entorno.")
    app.secret_key = secret_key

    app.config["UPLOAD_FOLDER_ORDENES"] = os.path.join(os.getcwd(), "uploads", "ordenes")
    app.config["UPLOAD_FOLDER_FACTURAS"] = os.path.join(os.getcwd(), "uploads", "facturas")

    os.makedirs(app.config["UPLOAD_FOLDER_ORDENES"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER_FACTURAS"], exist_ok=True)

    init_pool()
    init_db()

    # Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesión para acceder."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return cargar_usuario(user_id)

    def _get_csrf_token() -> str:
        token = session.get("_csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return token

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": _get_csrf_token()}

    @app.before_request
    def csrf_protect():
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        token = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
        expected = session.get("_csrf_token")
        if not token or not expected or not secrets.compare_digest(token, expected):
            abort(400, description="CSRF token inválido o ausente.")

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
