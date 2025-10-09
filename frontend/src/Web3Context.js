import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { ethers } from "ethers";
import toast from "react-hot-toast";

const Web3Context = createContext();

export const useWeb3 = () => {
  const context = useContext(Web3Context);
  if (!context) {
    throw new Error("useWeb3 must be used within a Web3Provider");
  }
  return context;
};

const SEPOLIA_CHAIN_ID = "0xaa36a7"; // 11155111 in hex
const API_BASE_URL =
  "https://whatsapp-dapp-backend-580832663068.us-central1.run.app/api/v1";

export const Web3Provider = ({ children }) => {
  const [account, setAccount] = useState(null);
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [chainId, setChainId] = useState(null);
  const [privateKey, setPrivateKey] = useState(() => {
    // Initialize from sessionStorage if available
    return sessionStorage.getItem("temp_private_key");
  });

  // Check if MetaMask is installed
  const isMetaMaskInstalled = () => {
    return (
      typeof window !== "undefined" && typeof window.ethereum !== "undefined"
    );
  };

  // Check if connected to correct network (Sepolia)
  const isCorrectNetwork = () => {
    return chainId === SEPOLIA_CHAIN_ID;
  };

  // Switch to Sepolia network
  const switchToSepolia = async () => {
    try {
      await window.ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: SEPOLIA_CHAIN_ID }],
      });
    } catch (switchError) {
      // If network doesn't exist, add it
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: "wallet_addEthereumChain",
            params: [
              {
                chainId: SEPOLIA_CHAIN_ID,
                chainName: "Sepolia Test Network",
                nativeCurrency: {
                  name: "Sepolia ETH",
                  symbol: "SEP",
                  decimals: 18,
                },
                rpcUrls: ["https://sepolia.infura.io/v3/"],
                blockExplorerUrls: ["https://sepolia.etherscan.io"],
              },
            ],
          });
        } catch (addError) {
          toast.error("Failed to add Sepolia network");
          throw addError;
        }
      } else {
        toast.error("Failed to switch to Sepolia network");
        throw switchError;
      }
    }
  };

  // Connect to MetaMask
  const connectWallet = useCallback(async () => {
    if (!isMetaMaskInstalled()) {
      toast.error(
        "MetaMask is not installed. Please install MetaMask to continue."
      );
      window.open("https://metamask.io/download/", "_blank");
      return;
    }

    setIsLoading(true);

    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts",
      });

      if (accounts.length === 0) {
        toast.error(
          "No accounts found. Please make sure MetaMask is unlocked."
        );
        return;
      }

      // Get current chain ID
      const currentChainId = await window.ethereum.request({
        method: "eth_chainId",
      });

      // Switch to Sepolia if not already
      if (currentChainId !== SEPOLIA_CHAIN_ID) {
        toast.success("Switching to Sepolia network...");
        await switchToSepolia();
      }

      // Set up provider and signer
      const web3Provider = new ethers.BrowserProvider(window.ethereum);
      const web3Signer = await web3Provider.getSigner();

      setProvider(web3Provider);
      setSigner(web3Signer);
      setAccount(accounts[0]);
      setChainId(currentChainId);
      setIsConnected(true);

      // Connection successful - toast will be shown by account change handler if needed

      // Store connection in localStorage
      localStorage.setItem("isWalletConnected", "true");
    } catch (error) {
      console.error("Error connecting to MetaMask:", error);
      toast.error("Failed to connect wallet");
    } finally {
      setIsLoading(false);
    }
  }, []); // Empty dependency array for useCallback

  // Disconnect wallet
  const disconnectWallet = () => {
    setAccount(null);
    setProvider(null);
    setSigner(null);
    setIsConnected(false);
    setChainId(null);
    clearPrivateKey(); // Clear stored private key for security
    localStorage.removeItem("isWalletConnected");
    toast.success("Wallet disconnected");
  };

  // Get private key (prompt only once per session)
  const getPrivateKey = async () => {
    if (privateKey) {
      return privateKey; // Return stored private key
    }

    const userPrivateKey = prompt(
      "🔐 Enter your private key for blockchain transactions:\n\n⚠️ SECURITY NOTE: This is for demo purposes only!\n• Your key will be stored temporarily in this session\n• Never share your real private key in production apps\n• Consider this a development/testing feature only\n\nPrivate Key:"
    );

    if (!userPrivateKey) {
      throw new Error("Private key is required for blockchain transactions");
    }

    // Validate private key format
    if (!userPrivateKey.match(/^(0x)?[a-fA-F0-9]{64}$/)) {
      throw new Error("Invalid private key format");
    }

    // Store in both state and sessionStorage for persistence
    setPrivateKey(userPrivateKey);
    sessionStorage.setItem("temp_private_key", userPrivateKey);
    return userPrivateKey;
  };

  // Clear private key (for logout or security)
  const clearPrivateKey = () => {
    setPrivateKey(null);
    sessionStorage.removeItem("temp_private_key");
    toast.success("Private key cleared for security");
  };

  // Check if user is registered
  const checkUserRegistration = async (address) => {
    try {
      const checksummedAddress = ethers.getAddress(address); // Convert to checksummed address
      const response = await fetch(
        `${API_BASE_URL}/users/${checksummedAddress}/exists`
      );
      const data = await response.json();
      return data.exists;
    } catch (error) {
      console.error("Error checking user registration:", error);
      return false;
    }
  };

  // Register user
  const registerUser = async (name) => {
    if (!signer || !account) {
      toast.error("Please connect your wallet first");
      return false;
    }

    try {
      setIsLoading(true);

      // Get private key (will be stored in session for seamless experience)
      const userPrivateKey = await getPrivateKey();

      const response = await fetch(`${API_BASE_URL}/users/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          address: ethers.getAddress(account), // Convert to checksummed address
          name: name,
          private_key: userPrivateKey,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("Registration successful!");
        return true;
      } else {
        toast.error(data.detail || "Registration failed");
        return false;
      }
    } catch (error) {
      console.error("Error registering user:", error);
      toast.error("Registration failed");
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Send message
  const sendMessage = async (toAddress, content) => {
    if (!signer || !account) {
      toast.error("Please connect your wallet first");
      return false;
    }

    try {
      setIsLoading(true);

      // Check if recipient is registered
      const isRecipientRegistered = await checkUserRegistration(toAddress);
      if (!isRecipientRegistered) {
        toast.error("The recipient is not registered on the platform");
        return false;
      }

      // Get private key (stored from previous input for seamless experience)
      const userPrivateKey = await getPrivateKey();

      const fromAddr = ethers.getAddress(account);
      const toAddr = ethers.getAddress(toAddress);

      console.log(`📨 Sending message:`);
      console.log(`   From: ${fromAddr}`);
      console.log(`   To: ${toAddr}`);
      console.log(`   Content: "${content}"`);

      const response = await fetch(`${API_BASE_URL}/messages/send`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from_address: fromAddr, // Convert to checksummed address
          to_address: toAddr, // Convert to checksummed address
          content: content,
          is_media: false,
          private_key: userPrivateKey,
        }),
      });

      const data = await response.json();
      console.log(`📥 Send response status: ${response.status}`);
      console.log(`📥 Send response data:`, data);

      if (response.ok) {
        console.log(`✅ Message sent successfully!`);
        toast.success("Message sent successfully!");
        return true;
      } else {
        console.error(`❌ Send failed:`, data.detail);
        toast.error(data.detail || "Failed to send message");
        return false;
      }
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Failed to send message");
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Get chat messages
  const getChatMessages = async (user1Address, user2Address) => {
    try {
      // Ensure consistent address ordering (lexicographically) for chat ID calculation
      const addr1 = ethers.getAddress(user1Address);
      const addr2 = ethers.getAddress(user2Address);

      console.log(`🔍 Fetching messages between:`);
      console.log(`   User 1: ${addr1}`);
      console.log(`   User 2: ${addr2}`);

      // Try both address orders to ensure we get all messages
      const payload1 = {
        user1_address: addr1,
        user2_address: addr2,
      };

      const payload2 = {
        user1_address: addr2,
        user2_address: addr1,
      };

      console.log(`📤 Trying payload 1:`, payload1);

      const response1 = await fetch(`${API_BASE_URL}/messages/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload1),
      });

      const data1 = await response1.json();
      console.log(`📥 Response 1 status: ${response1.status}`);
      console.log(`📥 Response 1 data:`, data1);

      let allMessages = [];

      if (response1.ok && data1.messages) {
        allMessages = [...data1.messages];
        console.log(`✅ Found ${data1.messages.length} messages with order 1`);
      }

      // Try reverse order to catch any missed messages
      console.log(`📤 Trying payload 2:`, payload2);

      const response2 = await fetch(`${API_BASE_URL}/messages/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload2),
      });

      const data2 = await response2.json();
      console.log(`� Response 2 status: ${response2.status}`);
      console.log(`📥 Response 2 data:`, data2);

      if (response2.ok && data2.messages) {
        // Add messages from second call, avoiding duplicates
        const existingIds = new Set(
          allMessages.map(
            (msg) =>
              msg.id || `${msg.from_address}-${msg.to_address}-${msg.timestamp}`
          )
        );
        const newMessages = data2.messages.filter(
          (msg) =>
            !existingIds.has(
              msg.id || `${msg.from_address}-${msg.to_address}-${msg.timestamp}`
            )
        );
        allMessages = [...allMessages, ...newMessages];
        console.log(
          `✅ Found ${data2.messages.length} messages with order 2, ${newMessages.length} new`
        );
      }

      // Sort messages by timestamp
      allMessages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

      console.log(`🎯 Total unique messages: ${allMessages.length}`);
      if (allMessages.length > 0) {
        console.log(
          `📋 All message details:`,
          allMessages.map((msg) => ({
            from: msg.from_address,
            to: msg.to_address,
            content: msg.content,
            timestamp: msg.timestamp,
          }))
        );
      }

      return allMessages;
    } catch (error) {
      console.error("💥 Error getting chat messages:", error);
      toast.error("Failed to load messages");
      return [];
    }
  };

  // Auto-connect if previously connected
  useEffect(() => {
    const wasConnected = localStorage.getItem("isWalletConnected");
    if (wasConnected === "true" && isMetaMaskInstalled() && !isConnected) {
      connectWallet();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array to run only once

  // Listen for account changes
  useEffect(() => {
    if (isMetaMaskInstalled()) {
      const handleAccountsChanged = (accounts) => {
        if (accounts.length === 0) {
          disconnectWallet();
        } else if (accounts[0] !== account && account) {
          // Only show toast if account was already set
          setAccount(accounts[0]);
          toast.success(
            `Switched to ${accounts[0].slice(0, 6)}...${accounts[0].slice(-4)}`
          );
        } else if (accounts[0] !== account) {
          setAccount(accounts[0]); // Set account without toast on initial connection
        }
      };

      const handleChainChanged = (newChainId) => {
        setChainId(newChainId);
        // Only show network warning if we were previously connected to Sepolia
        if (newChainId !== SEPOLIA_CHAIN_ID && chainId === SEPOLIA_CHAIN_ID) {
          toast.error("Please switch to Sepolia network");
        }
      };

      window.ethereum.on("accountsChanged", handleAccountsChanged);
      window.ethereum.on("chainChanged", handleChainChanged);

      return () => {
        window.ethereum.removeListener(
          "accountsChanged",
          handleAccountsChanged
        );
        window.ethereum.removeListener("chainChanged", handleChainChanged);
      };
    }
  }, [account, chainId]);

  const value = {
    account,
    provider,
    signer,
    isConnected,
    isLoading,
    chainId,
    privateKey, // Export private key state for UI indication
    isMetaMaskInstalled,
    isCorrectNetwork,
    connectWallet,
    disconnectWallet,
    switchToSepolia,
    checkUserRegistration,
    registerUser,
    sendMessage,
    getChatMessages,
    clearPrivateKey, // Export for logout functionality
  };

  return <Web3Context.Provider value={value}>{children}</Web3Context.Provider>;
};
