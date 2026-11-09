from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from common.config import DATABASE_PATH


class Base(DeclarativeBase):
    pass


engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)
Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def transaction():
    db = Session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
