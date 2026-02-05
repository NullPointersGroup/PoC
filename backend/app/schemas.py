from pydantic import BaseModel
from .models import RoleEnum
from sqlmodel import Session
from fastapi import Depends
from typing import Annotated
from .database import get_session

SessionDep = Annotated[Session, Depends(get_session)]

class UserOut(BaseModel):
    username: str
    cod_utente: int

class MessaggioOut(BaseModel):
   ruolo: RoleEnum
   testo: str

class AnagraficaArticoloOut(BaseModel):
    cod_art: str
    des_art: str


class ChatRequest(BaseModel):
    message: str
    conv_id: int | None = None

class ChatReply(BaseModel):
    reply: str
    conv_id: int

class MessagePayload(BaseModel):
    testo: str


class UpdateQuantityRequest(BaseModel):
    quantita: int


class CartAddRequest(BaseModel):
    conversation_id: int
    product_id: str
    name: str
    qty: int
    price: float