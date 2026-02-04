from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict

router = APIRouter(prefix="/cart", tags=["cart"])


class CartAddRequest(BaseModel):
    conversation_id: int
    product_id: str
    name: str
    qty: int
    price: float


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
