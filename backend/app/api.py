from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware;
from .database import get_session, get_all_users
from .models import Utente
from typing import Annotated
from sqlmodel import Session

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

@app.get("/users")
def users(session: SessionDep): 
   return get_all_users(session) 