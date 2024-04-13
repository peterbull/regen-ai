import React from "react";
import "./App.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Weather from "./components/Weather";
import NavButton from "./components/NavButton";
import RagTest from "./components/RagTest";

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
      {/* 
      <Router>
        <Routes>
          <Route path="/rag" component={RagTest} />
        </Routes>
      </Router> */}
    </div>
  );
}

export default App;
