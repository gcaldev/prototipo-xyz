import json

from common.clock import audit_timestamp
from common.config import AUDIT_PATH


def append(user, number, operation, result, reason, request_id):
    event = {
        "at": audit_timestamp(),
        "user": user or "",
        "number": number or "",
        "operation": operation,
        "result": result,
        "reason": reason,
        "requestId": request_id or "",
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
