import React from "react";
import "./App.css";
import Weather from "./components/Weather";
import { Discovery } from "aws-sdk";

function App() {
  return (
    <div className="App">
      <h1 className="text-3xl text-custom-blue">Regen AI API</h1>
      <Weather />
    </div>
  );
}

export default App;
