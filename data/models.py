from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from data.database import Base


class User(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column("usuario", String, unique=True)
    display_name: Mapped[str] = mapped_column("nombre", String)
    password_hash: Mapped[str] = mapped_column("clave_hash", String)


class Record(Base):
    __tablename__ = "expediente"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column("numero", String, unique=True)
    created_on: Mapped[str] = mapped_column("fecha_creacion", String)
    title: Mapped[str] = mapped_column("titulo", String)
    body: Mapped[str] = mapped_column("cuerpo", String)
    owner: Mapped[str] = mapped_column("responsable", String)


class Participation(Base):
    __tablename__ = "participacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("usuario.id"))
    record_id: Mapped[int] = mapped_column("expediente_id", ForeignKey("expediente.id"))
    role: Mapped[str] = mapped_column("funcion", String)
    operation: Mapped[str] = mapped_column("operacion", String)
    status: Mapped[str] = mapped_column("estado", String)
    valid_until: Mapped[str | None] = mapped_column("vigencia", String, nullable=True)
