import os
from typing import Any, Generator, Sequence
from sqlmodel import create_engine, Session, select
from .models import *

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL non impostata")

engine = create_engine(DATABASE_URL, echo=True)

def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session

def get_all_users(session: Session) -> Sequence[Utente]:
    return session.exec(select(Utente)).all()

def get_all_anagrafica_cliente(session: Session) -> Sequence[AnagraficaCliente]:
    return session.exec(select(AnagraficaCliente).limit(3)).all()

def get_all_anagrafica_articolo(session: Session) -> Sequence[AnagraficaArticolo]:
    return session.exec(select(AnagraficaArticolo).limit(3)).all()

def get_all_ordes(session: Session) -> Sequence[Ordine]:
    return session.exec(select(Ordine).limit(3)).all()