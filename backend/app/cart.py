from fastapi import APIRouter, status, HTTPException
from typing import Sequence
from .schemas import SessionDep
from .database import get_cart, remove_from_cart
from .models import CarrelloDTO
from .AI import invoke_cart_agent

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("", response_model=list[CarrelloDTO])
def list_cart(session: SessionDep) -> Sequence[CarrelloDTO]:
    return get_cart(session)


@router.delete("/{cod_art}", status_code=status.HTTP_200_OK)
def delete_cart_item(cod_art: str, session: SessionDep) -> dict[str, str]:
    removed = remove_from_cart(session, cod_art)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return {"status": "ok"}

@router.get("/{user}")
def query_cart_agent(user: str, message: str) -> Dict[str, Any] | Any:
    return invoke_cart_agent(message)["messages"][-1].content
