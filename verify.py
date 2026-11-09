import json
import sys
import uuid
from datetime import timedelta
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

from common.clock import now
from common.config import AUDIT_PATH, require_env
from common.context import sign

BASE = "http://127.0.0.1:5000"
SERVICE = "http://127.0.0.1:5001"


def opener():
    return build_opener(HTTPCookieProcessor(CookieJar()))


def request(client, path, form=None):
    body = None if form is None else urlencode(form).encode()
    call = Request(BASE + path, data=body, method="POST" if form is not None else "GET")
    if body is not None:
        call.add_header("Content-Type", "application/x-www-form-urlencoded")
    with client.open(call, timeout=5) as response:
        return response.status, response.read().decode("utf-8")


def direct(payload):
    call = Request(
        SERVICE + "/read",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(call, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as error:
        return error.code, error.read().decode("utf-8")


def login(client, username, password):
    status, html = request(client, "/SistemaZ/login", {"usuario": username, "clave": password})
    if status != 200 or "Código de expediente" not in html:
        raise SystemExit(f"No entró {username}")


def check(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    pedro_password = require_env("SEMILLA_PEDRO_CLAVE")
    vgomez_password = require_env("SEMILLA_VGOMEZ_CLAVE")
    client = opener()
    login(client, "pedro", pedro_password)
    _, html = request(client, "/SistemaZ/busqueda_expediente", {"codigoExpediente": "EXP-13"})
    check("soadf" in html and "Pedro Gomez" in html and "08-11-2026" in html, "pedro no vio EXP-13")

    client = opener()
    login(client, "vgomez", vgomez_password)
    _, html = request(client, "/SistemaZ/busqueda_expediente", {"codigoExpediente": "EXP-13"})
    check("Acceso denegado" in html and "soadf" not in html and "Pedro Gomez" not in html, "vgomez vio datos de EXP-13")

    client = opener()
    login(client, "pedro", pedro_password)
    _, html = request(client, "/SistemaZ/registro_expediente", {"titulo": "Contrato", "cuerpo": "Texto"})
    check("Se ha registrado el expediente. El codigo asignado es EXP-14" in html, "no se registró EXP-14")
    _, html = request(client, "/SistemaZ/busqueda_expediente", {"codigoExpediente": "EXP-14"})
    check("Contrato" in html and "Texto" in html, "pedro no leyó su alta")
    client = opener()
    login(client, "vgomez", vgomez_password)
    _, html = request(client, "/SistemaZ/busqueda_expediente", {"codigoExpediente": "EXP-14"})
    check("Acceso denegado" in html and "Contrato" not in html, "vgomez leyó el alta de pedro")

    status, body = direct({"number": "EXP-13"})
    check(status == 403 and "soadf" not in body and "denied" in body, "la llamada directa devolvió datos")
    forged = {
        "user": "pedro",
        "issuer": "sistema-z",
        "audience": "servicio-expedientes",
        "expiresAt": (now() + timedelta(seconds=60)).isoformat(),
        "requestId": uuid.uuid4().hex[:8],
        "operation": "read",
        "number": "EXP-13",
        "title": "",
        "body": "",
        "result": "",
        "reason": "",
    }
    signature = sign(forged, require_env("CONTEXTO_SECRETO"))
    forged["signature"] = ("0" if signature[0] != "0" else "1") + signature[1:]
    status, body = direct(forged)
    check(status == 403 and "soadf" not in body, "una firma alterada fue aceptada")
    stale = dict(forged)
    stale["expiresAt"] = (now() - timedelta(seconds=120)).isoformat()
    stale["signature"] = sign(stale, require_env("CONTEXTO_SECRETO"))
    status, body = direct(stale)
    check(status == 403 and "soadf" not in body, "un contexto vencido fue aceptado")

    from revoke import main as revoke

    sys.argv = ["revoke.py", "pedro", "EXP-13"]
    revoke()
    client = opener()
    login(client, "pedro", pedro_password)
    _, html = request(client, "/SistemaZ/busqueda_expediente", {"codigoExpediente": "EXP-13"})
    check("Acceso denegado" in html and "soadf" not in html, "la revocación no cortó la lectura")
    text = AUDIT_PATH.read_text(encoding="utf-8")
    check('"operation": "read"' in text and '"result": "allowed"' in text, "falta una lectura permitida")
    check('"result": "denied"' in text, "falta una lectura denegada")
    check('"operation": "revoke"' in text, "falta la revocación")
    check("soadf" not in text and "oadsfso" not in text and "Contrato" not in text and "Texto" not in text, "la auditoría guardó contenido del expediente")
    print("Los cinco casos pasaron.")


if __name__ == "__main__":
    main()
