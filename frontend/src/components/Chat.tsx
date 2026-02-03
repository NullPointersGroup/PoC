// Chat.tsx
import { useEffect, useState, useRef } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
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
    if (!input.trim()) return;
    
    const userMsg = { role: "user" as const, content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });

    const data = await res.json();
    setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 flex flex-col">
        {messages.map((m, i) => (
          <div key={i} className={`inline-block max-w-xs p-2 mb-2 px-4 ${
            m.role === "user"
              ? "bg-blue-400 text-white rounded-2xl self-end"
              : "bg-gray-300 text-black rounded-2xl self-start"
          }`}>
            {m.content}
          </div>          
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 border-t flex">
        <input
          className="flex-1 border rounded px-2 py-1"
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSend()}
          placeholder="Scrivi un messaggio..."
        />
        <button 
          onClick={handleSend} 
          className="ml-2 px-4 py-1 border rounded bg-slate-300"
        >
          Invia
        </button>
      </div>
    </div>
  );
}