import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from common.config import SERVICE_URL
from common.context import signed_payload

PATHS = {
    "read": "/read",
    "create": "/register",
    "login": "/login",
}


def call(operation, user, **fields):
    payload = signed_payload(operation, user, **fields)
    request = Request(
        SERVICE_URL + PATHS[operation],
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw)
    except HTTPError as error:
        raw = error.read().decode("utf-8")
        try:
            return error.code, json.loads(raw)
        except json.JSONDecodeError:
            return error.code, {"result": "denied"}
    except (URLError, TimeoutError, json.JSONDecodeError):
        return 503, {"result": "denied"}
