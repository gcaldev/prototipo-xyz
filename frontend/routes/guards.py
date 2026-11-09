from flask import redirect, session, url_for


def require_login():
    if not session.get("user"):
        return redirect(url_for("web.login"))
    return None
