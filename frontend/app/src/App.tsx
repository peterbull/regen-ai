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
    </div>
  );
}

export default App;
