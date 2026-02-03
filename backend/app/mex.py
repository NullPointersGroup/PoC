from sqlmodel import Session, select, col
from .models import Conversazione, Messaggio, RoleEnum

def create_conversation(session: Session) -> Conversazione:
    conv = Conversazione()
    session.add(conv)
    session.commit()
    session.refresh(conv)
    return conv

def get_messages(session: Session, conv_id: int):
    return session.exec(
        select(Messaggio)
        .where(Messaggio.conversazione_id == conv_id)
        .order_by(col(Messaggio.data_invio))
    ).all()

def add_message(session: Session, conv_id: int, ruolo: RoleEnum, testo: str) -> Messaggio:
    msg = Messaggio(conversazione_id=conv_id, ruolo=ruolo, testo=testo)
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg