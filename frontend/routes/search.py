from flask import Blueprint, render_template, request, session

from frontend.routes.guards import require_login
from frontend.services.gateway import call

bp = Blueprint("search", __name__)


@bp.get("/busqueda_expediente")
def search():
    rejection = require_login()
    if rejection:
        return rejection
    return render_template("search.html", record=None, message="")


@bp.post("/busqueda_expediente")
def search_submit():
    rejection = require_login()
    if rejection:
        return rejection
    number = (request.form.get("codigoExpediente") or "").strip()
    status, payload = call("read", session["user"], number=number)
    if status == 200 and payload.get("number"):
        return render_template("search.html", record=payload, message="")
    return render_template("search.html", record=None, message="Acceso denegado")
