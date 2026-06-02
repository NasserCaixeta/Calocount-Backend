from app.db.base import Base
from app.db.session import engine

import app.models.user  # noqa: F401
import app.models.calorie_log  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
