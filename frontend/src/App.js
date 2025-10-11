import React, { useState } from "react";
import PdfUpload from "./components/PdfUpload";
import './App.css';

function App() {
  const [uploaded, setUploaded] = useState(false);

  return (
    <div>
      {!uploaded ? (
        <PdfUpload onUploadSuccess={() => setUploaded(true)} />
      ) : (
        <div className="success-container">
          <h1 className="success-title">PDF Uploaded!</h1>
          <p className="success-text">You can now proceed to the chat interface.</p>
        </div>
      )}
    </div>
  );
}

export default App;
