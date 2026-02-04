// components/Carrello.tsx
interface CarrelloProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Carrello({ isOpen, onClose }: CarrelloProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* OVERLAY */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* PANNELLO LATERALE */}
      <div className="fixed right-0 top-0 h-full w-96 bg-slate-50 shadow-2xl z-50 flex flex-col font-sans">
        {/* HEADER */}
        <div className="bg-white border-b px-4 py-3 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-blue-600">Carrello</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-600 hover:bg-gray-100 rounded-full p-2 transition-colors"
            aria-label="Chiudi carrello"
          >
            <span className="text-2xl font-light">×</span>
          </button>
        </div>

        {/* CONTENUTO */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="text-center text-gray-500 mt-8">
            <div className="text-6xl mb-4">🛒</div>
            <p className="text-lg font-medium text-gray-700">Il carrello è vuoto</p>
            <p className="text-sm mt-2 text-gray-500">Inizia a ordinare tramite la chat!</p>
          </div>
        </div>

        {/* FOOTER */}
        <div className="p-4 bg-white border-t border-gray-100 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <span className="font-semibold text-gray-700">Totale:</span>
            <span className="text-xl font-bold text-blue-600">€ 0,00</span>
          </div>
          <button
            disabled
            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-2xl py-3 text-sm font-bold hover:from-blue-700 hover:to-blue-800 disabled:from-slate-200 disabled:to-slate-300 disabled:text-slate-400 transition-all shadow-md hover:shadow-lg disabled:cursor-not-allowed"
          >
            Conferma Ordine
          </button>
        </div>
      </div>
    </>
  );
}