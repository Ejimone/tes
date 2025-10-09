import React, { useState, useEffect } from "react";
import { useWeb3 } from "./Web3Context";
import toast from "react-hot-toast";

const ChatInterface = () => {
  const {
    account,
    isConnected,
    isLoading,
    isCorrectNetwork,
    privateKey,
    connectWallet,
    disconnectWallet,
    switchToSepolia,
    checkUserRegistration,
    registerUser,
    sendMessage,
    getChatMessages,
    clearPrivateKey,
  } = useWeb3();

  const [currentView, setCurrentView] = useState("home"); // 'home', 'register', 'chat'
  const [recipientAddress, setRecipientAddress] = useState("");
  const [messageContent, setMessageContent] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [userName, setUserName] = useState("");
  const [chatPartner, setChatPartner] = useState("");

  // Check user registration status when connected
  useEffect(() => {
    const checkRegistration = async () => {
      if (isConnected && account) {
        const registered = await checkUserRegistration(account);
        if (!registered) {
          setCurrentView("register");
        }
      }
    };

    checkRegistration();
  }, [isConnected, account, checkUserRegistration]);

  // Handle user registration
  const handleRegister = async (e) => {
    e.preventDefault();
    if (!userName.trim()) {
      toast.error("Please enter your name");
      return;
    }

    const success = await registerUser(userName);
    if (success) {
      setCurrentView("home");
    }
  };

  // Start new chat
  const handleStartChat = async () => {
    if (!recipientAddress.trim()) {
      toast.error("Please enter recipient address");
      return;
    }

    // Validate Ethereum address format
    if (!/^0x[a-fA-F0-9]{40}$/.test(recipientAddress)) {
      toast.error("Invalid Ethereum address format");
      return;
    }

    if (recipientAddress.toLowerCase() === account.toLowerCase()) {
      toast.error("You cannot chat with yourself");
      return;
    }

    // Check if recipient is registered
    const isRecipientRegistered = await checkUserRegistration(recipientAddress);
    if (!isRecipientRegistered) {
      toast.error(
        "This user is not registered on the platform. Please ask them to register first."
      );
      return;
    }

    // Load existing messages
    const messages = await getChatMessages(account, recipientAddress);
    setChatMessages(messages);
    setChatPartner(recipientAddress);
    setCurrentView("chat");
  };

  // Send a message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageContent.trim()) {
      toast.error("Please enter a message");
      return;
    }

    try {
      const success = await sendMessage(chatPartner, messageContent);
      if (success) {
        // Clear message immediately for better UX
        setMessageContent("");

        // Refresh messages after a short delay to ensure backend is updated
        setTimeout(async () => {
          const messages = await getChatMessages(account, chatPartner);
          setChatMessages(messages);
        }, 1000);

        toast.success("Message sent! 📨");
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      toast.error("Failed to send message. Please try again.");
    }
  };

  // Format address for display
  const formatAddress = (address) => {
    if (!address) return "";
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  // Welcome/Connection Screen
  if (!isConnected) {
    return (
      <div className="whatsapp-container">
        <div className="welcome-card">
          <div className="logo">💬</div>
          <h1
            style={{
              fontSize: "2rem",
              fontWeight: "bold",
              color: "#3b4a54",
              marginBottom: "8px",
            }}
          >
            WhatsApp Web3
          </h1>
          <p className="text-gray">Decentralized messaging on the blockchain</p>

          <div style={{ marginTop: "32px" }}>
            <div
              style={{
                background: "#e8f5e8",
                padding: "16px",
                borderRadius: "8px",
                marginBottom: "20px",
                textAlign: "left",
              }}
            >
              <h3
                style={{
                  fontWeight: "600",
                  color: "#00a884",
                  marginBottom: "8px",
                }}
              >
                🚀 Features
              </h3>
              <ul
                style={{
                  fontSize: "14px",
                  color: "#00a884",
                  listStyle: "none",
                  padding: 0,
                }}
              >
                <li>• Connect with MetaMask wallet</li>
                <li>• Send messages on Sepolia testnet</li>
                <li>• Decentralized & secure</li>
                <li>• No intermediaries</li>
              </ul>
            </div>

            <button
              onClick={connectWallet}
              disabled={isLoading}
              className="button"
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {isLoading ? "⏳ " : "👛 "}
              Connect MetaMask
            </button>

            <p
              style={{ fontSize: "12px", color: "#667781", marginTop: "12px" }}
            >
              Make sure you're on Sepolia testnet
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Network Warning
  if (!isCorrectNetwork()) {
    return (
      <div className="whatsapp-container">
        <div className="welcome-card">
          <div style={{ fontSize: "4rem", marginBottom: "16px" }}>⚠️</div>
          <h2
            style={{
              fontSize: "1.5rem",
              fontWeight: "bold",
              color: "#3b4a54",
              marginBottom: "16px",
            }}
          >
            Wrong Network
          </h2>
          <p className="text-gray" style={{ marginBottom: "24px" }}>
            Please switch to Sepolia testnet to use this application.
          </p>
          <button
            onClick={switchToSepolia}
            className="button"
            style={{
              width: "100%",
              backgroundColor: "#dc3545",
              ":hover": { backgroundColor: "#c82333" },
            }}
          >
            Switch to Sepolia
          </button>
        </div>
      </div>
    );
  }

  // Registration Screen
  if (currentView === "register") {
    return (
      <div className="whatsapp-container">
        <div className="form-section">
          <div className="text-center mb-4">
            <div style={{ fontSize: "4rem", marginBottom: "16px" }}>👤</div>
            <h2
              style={{
                fontSize: "1.5rem",
                fontWeight: "bold",
                color: "#3b4a54",
                marginBottom: "8px",
              }}
            >
              Complete Registration
            </h2>
            <p className="text-gray">Choose a display name for your account</p>
          </div>

          <div className="wallet-info">
            <p style={{ fontSize: "14px" }}>
              <strong>Connected:</strong> {formatAddress(account)}
            </p>
          </div>

          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label className="label">Display Name</label>
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Enter your name"
                className="input"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="button"
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {isLoading ? "⏳ " : "✅ "}
              Register Account
            </button>
          </form>

          <button
            onClick={disconnectWallet}
            className="button-secondary"
            style={{ width: "100%", marginTop: "16px" }}
          >
            Disconnect Wallet
          </button>
        </div>
      </div>
    );
  }

  // Chat Interface
  if (currentView === "chat") {
    return (
      <div className="whatsapp-container">
        <div className="chat-interface">
          {/* Header */}
          <div className="chat-header">
            <div className="flex items-center">
              <button
                onClick={() => setCurrentView("home")}
                style={{
                  marginRight: "16px",
                  background: "none",
                  border: "none",
                  color: "white",
                  fontSize: "18px",
                  cursor: "pointer",
                }}
              >
                ← Back
              </button>
              <div>
                <h3 style={{ fontWeight: "600", margin: 0 }}>Chat with</h3>
                <p style={{ fontSize: "14px", margin: 0, opacity: 0.8 }}>
                  {formatAddress(chatPartner)}
                </p>
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <p style={{ fontSize: "14px", margin: 0 }}>You</p>
              <p style={{ fontSize: "12px", margin: 0, opacity: 0.8 }}>
                {formatAddress(account)}
              </p>
            </div>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {chatMessages.length === 0 ? (
              <div className="loading">
                <div style={{ fontSize: "3rem", marginBottom: "16px" }}>💬</div>
                <p>No messages yet. Start the conversation!</p>
              </div>
            ) : (
              chatMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`message ${
                    msg.sender.toLowerCase() === account.toLowerCase()
                      ? "sent"
                      : "received"
                  }`}
                >
                  <div className="message-bubble">
                    <div className="message-content">{msg.content}</div>
                    <div className="message-time">
                      {formatTimestamp(msg.timestamp)}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} className="chat-input">
            <input
              type="text"
              value={messageContent}
              onChange={(e) => setMessageContent(e.target.value)}
              placeholder="Type a message..."
            />
            <button
              type="submit"
              disabled={isLoading || !messageContent.trim()}
              className="send-button"
            >
              ➤
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Home Screen
  return (
    <div className="whatsapp-container">
      {/* Header */}
      <div
        style={{
          background: "#00a884",
          color: "white",
          padding: "16px 20px",
          borderRadius: "12px",
          marginBottom: "20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: "bold", margin: 0 }}>
            WhatsApp Web3
          </h1>
          <p style={{ fontSize: "14px", margin: 0, opacity: 0.8 }}>
            Decentralized Messaging
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <p style={{ fontSize: "14px", margin: 0, opacity: 0.8 }}>
            {formatAddress(account)}
          </p>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginTop: "4px",
            }}
          >
            {privateKey ? (
              <>
                <span
                  style={{ fontSize: "12px", opacity: 0.8, color: "#90EE90" }}
                >
                  🔐 Key Stored
                </span>
                <button
                  onClick={clearPrivateKey}
                  style={{
                    background: "none",
                    border: "none",
                    color: "rgba(255,255,255,0.8)",
                    fontSize: "12px",
                    cursor: "pointer",
                    textDecoration: "underline",
                  }}
                >
                  Clear Key
                </button>
              </>
            ) : (
              <span
                style={{ fontSize: "12px", opacity: 0.8, color: "#FFB6C1" }}
              >
                🔓 No Key Stored
              </span>
            )}
            <button
              onClick={disconnectWallet}
              style={{
                background: "none",
                border: "none",
                color: "rgba(255,255,255,0.8)",
                fontSize: "12px",
                cursor: "pointer",
                textDecoration: "underline",
              }}
            >
              Disconnect
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="form-section">
        <div className="text-center mb-4">
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>💬</div>
          <h2
            style={{
              fontSize: "1.25rem",
              fontWeight: "bold",
              color: "#3b4a54",
              marginBottom: "8px",
            }}
          >
            Start New Chat
          </h2>
          <p className="text-gray">
            Enter the wallet address of the person you want to chat with
          </p>
        </div>

        <div className="form-group">
          <label className="label">Recipient Wallet Address</label>
          <input
            type="text"
            value={recipientAddress}
            onChange={(e) => setRecipientAddress(e.target.value)}
            placeholder="0x1234...5678"
            className="input"
          />
        </div>

        <button
          onClick={handleStartChat}
          disabled={isLoading || !recipientAddress.trim()}
          className="button"
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {isLoading ? "⏳ " : "💬 "}
          Start Chat
        </button>

        <div
          style={{
            marginTop: "24px",
            padding: "16px",
            background: "#e8f5e8",
            borderRadius: "8px",
          }}
        >
          <h3
            style={{ fontWeight: "600", color: "#00a884", marginBottom: "8px" }}
          >
            💡 Tips
          </h3>
          <ul
            style={{
              fontSize: "14px",
              color: "#00a884",
              listStyle: "none",
              padding: 0,
            }}
          >
            <li>• Make sure the recipient is registered</li>
            <li>• Use valid Ethereum addresses</li>
            <li>• Messages are stored on blockchain</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
