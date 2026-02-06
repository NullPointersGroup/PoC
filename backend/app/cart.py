from fastapi import APIRouter, status, HTTPException
from typing import Any, Dict
from .api import SessionDep
from .database import *
from .schemas import UpdateQuantityRequest, CartAddRequest
from .AI import invoke_cart_agent

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

@router.get("/{user}")
def query_cart_agent(user: str, message: str) -> Dict[str, Any] | Any:
    return invoke_cart_agent(message)["messages"][-1].content