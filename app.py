from flask import Flask
from db import init_pool
from init_db import init_db
from routes.main import bp as main_bp
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = "clave_temporal_123"

    app.config["UPLOAD_FOLDER_ORDENES"] = os.path.join(os.getcwd(), "uploads", "ordenes")
    app.config["UPLOAD_FOLDER_FACTURAS"] = os.path.join(os.getcwd(), "uploads", "facturas")

    os.makedirs(app.config["UPLOAD_FOLDER_ORDENES"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER_FACTURAS"], exist_ok=True)

    init_pool()
    init_db()

    app.register_blueprint(main_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)