from argon2 import PasswordHasher

from common.config import AUDIT_PATH, require_env
from data.database import Base, engine, transaction
from data.models import Participation, Record, User

HASHER = PasswordHasher()


def main():
    pedro_password = require_env("SEMILLA_PEDRO_CLAVE")
    vgomez_password = require_env("SEMILLA_VGOMEZ_CLAVE")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    AUDIT_PATH.write_text("", encoding="utf-8")
    with transaction() as db:
        pedro = User(username="pedro", display_name="Pedro Gomez", password_hash=HASHER.hash(pedro_password))
        vgomez = User(username="vgomez", display_name="Victor Gomez", password_hash=HASHER.hash(vgomez_password))
        record = Record(
            number="EXP-13",
            created_on="08-11-2026",
            title="soadf",
            body="oadsfso",
            owner="Pedro Gomez",
        )
        db.add_all([pedro, vgomez, record])
        db.flush()
        db.add(
            Participation(
                user_id=pedro.id,
                record_id=record.id,
                role="cliente",
                operation="read",
                status="active",
                valid_until=None,
            )
        )
    print("Semilla cargada: pedro participa en EXP-13; vgomez no.")


if __name__ == "__main__":
    main()
