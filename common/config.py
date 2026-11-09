import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMEZONE = "America/Argentina/Buenos_Aires"
ISSUER = "sistema-z"
AUDIENCE = "servicio-expedientes"
CONTEXT_TTL_SECONDS = 60


def load_env():
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env()


def require_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Falta la variable de entorno {name}")
    return value


def resolve_path(name, default):
    value = os.environ.get(name, "").strip()
    path = Path(value) if value else ROOT / default
    if not path.is_absolute():
        path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


DATABASE_PATH = resolve_path("DATABASE_PATH", Path("data") / "sistemaz.db")
AUDIT_PATH = resolve_path("AUDIT_PATH", Path("data") / "audit.log")
SERVICE_URL = os.environ.get("SERVICE_URL", "http://127.0.0.1:5001").rstrip("/")
