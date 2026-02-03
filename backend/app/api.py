from fastapi import FastAPI, Depends, Path
from fastapi.middleware.cors import CORSMiddleware;
from pydantic import AfterValidator
from .database import *
from .schemas import *
from typing import Annotated, Sequence, Any
from sqlmodel import Session

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/ai/{info}")
def print_ai(info: str, session: SessionDep) -> Any: 
    if info =="utenti":
      return get_all_users(session) 
    if info =="articoli":
        return get_all_anagrafica_articolo(session)
    return {"response": "Errore, non è possibile ottenere le info"}


@app.get("/")
def root() -> dict[str, str]:
    return {"hello": "world"}


@app.get("/users", response_model=list[UserOut])
def users(session: SessionDep) -> Sequence[Utente]: 
   return get_all_users(session) 

def valida_tipo_anagrafica(tipo: str) -> str:
    tipo = tipo.lower()
    if tipo != "cliente" and tipo != "articolo":
        raise ValueError("Tipo di anagrafica non supportato")
    return tipo

@app.get("/anagrafica/{tipo}", response_model=list[AnagraficaArticoloOut])
def get_anagrafica(tipo: Annotated[str, Path(min_length=7, max_length=8), AfterValidator(valida_tipo_anagrafica)], session: SessionDep)-> Sequence[AnagraficaCliente] | Sequence[AnagraficaArticolo]:
    if tipo.lower() == "cliente":
        return get_all_anagrafica_cliente(session)
    return get_all_anagrafica_articolo(session)

@app.get("/ordini")
def get_ordini(session: SessionDep) -> Sequence[Ordine]:
    return get_all_ordes(session)