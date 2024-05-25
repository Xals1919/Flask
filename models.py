import atexit
import datetime
import os
from sqlalchemy import create_engine, String, DateTime, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'secret')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'viktor')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'my_database')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5431')

PG_DNS = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_engine(PG_DNS)
Session = sessionmaker(bind=engine)

atexit.register(engine.dispose)


class Base(DeclarativeBase):
    pass


class Ticket(Base):
    __tablename__ = "ticket"

    id: Mapped[int] = mapped_column(primary_key=True)
    header: Mapped[str] = mapped_column(String(100), index=True, nullable=True)
    description: Mapped[str] = mapped_column(String(100), index=True, nullable=True)
    date_created: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    owner: Mapped[str] = mapped_column(String(100), index=True, nullable=True)

    @property
    def dictionary(self):
        return {
            "id": self.id,
            "header": self.header,
            "description": self.description,
            "date_created": self.date_created.isoformat(),
            "owner": self.owner
        }


Base.metadata.create_all(bind=engine)

