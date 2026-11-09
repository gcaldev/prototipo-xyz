from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy import or_, select

from common.clock import display_date, now
from data.database import transaction
from data.models import Participation, Record, User
from service.services.access import rejection_reason
from service.services.audit import append
from service.services.outcomes import Outcome


def _denied(payload, operation, reason, number=""):
    append(
        payload.get("user") if isinstance(payload, dict) else "",
        number or (payload.get("number") if isinstance(payload, dict) else ""),
        operation,
        "denied",
        reason,
        payload.get("requestId") if isinstance(payload, dict) else "",
    )
    return Outcome(False, reason, {"result": "denied"})


def _active_read(db, username, number):
    today = now().date().isoformat()
    statement = (
        select(Participation.id)
        .join(User, Participation.user_id == User.id)
        .join(Record, Participation.record_id == Record.id)
        .where(
            User.username == username,
            Record.number == number,
            Participation.operation == "read",
            Participation.status == "active",
            or_(
                Participation.valid_until.is_(None),
                Participation.valid_until == "",
                Participation.valid_until >= today,
            ),
        )
    )
    return db.scalar(statement) is not None


def read_record(payload):
    reason = rejection_reason(payload, "read")
    if reason:
        return _denied(payload, "read", reason)
    number = (payload.get("number") or "").strip()
    with transaction() as db:
        record = db.scalar(select(Record).where(Record.number == number))
        if record is None or not _active_read(db, payload["user"], number):
            reason = "missing" if record is None else "no_participation"
            return _denied(payload, "read", reason, number)
        body = {
            "number": record.number,
            "createdOn": record.created_on,
            "owner": record.owner,
            "title": record.title,
            "body": record.body,
        }
    append(payload["user"], number, "read", "allowed", "active_participation", payload["requestId"])
    return Outcome(True, "active_participation", body)


def create_record(payload):
    reason = rejection_reason(payload, "create")
    if reason:
        return _denied(payload, "create", reason)
    title = (payload.get("title") or "").strip()
    text = (payload.get("body") or "").strip()
    if not title or not text:
        return _denied(payload, "create", "incomplete")
    with transaction() as db:
        user = db.scalar(select(User).where(User.username == payload["user"]))
        if user is None:
            return _denied(payload, "create", "unknown_user")
        numbers = []
        for current in db.scalars(select(Record.number)):
            suffix = current.split("-", 1)[1] if current.startswith("EXP-") else ""
            if suffix.isdigit():
                numbers.append(int(suffix))
        number = f"EXP-{(max(numbers) if numbers else 0) + 1}"
        record = Record(
            number=number,
            created_on=display_date(),
            title=title,
            body=text,
            owner=user.display_name,
        )
        db.add(record)
        db.flush()
        db.add(
            Participation(
                user_id=user.id,
                record_id=record.id,
                role="cliente",
                operation="read",
                status="active",
                valid_until=None,
            )
        )
        owner = user.display_name
    append(payload["user"], number, "create", "allowed", "record_created", payload["requestId"])
    return Outcome(True, "record_created", {"number": number, "owner": owner})


def revoke_participation(payload):
    reason = rejection_reason(payload, "revoke")
    if reason:
        return _denied(payload, "revoke", reason)
    number = (payload.get("number") or "").strip()
    with transaction() as db:
        rows = db.scalars(
            select(Participation)
            .join(User, Participation.user_id == User.id)
            .join(Record, Participation.record_id == Record.id)
            .where(
                User.username == payload["user"],
                Record.number == number,
                Participation.status == "active",
            )
        ).all()
        if not rows:
            return _denied(payload, "revoke", "no_participation", number)
        for row in rows:
            row.status = "revoked"
    append(payload["user"], number, "revoke", "allowed", "participation_revoked", payload["requestId"])
    return Outcome(True, "participation_revoked", {"result": "revoked"})


def authenticate(payload):
    reason = rejection_reason(payload, "login")
    if reason:
        return _denied(payload, "login", reason)
    username = (payload.get("user") or "").strip()
    password = payload.get("password") or ""
    with transaction() as db:
        user = db.scalar(select(User).where(User.username == username))
        password_hash = user.password_hash if user is not None else ""
        display_name = user.display_name if user is not None else ""
    if user is None:
        append(username, "", "login", "denied", "credentials", payload.get("requestId"))
        return Outcome(False, "credentials", {"result": "denied", "reason": "credentials"})
    try:
        PasswordHasher().verify(password_hash, password)
    except VerificationError:
        append(username, "", "login", "denied", "credentials", payload.get("requestId"))
        return Outcome(False, "credentials", {"result": "denied", "reason": "credentials"})
    append(username, "", "login", "allowed", "session_started", payload.get("requestId"))
    return Outcome(True, "session_started", {"result": "allowed", "displayName": display_name})
