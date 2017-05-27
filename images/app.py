from flask import Flask

from src.controller import bp as api_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
