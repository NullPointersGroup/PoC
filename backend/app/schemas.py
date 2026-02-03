from pydantic import BaseModel

class UserOut(BaseModel):
    username: str
    cod_utente: int