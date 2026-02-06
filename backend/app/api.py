from fastapi import FastAPI, Depends, HTTPException, Path, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AfterValidator
from .database import *
from .schemas import *
from typing import Annotated, Sequence, Any, Dict
from sqlmodel import Session, select, delete
from .mex import create_conversation, get_messages, add_message
from .cart import router as cart_router
from .AI import invoke_cart_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cart_router)


def get_global_conversation(session: Session) -> int:
    conv = session.exec(select(Conversazioni).limit(1)).first()
    if conv is None:
        conv = create_conversation(session)
    return conv.id


@app.post("/chat", response_model=ChatReply)
def chat(req: ChatRequest, session: SessionDep) -> ChatReply:
    conv_id = req.conv_id or get_global_conversation(session)

    add_message(session, conv_id, RoleEnum.user, req.message)
    reply = f"Hai scritto: {req.message}"
    add_message(session, conv_id, RoleEnum.assistant, reply)

    return ChatReply(reply=reply, conv_id=conv_id)


@app.post("/conversazioni/1/messaggi")
def send_message(
    payload: MessagePayload, session: SessionDep ) -> Dict[str, str]:
    testo = payload.testo
    if not testo:
        return {"reply": "Messaggio vuoto"}

    # Salva messaggio utente
    add_message(session, conv_id=1, ruolo=RoleEnum.user, testo=testo)

    # Genera risposta semplice dell'assistente
    reply = f"Hai scritto: {testo}"
    add_message(session, conv_id=1, ruolo=RoleEnum.assistant, testo=reply)

    return {"reply": reply}

@app.delete("/conversazioni/{conv_id}")
def delete_conversation(
    conv_id: int, session: SessionDep) -> dict[str, str]:
    session.exec(delete(Messaggi).where(Messaggi.conversazione_id == conv_id))  # type: ignore
    session.commit()
    return {
        "status": "ok",
        "message": f"Messaggi della conversazione {conv_id} eliminati",
    }

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


@app.get(
    "/anagrafica/{tipo}",
    response_model=list[AnagraficaCliente] | list[AnagraficaArticoloOut],
)
def get_anagrafica(
    tipo: Annotated[
        str, Path(min_length=7, max_length=8), AfterValidator(valida_tipo_anagrafica)
    ],
    session: SessionDep,
) -> Sequence[AnagraficaCliente] | Sequence[AnagraficaArticolo]:
    if tipo.lower() == "cliente":
        print("SONO QUIII")
        return get_all_anagrafica_cliente(session)
    return get_all_anagrafica_articolo(session)


@app.get("/ordini")
def get_ordini(session: SessionDep) -> Sequence[Ordine]:
    return get_all_ordes(session)


@app.post("/conversazioni")
def new_conversation(session: SessionDep) -> dict[str, int]:
    conv = create_conversation(session)
    return {"id": conv.id}


@app.get("/conversazioni/{conv_id}/messaggi", response_model=list[MessaggioOut])
def read_messages(conv_id: int, session: SessionDep) -> Any:
    return get_messages(session, conv_id)


@app.get("/ai")
def query_ai(message: str) -> dict[str, Any] | Any:
    risposta = invoke_cart_agent(message)
    return risposta["messages"][-1]

