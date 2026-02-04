// Chat.tsx
import { useEffect, useState, useRef } from "react";

interface Message {
  ruolo: "user" | "assistant";
  testo: string;
  timestamp?: Date;
}

const MAX_CHARS = 4096;

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // CARICA I MESSAGGI ESISTENTI
  useEffect(() => {
    const loadMessages = async () => {
      try {
        const res = await fetch("http://localhost:8000/conversazioni/1/messaggi");
        if (res.ok) {
          const data = await res.json();
          setMessages(data);
        }
      } catch (error) {
        console.error("Errore nel caricamento messaggi:", error);
      }
    };

    loadMessages();
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isProcessing || input.length > MAX_CHARS) return;

    const userMsg = { 
      ruolo: "user" as const, 
      testo: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsProcessing(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();
      setMessages(prev => [...prev, { 
        ruolo: "assistant", 
        testo: data.reply,
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error("Errore nell'invio:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      {/* HEADER */}
      <header className="bg-white border-b px-4 py-3 flex items-center justify-between shadow-sm z-10">
        <div>
          <h1 className="text-xl font-bold text-blue-600">SmartOrder AI</h1>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-[10px] text-gray-500 uppercase font-medium tracking-tight">Online</span>
          </div>
        </div>
      </header>

      <main className="flex-1 flex relative overflow-hidden">
        {/* AREA MESSAGGI */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex flex-col ${m.ruolo === "user" ? "items-end" : "items-start"}`}>
              <div className={`max-w-[85%] p-3 px-4 shadow-sm ${
                m.ruolo === "user" 
                  ? "bg-blue-600 text-white rounded-2xl rounded-tr-none" 
                  : "bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-tl-none"
              }`}>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{m.testo}</p>
                {m.timestamp && (
                  <p className={`text-[9px] mt-1 opacity-60 ${m.ruolo === "user" ? "text-right" : "text-left"}`}>
                    {m.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                )}
              </div>
            </div>
          ))}
          
          {isProcessing && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none p-3 shadow-sm">
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* BARRA DI INPUT */}
      <footer className="p-4 bg-white border-t border-gray-100 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3 items-end">
            {/* Input container*/}
            <div className="flex-1 relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-3xl blur opacity-0 group-hover:opacity-20 transition-opacity"></div>
              <div className="relative bg-slate-50 border-2 border-slate-200 rounded-3xl flex items-center gap-2 px-4 py-2 focus-within:border-blue-500 focus-within:bg-white transition-all shadow-sm hover:shadow-md">
                
                <textarea
                  className="flex-1 bg-transparent border-none resize-none text-sm focus:outline-none placeholder:text-slate-400 max-h-32 py-1.5"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      if (input.length <= MAX_CHARS) {
                        handleSend();
                      }
                    }
                  }}
                  placeholder="Scrivi il tuo ordine qui..."
                  disabled={isProcessing}
                  rows={1}
                  style={{
                    height: 'auto',
                    minHeight: '24px',
                  }}
                  onInput={(e) => {
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = Math.min(target.scrollHeight, 128) + 'px';
                  }}
                />
                
                {/* Contatore caratteri*/}
                <span className={`text-[10px] font-medium transition-colors ${
                  input.length > MAX_CHARS * 0.9 
                    ? 'text-red-500' 
                    : input.length > MAX_CHARS * 0.7 
                      ? 'text-orange-500' 
                      : 'text-slate-400'
                }`}>
                  {input.length}/{MAX_CHARS}
                </span>
              </div>
            </div>

            {/* Pulsante */}
            <button
              onClick={handleSend}
              disabled={!input.trim() || isProcessing || input.length > MAX_CHARS}
              className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-2xl px-6 py-3 text-sm font-bold hover:from-blue-700 hover:to-blue-800 disabled:from-slate-200 disabled:to-slate-300 disabled:text-slate-400 transition-all shadow-md hover:shadow-lg active:scale-95 disabled:cursor-not-allowed flex items-center gap-2 min-w-[100px] justify-center"
            >
              {isProcessing ? (
                <>
                  <span className="inline-block w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  <span>Invio...</span>
                </>
              ) : (
                <>
                  <span>Invia</span>
                  <span className="text-base">➤</span>
                </>
              )}
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}