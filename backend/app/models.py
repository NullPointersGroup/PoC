from sqlmodel import SQLModel, Field, table
from datetime import date

class AnagraficaCliente(SQLModel, table = True):
    __tablename__="anacli"
    cod_cli: int = Field(default=None, primary_key=True)
    rag_soc: str = Field(default=None,max_length = 255)

class Utente(SQLModel, table=True):
    __tablename__="utentiweb"
    username: str = Field(default=None, max_length = 255, primary_key=True)
    descrizione: str = Field(default=None, max_length = 80)
    password: str = Field(default=None, max_length = 60)
    cod_utente: int = Field(default=None, foreign_key = "anacli.cod_cli")

class Ordine(SQLModel, table=True):
    __tablename__="ordclidet"
    id:int = Field(default=None, primary_key=True)
    cod_cli:int = Field(default=None, foreign_key="anacli.cod_cli")
    cod_art: str = Field(default=None, max_length=13, foreign_key="anaart.cod_art")
    data_ord: date = Field(default=None)
    qta_ordinata: int = Field(default=None)
    rif: str = Field(default=None)

class AnagraficaArticolo(SQLModel, table=True):
    __tablename__="anaart"
    cod_art: str = Field(default=None, max_length=13, primary_key=True)
    des_art: str = Field(default=None, max_length=255)
    des_um: str = Field(default=None,max_length=40)
    tipo_um: str = Field(default=None, max_length=1)
    des_tipo_um: str = Field(default=None, max_length=20)
    peso_netto_conf: float = Field(default=None)
    conf_collo: float = Field(default=None)
    pezzi_conf: int = Field(default=None)