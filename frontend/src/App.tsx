import { useEffect, useState } from "react";
import Navbar from "./components/Navbar";
import Chat from "./components/Chat";
import type { CartItem } from "./types/cart";

const API_BASE_URL = "http://localhost:8000";

function App() {
  const [isCarrelloOpen, setIsCarrelloOpen] = useState(false);
  const [cart, setCart] = useState<CartItem[]>([]);

  const reloadCart = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/cart`);
      if (!res.ok) return;
      const data = await res.json();
      const mapped = (data as Array<{ prodotto: string; quantita: number; des_art?: string }>).map(
        (item) => ({
          id: item.prodotto,
          name: item.des_art ?? item.prodotto,
          quantity: item.quantita ?? 0,
        })
      );
      setCart(mapped.filter((item) => item.quantity > 0));
    } catch (error) {
      console.error("Errore nel caricamento carrello:", error);
    }
  };

  const removeCartItem = async (id: string) => {
    try {
      await fetch(`${API_BASE_URL}/cart/${encodeURIComponent(id)}`, {
        method: "DELETE",
      });
      await reloadCart();
    } catch (error) {
      console.error("Errore nella rimozione dal carrello:", error);
    }
  };

  const clearCart = async () => {
    try {
      await fetch(`${API_BASE_URL}/cart`, { method: "DELETE" });
      setCart([]);
    } catch (error) {
      console.error("Errore nella pulizia carrello:", error);
    }
  };

  useEffect(() => {
    reloadCart();
  }, []);

  return (
    <div className="flex h-screen bg-cyan-200 text-black">
      <Navbar
        isCarrelloOpen={isCarrelloOpen}
        setIsCarrelloOpen={setIsCarrelloOpen}
        cart={cart}
        onRemoveItem={removeCartItem}
        onReloadCart={reloadCart}
        onClearCart={clearCart}
      />
      <div className="flex-1 flex flex-col">
        <Chat isCarrelloOpen={isCarrelloOpen} onCartUpdated={reloadCart} />
      </div>
    </div>
  );
}

export default App;
