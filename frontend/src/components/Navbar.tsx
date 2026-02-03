// components/Navbar.tsx
import { useState } from "react";
import DeleteModal from "./DeleteModal";

export default function Navbar() {
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

  return (
    <>
      <div className={`bg-blue-600 text-white h-full p-4 transition-all duration-300 ${
        open ? "w-64" : "w-16"
      }`}>
        <button
          className="mb-4 text-white font-bold"
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

      {/* Modal di conferma */}
      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleClearChat}
      />
    </>
  );
}