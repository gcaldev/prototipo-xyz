from flask import Blueprint, redirect, render_template, request, session, url_for

from frontend.services.gateway import call

bp = Blueprint("web", __name__)


@bp.get("/")
@bp.get("")
def home():
    if session.get("user"):
        return redirect(url_for("search.search"))
    return redirect(url_for("web.login"))


@bp.get("/login")
def login():
    if session.get("user"):
        return redirect(url_for("search.search"))
    return render_template("login.html", message="")


@bp.post("/login")
def login_submit():
    username = (request.form.get("usuario") or "").strip()
    password = request.form.get("clave") or ""
    status, payload = call("login", username, password=password)
    if status == 200 and payload.get("result") == "allowed":
        session["user"] = username
        session["name"] = payload.get("displayName") or username
        return redirect(url_for("search.search"))
    if payload.get("reason") == "credentials":
        return render_template("login.html", message="Usuario o clave incorrectos")
    return render_template("login.html", message="No se pudo completar el ingreso")


@bp.get("/salir")
def logout():
    session.clear()
    return redirect(url_for("web.login"))
