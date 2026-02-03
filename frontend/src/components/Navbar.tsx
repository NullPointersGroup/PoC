import { useState } from "react";

export default function Sidebar() {
  const [open, setOpen] = useState(true);

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div
        className={`bg-blue-600 text-white h-full p-4 transition-all duration-300 ${
          open ? "w-64" : "w-16"
        }`}
      >
        <button
          className="mb-4 text-white font-bold"
          onClick={() => setOpen(!open)}
        >
          <span aria-hidden="true" aria-label="Menù">☰</span>
        </button>

        {open && (
          <ul className="space-y-4">
            <li>Home</li>
            <li>Chat</li>
            <li>Impostazioni</li>
          </ul>
        )}
      </div>
    </div>
  );
}