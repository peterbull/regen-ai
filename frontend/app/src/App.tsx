import React from "react";
import "./App.css";
import Weather from "./components/Weather";
import { Discovery } from "aws-sdk";

function App() {
  return (
    <div className="App">
      <h1 className="text-3xl text-custom-off-white">Regen AI API</h1>
      <p>testing 2</p>
      <Weather />
    </div>
  );
}

export default App;
