from flask import Flask

from common.config import require_env
from service.routes.login_event import bp as login_event_bp
from service.routes.read import bp as read_bp
from service.routes.registration import bp as registration_bp
from service.routes.revocation import bp as revocation_bp


def create_app():
    require_env("CONTEXTO_SECRETO")
    app = Flask(__name__)
    app.register_blueprint(read_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(revocation_bp)
    app.register_blueprint(login_event_bp)
    return app
