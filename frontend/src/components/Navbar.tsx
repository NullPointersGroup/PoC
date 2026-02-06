import { useEffect, useState } from "react";
import DeleteModal from "./DeleteModal";
import Carrello from "./Carrello";
import type { CartItem } from "../types/cart";

interface NavbarProps {
  isCarrelloOpen: boolean;
  setIsCarrelloOpen: (open: boolean) => void;
  cart: CartItem[];
  onReloadCart: () => void;
}

export default function Navbar({
  isCarrelloOpen,
  setIsCarrelloOpen,
  cart,
  onReloadCart
}: NavbarProps) {
  const [open, setOpen] = useState(true);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const handleClearChat = async () => {
    try {
      const response = await fetch("http://localhost:8000/conversazioni/1", {
        method: "DELETE",
      });

      if (response.ok) {
        console.log("Chat cancellata con successo");
        window.location.reload();
      } else {
        console.error("Errore nella cancellazione");
      }
    } catch (error) {
      console.error("Errore:", error);
    }
  };

  useEffect(() => {
    if (isCarrelloOpen) {
      onReloadCart();
    }
  }, [isCarrelloOpen, onReloadCart]);

  return (
    <>
      <div
        className={`bg-blue-600 text-white h-full p-4 transition-all duration-300 flex-shrink-0 relative z-20 ${
          open ? "w-64" : "w-16"
        }`}
      >
        <button
          className="mb-4 text-white font-bold text-2xl hover:text-gray-200 transition-colors"
          onClick={() => setOpen(!open)}
        >
          <span aria-hidden="true" aria-label="Menù">☰</span>
        </button>

        {open && (
          <ul className="space-y-4">
            <li>
              <button
                onClick={() => setIsDeleteModalOpen(true)}
                className="w-full p-2 bg-red-600 hover:bg-red-700 rounded text-white text-left flex items-center"
              >
                <span className="mr-2">🗑️</span>
                Cancella Chat
              </button>
            </li>
          </ul>
        )}
      </div>

      <header
        className={`absolute top-0 bg-white border-b px-4 py-3 flex items-center justify-between shadow-sm z-10 transition-all duration-300 ${
          open ? "left-64" : "left-16"
        } ${isCarrelloOpen ? "right-96" : "right-0"}`}
      >
        <div>
          <h1 className="text-xl font-bold text-blue-600">SmartOrder AI</h1>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-[10px] text-gray-500 uppercase font-medium tracking-tight">
              Online
            </span>
          </div>
        </div>

        <button
          onClick={() => setIsCarrelloOpen(true)}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          aria-label="Apri carrello"
        >
          <span className="text-2xl">🛒</span>
        </button>
      </header>

      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleClearChat}
      />

      <Carrello
        isOpen={isCarrelloOpen}
        onClose={() => setIsCarrelloOpen(false)}
        cart={cart}
      />
    </>
  );
}
