from flask import Blueprint, jsonify, request

from service.services.records import revoke_participation

bp = Blueprint("revocation", __name__)


@bp.post("/revoke")
def revoke():
    outcome = revoke_participation(request.get_json(silent=True) or {})
    return jsonify(outcome.payload), 200 if outcome.allowed else 403
