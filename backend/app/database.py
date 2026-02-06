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


def get_cart(session: Session) -> Sequence[CarrelloDTO]:
    statement = (
        select(Carrello.prodotto, Carrello.quantita, AnagraficaArticolo.des_art)
        .select_from(Carrello)
        .join(AnagraficaArticolo)
        .where(Carrello.prodotto == AnagraficaArticolo.cod_art)
    )
    results = session.exec(statement).all()

    return [
        CarrelloDTO(prodotto=prodotto, quantita=quantita, des_art=des_art)
        for prodotto, quantita, des_art in results
    ]


def remove_from_cart(session: Session, cod_art: str) -> bool:
    statement = select(Carrello).where(Carrello.prodotto == cod_art)
    carrello_item = session.exec(statement).first()

    if carrello_item:
        session.delete(carrello_item)
        session.commit()
        return True
    return False


def clear_cart(session: Session) -> None:
    statement = select(Carrello)
    items = session.exec(statement).all()

    for item in items:
        session.delete(item)
    session.commit()


def update_cart_quantity(session: Session, cod_art: str, quantita: int) -> bool:
    statement = select(Carrello).where(Carrello.prodotto == cod_art)
    item = session.exec(statement).first()

    if item:
        item.quantita = quantita
        session.commit()
        return True
    return False
