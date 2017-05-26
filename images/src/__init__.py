from flask import Flask

from .controller import bp as api_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app


app = create_app()
