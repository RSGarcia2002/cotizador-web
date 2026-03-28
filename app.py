from flask import Flask
from flask_login import LoginManager
from db import init_pool
from init_db import init_db
from routes.main import bp as main_bp
from routes.auth import bp as auth_bp
from services.auth_service import cargar_usuario
from dotenv import load_dotenv
load_dotenv()
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "clave_temporal_123")

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

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)