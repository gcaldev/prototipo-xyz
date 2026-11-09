from flask import Blueprint, render_template, request, session

from frontend.routes.guards import require_login
from frontend.services.gateway import call

bp = Blueprint("registration", __name__)


@bp.get("/registro_expediente")
def register():
    rejection = require_login()
    if rejection:
        return rejection
    return render_template("register.html", message="", error="")


@bp.post("/registro_expediente")
def register_submit():
    rejection = require_login()
    if rejection:
        return rejection
    title = (request.form.get("titulo") or "").strip()
    body = (request.form.get("cuerpo") or "").strip()
    if not title or not body:
        return render_template("register.html", message="", error="Complete título y cuerpo")
    status, payload = call("create", session["user"], title=title, body=body)
    if status == 200 and payload.get("number"):
        text = f"Se ha registrado el expediente. El codigo asignado es {payload['number']}"
        return render_template("register.html", message=text, error="")
    return render_template("register.html", message="", error="Acceso denegado")
