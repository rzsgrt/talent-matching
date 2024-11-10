from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError


class Database:
    def __init__(
        self,
        user,
        password,
        host,
        port,
        db,
    ):

        self.engine = create_engine(
            f"postgresql://{user}:{password}@{host}:{port}/{db}",
            echo=True,  # Set to False in production
        )
        try:
            with self.engine.connect() as conn:
                pass
            self.SessionLocal = sessionmaker(bind=self.engine)
        except SQLAlchemyError as e:
            print(f"Database connection error. Error details: {str(e)}")

    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
