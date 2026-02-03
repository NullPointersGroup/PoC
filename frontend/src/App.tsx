import Navbar from "./components/Navbar";
import Chat from "./components/Chat";

function App() {
  return (
    <div className="flex h-screen bg-cyan-200 text-black">
      <Navbar /> 
      <div className="flex-1">
        <Chat /> 
      </div>
    </div>
  );
}

export default App;