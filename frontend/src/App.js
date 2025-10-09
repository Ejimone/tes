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
            duration: 2000, // Shorter duration
            style: {
              background: "#363636",
              color: "#fff",
            },
            success: {
              duration: 2000, // Shorter duration for success messages
              theme: {
                primary: "#4ade80",
              },
            },
            error: {
              duration: 3000, // Slightly longer for errors
            },
          }}
          containerStyle={{
            top: 20,
            right: 20,
          }}
          reverseOrder={false}
          limit={3} // Limit maximum number of toasts shown at once
        />
      </div>
    </Web3Provider>
  );
}

export default App;
