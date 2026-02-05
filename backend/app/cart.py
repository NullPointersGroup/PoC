from fastapi import APIRouter, status, HTTPException
from typing import Any, Dict
from .api import SessionDep
from .database import *
from .schemas import UpdateQuantityRequest, CartAddRequest

router = APIRouter(prefix="/cart", tags=["cart"])

# In-memory carts keyed by conversation_id
_CARTS: Dict[int, Dict[str, Dict[str, Any]]] = {}


def _build_cart_response(items_by_id: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    items = list(items_by_id.values())
    total_items = sum(item["qty"] for item in items)
    total_price = round(sum(item["qty"] * item["price"] for item in items), 2)
    return {
        "items": items,
        "total_items": total_items,
        "total_price": total_price,
    }


@router.post("/add")
def add_to_cart(payload: CartAddRequest) -> Dict[str, Any]:
    cart_items = _CARTS.setdefault(payload.conversation_id, {})

    if payload.product_id in cart_items:
        cart_items[payload.product_id]["qty"] += payload.qty
    else:
        cart_items[payload.product_id] = {
            "product_id": payload.product_id,
            "name": payload.name,
            "qty": payload.qty,
            "price": payload.price,
        }

    cart_summary = _build_cart_response(cart_items)
    return {
        "ok": True,
        "message": f"Aggiunto: {payload.name} x{payload.qty}",
        "cart": cart_summary,
    }


@router.get("/{user}/cart")
def get_user_cart(user: str, session: SessionDep) -> Any:
    carrello = get_cart(session, user)
    if not carrello:
        return []
    return carrello

@router.delete("/{user}/cart/{cod_art}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_article(user: str, cod_art: str, session: SessionDep) -> None:
    removed = remove_from_cart(session, user, cod_art)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Articolo {cod_art} non trovato nel carrello dell'utente {user}",
        )


@router.delete("/{user}/cart", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(user: str, session: SessionDep) -> None:
    clear_user_cart(session, user)


@router.put("/{user}/cart/{cod_art}")
def update_quantity(
    user: str, cod_art: str, update: UpdateQuantityRequest, session: SessionDep
) -> Any:
    if update.quantita <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La quantità deve essere maggiore di zero",
        )
    updated = update_cart_quantity(session, user, cod_art, update.quantita)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Articolo {cod_art} non trovato nel carrello dell'utente {user}",
        )