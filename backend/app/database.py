from sqlmodel import create_engine, Session, select
from .models import Utente

# Prendi l'URL dal docker-compose environment
DATABASE_URL = "postgresql://user:password@db:5432/mydb"

engine = create_engine(DATABASE_URL, echo=True)

# Funzione per ottenere una sessione
def get_session():
    with Session(engine) as session:
        yield session

def get_all_users(session: Session):
    return session.exec(select(Utente)).all()