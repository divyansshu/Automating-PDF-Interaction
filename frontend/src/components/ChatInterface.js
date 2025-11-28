import React, { useState } from "react";
import axios from "axios";
import '../App.css';

export default function ChatInterface({ onReset }) {
    const [query, setQuery] = useState("");
    const messagesEndRef = React.useRef(null);

    // Initialize messages from localStorage
    const [messages, setMessages] = useState(() => {
        const saved = localStorage.getItem("chatMessages");
        return saved ? JSON.parse(saved) : [
            { sender: "ai", text: "Hello! I'm ready to answer questions about your PDF." }
        ];
    });

    const [loading, setLoading] = useState(false);

    // Auto-scroll to bottom whenever messages or loading state changes
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    React.useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    // Save messages to localStorage whenever they change
    React.useEffect(() => {
        localStorage.setItem("chatMessages", JSON.stringify(messages));
    }, [messages]);

    const handleSend = async () => {
        if (!query.trim()) return;

        // Add user message
        const newMessages = [...messages, { sender: "user", text: query }];
        setMessages(newMessages);
        setQuery("");
        setLoading(true);

        try {
            const res = await axios.post("http://localhost:8000/query", {
                question: query
            });

            // Add AI response
            setMessages(prev => [...prev, { sender: "ai", text: res.data.answer }]);
        } catch (error) {
            console.error("Query failed:", error);
            setMessages(prev => [...prev, { sender: "ai", text: "❌ Sorry, something went wrong." }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-history">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender}`}>
                        <div className="message-bubble">
                            {msg.text}
                        </div>
                    </div>
                ))}
                {loading && <div className="message ai"><div className="message-bubble">Typing...</div></div>}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
                <input
                    type="text"
                    placeholder="Ask a question about the PDF..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={loading}
                />
                <button onClick={handleSend} disabled={loading}>
                    Send
                </button>
            </div>
        </div>
    );
}
