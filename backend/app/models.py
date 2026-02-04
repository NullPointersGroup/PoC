from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import date, datetime, timezone
from typing import ClassVar, Optional


class AnagraficaCliente(SQLModel, table=True):
    __tablename__: ClassVar[str] = "anacli"
    cod_cli: int = Field(default=None, primary_key=True)
    rag_soc: str = Field(default=None, max_length=255)


class Utente(SQLModel, table=True):
    __tablename__: ClassVar[str] = "utentiweb"
    username: str = Field(default=None, max_length=255, primary_key=True)
    descrizione: str = Field(default=None, max_length=80)
    password: str = Field(default=None, max_length=60)
    cod_utente: int = Field(default=None, foreign_key="anacli.cod_cli")


class Ordine(SQLModel, table=True):
    __tablename__: ClassVar[str] = "ordclidet"
    id: int = Field(default=None, primary_key=True)
    cod_cli: int = Field(default=None, foreign_key="anacli.cod_cli")
    cod_art: str = Field(default=None, max_length=13, foreign_key="anaart.cod_art")
    data_ord: date = Field(default=None)
    qta_ordinata: int = Field(default=None)
    rif: str = Field(default=None)


class AnagraficaArticolo(SQLModel, table=True):
    __tablename__: ClassVar[str] = "anaart"
    cod_art: str = Field(default=None, max_length=13, primary_key=True)
    des_art: str = Field(default=None, max_length=255)
    des_um: str = Field(default=None, max_length=40)
    tipo_um: str = Field(default=None, max_length=1)
    des_tipo_um: str = Field(default=None, max_length=20)
    peso_netto_conf: float = Field(default=None)
    conf_collo: float = Field(default=None)
    pezzi_conf: int = Field(default=None)


class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"


class Conversazioni(SQLModel, table=True):
    __tablename__: ClassVar[str] = "conversazioni"
    id: int = Field(default=None, primary_key=True)
    data_creazione: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Messaggi(SQLModel, table=True):
    __tablename__: ClassVar[str] = "messaggi"
    id: int = Field(default=None, primary_key=True)
    conversazione_id: int = Field(foreign_key="conversazioni.id")
    ruolo: RoleEnum
    testo: str
    data_invio: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Carrello(SQLModel, table=True):
    __tablename__: ClassVar[str] = "carrello"
    utente: str = Field(foreign_key="utentiweb.username", primary_key=True)
    prodotto: str = Field(foreign_key="anaart.cod_art", primary_key=True)
    quantita: int


class CarrelloDTO(SQLModel):
    prodotto: str
    quantita: int
    des_art: Optional[str] = None

