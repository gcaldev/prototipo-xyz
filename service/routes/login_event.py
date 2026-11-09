from flask import Blueprint, jsonify, request

from service.services.records import authenticate

bp = Blueprint("login_event", __name__)


@bp.post("/login")
def login_event():
    outcome = authenticate(request.get_json(silent=True) or {})
    return jsonify(outcome.payload), 200 if outcome.allowed else 403
