from common.config import AUDIENCE, ISSUER, require_env
from common.context import expired, signature_valid


def rejection_reason(payload, operation):
    if not isinstance(payload, dict) or not payload.get("signature"):
        return "missing_context"
    if payload.get("operation") != operation:
        return "operation_mismatch"
    if payload.get("issuer") != ISSUER:
        return "issuer_not_allowed"
    if payload.get("audience") != AUDIENCE:
        return "invalid_audience"
    if not signature_valid(payload, require_env("CONTEXTO_SECRETO")):
        return "invalid_signature"
    if expired(payload.get("expiresAt")):
        return "expired_context"
    if not payload.get("user"):
        return "missing_user"
    return None
