import { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/")
      .then(r => r.json())
      .then(j => setData(j.hello));
  }, []);

  return <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white text-3xl">{data}</div>;
}

export default App;
