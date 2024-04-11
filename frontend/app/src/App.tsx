import React from "react";
import "./App.css";
import Weather from "./components/Weather";

function App() {
  return (
    <div className="App pt-6">
      <h1 className="inline-block font-extralight text-7xl text-custom-blue py-6 border-4 border-custom-blue rounded-xl p-4 uppercase">
        Regen APAI
      </h1>
      <Weather />

      <button className="inline-block font-extralight text-2xl text-custom-blue py-3 border-2 border-custom-blue rounded-xl p-4 mt-6 uppercase hover:bg-custom-blue hover:text-custom-light-green active:bg-custom-teal active:text-custom-off-white">
        <a
          href="http://localhost:6006"
          target="_blank"
          rel="noopener noreferrer"
        >
          Trace in Phoenix
        </a>
      </button>
    </div>
  );
}

export default App;
