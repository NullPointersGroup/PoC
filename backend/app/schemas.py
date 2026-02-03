from pydantic import BaseModel

class UserOut(BaseModel):
    username: str
    cod_utente: int

class AnagraficaArticoloOut(BaseModel):
    cod_art: str
    des_art: str