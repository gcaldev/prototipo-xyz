from flask import Blueprint, jsonify, request

from service.services.records import create_record

bp = Blueprint("registration", __name__)


@bp.post("/register")
def register():
    outcome = create_record(request.get_json(silent=True) or {})
    return jsonify(outcome.payload), 200 if outcome.allowed else 403
