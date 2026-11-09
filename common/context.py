import hashlib
import hmac
import uuid
from datetime import timedelta

from common.clock import now
from common.config import AUDIENCE, CONTEXT_TTL_SECONDS, ISSUER, require_env

FIELDS = (
    "user",
    "issuer",
    "audience",
    "expiresAt",
    "requestId",
    "operation",
    "number",
    "title",
    "body",
    "result",
    "reason",
    "password",
)


def canonical(payload):
    return "\n".join(f"{field}={payload.get(field) or ''}" for field in FIELDS)


def sign(payload, secret):
    return hmac.new(
        secret.encode("utf-8"),
        canonical(payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def signature_valid(payload, secret):
    received = payload.get("signature") or ""
    return hmac.compare_digest(received, sign(payload, secret))


def expired(expires_at):
    from datetime import datetime

    try:
        limit = datetime.fromisoformat(expires_at)
    except (TypeError, ValueError):
        return True
    if limit.tzinfo is None:
        return True
    return datetime.now(limit.tzinfo) >= limit


def signed_payload(operation, user, **fields):
    payload = {
        "user": user,
        "issuer": ISSUER,
        "audience": AUDIENCE,
        "expiresAt": (now() + timedelta(seconds=CONTEXT_TTL_SECONDS)).isoformat(),
        "requestId": uuid.uuid4().hex[:8],
        "operation": operation,
        "number": fields.get("number", ""),
        "title": fields.get("title", ""),
        "body": fields.get("body", ""),
        "result": fields.get("result", ""),
        "reason": fields.get("reason", ""),
        "password": fields.get("password", ""),
    }
    payload["signature"] = sign(payload, require_env("CONTEXTO_SECRETO"))
    return payload
