from flask import Flask

from common.config import require_env
from frontend.routes.auth import bp as auth_bp
from frontend.routes.registration import bp as registration_bp
from frontend.routes.search import bp as search_bp


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = require_env("SESION_SECRETO")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.register_blueprint(auth_bp, url_prefix="/SistemaZ")
    app.register_blueprint(search_bp, url_prefix="/SistemaZ")
    app.register_blueprint(registration_bp, url_prefix="/SistemaZ")
    return app
