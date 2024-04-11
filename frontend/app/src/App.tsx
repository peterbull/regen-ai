import React from "react";
import "./App.css";
import Weather from "./components/Weather";
import NavButton from "./components/NavButton";

function App() {
  return (
    <div className="App pt-6">
      <h1 className="inline-block font-extralight text-7xl text-custom-blue py-6 border-4 border-custom-blue rounded-xl p-4 uppercase">
        Regen AP-AI
      </h1>
      <Weather />
      <div className="flex space-x-4 justify-center">
        <NavButton name="Trace in Phoenix" redirect="http://localhost:6006" />
        <NavButton name="API Docs" redirect="http://localhost:8000/docs" />
      </div>
    </div>
  );
}

export default App;
