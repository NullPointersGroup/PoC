from fastapi import FastAPI
from beartype import beartype

app = FastAPI()

@beartype
@app.get("/")
def root() -> dict[str, str]:
    return {"hello": "world"}
