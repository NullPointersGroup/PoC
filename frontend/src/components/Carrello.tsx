import type { CartItem } from "../types/cart";

interface CarrelloProps {
  isOpen: boolean;
  onClose: () => void;
  cart: CartItem[];
  onClearCart: () => void;
}

export default function Carrello({
  isOpen,
  onClose,
  cart,
  onClearCart,
}: CarrelloProps) {
  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />

      <div className="fixed right-0 top-0 h-full w-96 bg-slate-50 shadow-2xl z-50 flex flex-col font-sans animate-in slide-in-from-right duration-300">
        <div className="bg-white border-b px-4 py-4 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-blue-600">Carrello</h2>
            {cart.length > 0 && (
              <span className="bg-blue-100 text-blue-700 text-xs font-semibold px-2 py-1 rounded-full">
                {cart.length} {cart.length === 1 ? "articolo" : "articoli"}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full p-2 transition-all"
            aria-label="Chiudi carrello"
          >
            <span className="text-2xl font-light">×</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {cart.length === 0 ? (
            <div className="text-center text-gray-500 mt-12">
              <div className="text-6xl mb-4 opacity-20">🛒</div>
              <p className="text-lg font-medium text-gray-700">
                Il carrello è vuoto
              </p>
              <p className="text-sm mt-2 text-gray-500">
                Inizia a ordinare tramite la chat!
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {cart.map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-xl p-4 border border-gray-100 hover:border-blue-200 transition-all shadow-sm hover:shadow-md group"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-bold text-gray-800 flex-1 leading-tight">
                      {item.name}
                    </h3>
                  </div>

                  <div className="flex items-end justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-md font-bold">
                          x{item.quantity}
                        </span>
                        <span className="text-gray-500">Codice: {item.id}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-6 bg-white border-t border-gray-100 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]" />
      </div>
    </>
  );
}
