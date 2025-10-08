import React, { useState, useEffect } from "react";
import { useWeb3 } from "./Web3Context";
import toast from "react-hot-toast";

const ChatInterface = () => {
  const {
    account,
    isConnected,
    isLoading,
    isCorrectNetwork,
    connectWallet,
    disconnectWallet,
    switchToSepolia,
    checkUserRegistration,
    registerUser,
    sendMessage,
    getChatMessages,
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

    const success = await sendMessage(chatPartner, messageContent);
    if (success) {
      // Refresh messages
      const messages = await getChatMessages(account, chatPartner);
      setChatMessages(messages);
      setMessageContent("");
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
          <div style={{ fontSize: '4rem', marginBottom: '16px' }}>⚠️</div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3b4a54', marginBottom: '16px' }}>
            Wrong Network
          </h2>
          <p className="text-gray" style={{ marginBottom: '24px' }}>
            Please switch to Sepolia testnet to use this application.
          </p>
          <button
            onClick={switchToSepolia}
            className="button"
            style={{ 
              width: '100%', 
              backgroundColor: '#dc3545',
              ':hover': { backgroundColor: '#c82333' }
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
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">
          <div className="text-center mb-6">
            <User className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Complete Registration
            </h2>
            <p className="text-gray-600">
              Choose a display name for your account
            </p>
          </div>

          <div className="bg-green-50 p-4 rounded-lg mb-6">
            <p className="text-sm text-green-800">
              <strong>Connected:</strong> {formatAddress(account)}
            </p>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Display Name
              </label>
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Enter your name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
            >
              {isLoading ? (
                <Loader className="w-5 h-5 animate-spin mr-2" />
              ) : (
                <CheckCircle className="w-5 h-5 mr-2" />
              )}
              Register Account
            </button>
          </form>

          <button
            onClick={disconnectWallet}
            className="w-full mt-4 text-gray-500 hover:text-gray-700 font-medium py-2"
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
      <div className="min-h-screen bg-gray-100 flex flex-col">
        {/* Header */}
        <div className="bg-green-500 text-white p-4 flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => setCurrentView("home")}
              className="mr-4 text-white hover:text-green-200"
            >
              ←
            </button>
            <div>
              <h3 className="font-semibold">Chat with</h3>
              <p className="text-sm text-green-100">
                {formatAddress(chatPartner)}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-green-100">You</p>
            <p className="text-xs text-green-200">{formatAddress(account)}</p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 p-4 space-y-4 overflow-y-auto">
          {chatMessages.length === 0 ? (
            <div className="text-center text-gray-500 mt-20">
              <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No messages yet. Start the conversation!</p>
            </div>
          ) : (
            chatMessages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${
                  msg.sender.toLowerCase() === account.toLowerCase()
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    msg.sender.toLowerCase() === account.toLowerCase()
                      ? "bg-green-500 text-white"
                      : "bg-white text-gray-800 border"
                  }`}
                >
                  <p className="text-sm">{msg.content}</p>
                  <p className="text-xs opacity-75 mt-1">
                    {formatTimestamp(msg.timestamp)}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Message Input */}
        <form onSubmit={handleSendMessage} className="p-4 bg-white border-t">
          <div className="flex space-x-2">
            <input
              type="text"
              value={messageContent}
              onChange={(e) => setMessageContent(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={isLoading || !messageContent.trim()}
              className="bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white p-2 rounded-lg transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    );
  }

  // Home Screen
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-green-500 text-white p-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">WhatsApp Web3</h1>
          <p className="text-sm text-green-100">Decentralized Messaging</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-green-100">{formatAddress(account)}</p>
          <button
            onClick={disconnectWallet}
            className="text-xs text-green-200 hover:text-white"
          >
            Disconnect
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-4 max-w-md mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="text-center mb-6">
            <MessageCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-800 mb-2">
              Start New Chat
            </h2>
            <p className="text-gray-600">
              Enter the wallet address of the person you want to chat with
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recipient Wallet Address
              </label>
              <input
                type="text"
                value={recipientAddress}
                onChange={(e) => setRecipientAddress(e.target.value)}
                placeholder="0x1234...5678"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <button
              onClick={handleStartChat}
              disabled={isLoading || !recipientAddress.trim()}
              className="w-full bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
            >
              {isLoading ? (
                <Loader className="w-5 h-5 animate-spin mr-2" />
              ) : (
                <MessageCircle className="w-5 h-5 mr-2" />
              )}
              Start Chat
            </button>
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-800 mb-2">💡 Tips</h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Make sure the recipient is registered</li>
              <li>• Use valid Ethereum addresses</li>
              <li>• Messages are stored on blockchain</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
