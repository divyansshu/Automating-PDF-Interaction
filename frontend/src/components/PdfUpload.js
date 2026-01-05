
import React, { useState } from "react";
import axios from "axios";
import '../App.css'; // make sure CSS is imported

export default function PdfUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  const handleUpload = async () => {
    if (!file) {
      setMessage("⚠️ Please select a PDF first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploading(true);
      setMessage("⏳ Uploading... Please wait...");

      let API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
      API_URL = API_URL.replace(/\/$/, "");
      const res = await axios.post(`${API_URL}/upload_pdf`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage("✅ PDF uploaded successfully!");
      setUploading(false);

      onUploadSuccess(); // switch to chat interface

    } catch (error) {
      console.error("Upload failed:", error);
      setMessage("❌ Upload failed. Please try again.");
      setUploading(false);
    }
  };

  return (
    <div className="upload-card">
      <h2>Upload Your PDF</h2>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button
        onClick={handleUpload}
        disabled={uploading}
        className="upload-button"
      >
        {uploading ? "Uploading..." : "Upload PDF"}
      </button>
      {message && <p className="status-message">{message}</p>}
    </div>
  );
}
