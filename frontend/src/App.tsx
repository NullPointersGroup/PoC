import { useState } from "react";
import Navbar from "./components/Navbar";
import Chat from "./components/Chat";

function App() {
  const [isCarrelloOpen, setIsCarrelloOpen] = useState(false);

  return (
    <div className="flex h-screen bg-cyan-200 text-black">
      <Navbar 
        isCarrelloOpen={isCarrelloOpen}
        setIsCarrelloOpen={setIsCarrelloOpen}
      /> 
      <div className="flex-1 flex flex-col">
        <Chat isCarrelloOpen={isCarrelloOpen} /> 
      </div>
    </div>
  );
}

export default App;