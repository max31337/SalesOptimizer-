from contextlib import contextmanager
from typing import Callable
from sqlalchemy.orm import Session
from fastapi import HTTPException

class UnitOfWork:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    @contextmanager
    def start(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            session.close()

    @contextmanager
    def start_nested(self):
        session = self.session_factory()
        try:
            with session.begin_nested():
                yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            session.close()