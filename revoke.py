import json
import sys
from urllib.request import Request, urlopen

from common.config import SERVICE_URL
from common.context import signed_payload


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python revoke.py <usuario> <numero>")
    username, number = sys.argv[1:]
    payload = signed_payload("revoke", username, number=number)
    request = Request(
        SERVICE_URL + "/revoke",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        print(response.read().decode("utf-8"))


if __name__ == "__main__":
    main()
