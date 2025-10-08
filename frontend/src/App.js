import React from "react";
import { Toaster } from "react-hot-toast";
import { Web3Provider } from "./Web3Context";
import ChatInterface from "./ChatInterface";
import "./App.css";

function App() {
  return (
    <Web3Provider>
      <div className="App">
        <ChatInterface />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: "#363636",
              color: "#fff",
            },
            success: {
              duration: 3000,
              theme: {
                primary: "#4ade80",
              },
            },
          }}
        />
      </div>
    </Web3Provider>
  );
}

export default App;
