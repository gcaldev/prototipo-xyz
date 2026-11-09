from flask import Blueprint, jsonify, request

from service.services.records import read_record

bp = Blueprint("read", __name__)


@bp.post("/read")
def read():
    outcome = read_record(request.get_json(silent=True) or {})
    return jsonify(outcome.payload), 200 if outcome.allowed else 403
