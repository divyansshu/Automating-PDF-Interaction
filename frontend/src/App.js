import React, { useState } from "react";
import PdfUpload from "./components/PdfUpload";
import ChatInterface from "./components/ChatInterface";
import './App.css';

function App() {
  // Initialize state from localStorage or default to "upload"
  const [step, setStep] = useState(() => {
    return localStorage.getItem("appStep") || "upload";
  });

  // Update localStorage whenever step changes
  React.useEffect(() => {
    localStorage.setItem("appStep", step);
  }, [step]);

  const handleReset = () => {
    localStorage.removeItem("appStep");
    localStorage.removeItem("chatMessages"); // Clear chat history too
    setStep("upload");
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📄 PDF AI Assistant</h1>
        {step === "chat" && (
          <button className="reset-button" onClick={handleReset}>
            Upload New PDF
          </button>
        )}
      </header>
      <main>
        {step === "upload" ? (
          <PdfUpload onUploadSuccess={() => setStep("chat")} />
        ) : (
          <ChatInterface onReset={handleReset} />
        )}
      </main>
    </div>
  );
}

export default App;
