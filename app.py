from flask import Flask
from db import init_pool
from init_db import init_db, seed_db
from routes.main import bp as main_bp


def create_app():
    app = Flask(__name__)
    init_pool()
    init_db()
    seed_db()
    app.register_blueprint(main_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
