from sqlmodel import Session, select, col
from .models import Conversazioni, Messaggi, RoleEnum
from typing import Any

def create_conversation(session: Session) -> Conversazioni:
    conv = Conversazioni()
    session.add(conv)
    session.commit()
    session.refresh(conv)
    return conv

def get_messages(session: Session, conv_id: int) -> Any:
    return session.exec(
        select(Messaggi)
        .where(Messaggi.conversazione_id == conv_id)
        .order_by(col(Messaggi.data_invio))
    ).all()

def add_message(session: Session, conv_id: int, ruolo: RoleEnum, testo: str) -> Messaggi:
    msg = Messaggi(conversazione_id=conv_id, ruolo=ruolo, testo=testo)
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg