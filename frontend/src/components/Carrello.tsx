import type { CartItem } from "../types/cart";

// DATI DI ESEMPIO (MOCK DATA) per visualizzare l'anteprima!!!
const MOCK_ITEMS: CartItem[] = [
  { id: 1, name: "Acqua naturale", price: 0.50, quantity: 10 },
  { id: 2, name: "Birra", price: 1.50, quantity: 3 },
  { id: 3, name: "Pizza", price: 5.00, quantity: 3 },
];

interface CarrelloProps {
  isOpen: boolean;
  onClose: () => void;
  cart: CartItem[];
  onRemoveItem: (itemId: number) => void;
  onReloadCart: () => void;
}

export default function Carrello({ isOpen, onClose, cart, onRemoveItem, onReloadCart }: CarrelloProps) {
  // USA I DATI REALI SE PRESENTI, ALTRIMENTI USA I MOCK PER IL TEST VISIVO, DA SISTEMARE APPENA SI IMPLEMENTA
  const displayCart = cart.length > 0 ? cart : MOCK_ITEMS;

  if (!isOpen) return null;

  // Calcola il totale basandosi su displayCart
  const total = displayCart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const handleConfirmOrder = async () => {
    if (displayCart.length === 0) return;
    alert("Funzionalità di conferma ordine in arrivo!");
    onClose();
  };

  return (
    <>
      {/* OVERLAY */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* PANNELLO LATERALE */}
      <div className="fixed right-0 top-0 h-full w-96 bg-slate-50 shadow-2xl z-50 flex flex-col font-sans animate-in slide-in-from-right duration-300">
        {/* HEADER */}
        <div className="bg-white border-b px-4 py-4 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-blue-600">Carrello</h2>
            {displayCart.length > 0 && (
              <span className="bg-blue-100 text-blue-700 text-xs font-semibold px-2 py-1 rounded-full">
                {displayCart.length} {displayCart.length === 1 ? 'articolo' : 'articoli'}
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

        {/* CONTENUTO */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {displayCart.length === 0 ? (
            <div className="text-center text-gray-500 mt-12">
              <div className="text-6xl mb-4 opacity-20">🛒</div>
              <p className="text-lg font-medium text-gray-700">Il carrello è vuoto</p>
              <p className="text-sm mt-2 text-gray-500">Inizia a ordinare tramite la chat!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {displayCart.map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-xl p-4 border border-gray-100 hover:border-blue-200 transition-all shadow-sm hover:shadow-md group"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-bold text-gray-800 flex-1 leading-tight">
                      {item.name}
                    </h3>
                    
                    <button
                      onClick={() => onRemoveItem(item.id)}
                      className="ml-2 p-1.5 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      title="Rimuovi"
                    >
                      <span className="text-lg">🗑️</span>
                    </button>
                  </div>

                  <div className="flex items-end justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-md font-bold">
                          x{item.quantity}
                        </span>
                        <span className="text-gray-500">
                          €{item.price.toFixed(2)}
                        </span>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="block text-xs text-gray-400">Subtotale</span>
                      <span className="font-bold text-blue-600 text-lg">
                        €{(item.price * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* FOOTER */}
        <div className="p-6 bg-white border-t border-gray-100 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
          {displayCart.length > 0 && (
            <div className="mb-4 space-y-2">
              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>Resoconto quantità:</span>
                <span className="font-medium text-gray-700">
                   {displayCart.reduce((sum, item) => sum + item.quantity, 0)} pz
                </span>
              </div>
              <div className="flex justify-between items-center pt-2 border-t border-dashed">
                <span className="text-lg font-medium text-gray-800">Totale Ordine</span>
                <span className="text-2xl font-black text-blue-600">€ {total.toFixed(2)}</span>
              </div>
            </div>
          )}
          
          <button
            disabled={displayCart.length === 0}
            onClick={handleConfirmOrder}
            className="w-full bg-blue-600 text-white rounded-xl py-4 text-base font-bold hover:bg-blue-700 active:scale-[0.98] disabled:bg-gray-200 disabled:text-gray-400 transition-all shadow-lg shadow-blue-200 disabled:shadow-none"
          >
            Invia Ordine
          </button>
        </div>
      </div>
    </>
  );
}