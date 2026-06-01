from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.doctor import Doctor  # noqa: E402,F401
