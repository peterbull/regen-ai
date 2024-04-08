import React from "react";
import "./App.css";
import Weather from "./components/Weather";

function App() {
  return (
    <div className="App">
      <h1 className="text-3xl font-bold underline text-red-600">
        Simple React Typescript Tailwind Sample
      </h1>
      <Weather />
    </div>
  );
}

export default App;
