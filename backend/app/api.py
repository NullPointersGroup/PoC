from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware;
from .database import get_session, get_all_users
from .schemas import UserOut
from typing import Annotated, Sequence
from sqlmodel import Session
from .models import Utente

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root() -> dict[str, str]:
    return {"hello": "world"}

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/users", response_model=list[UserOut])
def users(session: SessionDep) -> Sequence[Utente]: 
   return get_all_users(session) 