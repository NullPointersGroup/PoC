from pydantic import BaseModel
from .models import RoleEnum

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