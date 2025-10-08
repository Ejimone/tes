import React, { createContext, useContext, useState, useEffect } from "react";
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
  const connectWallet = async () => {
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
        toast.loading("Switching to Sepolia network...");
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

      toast.success(
        `Connected to ${accounts[0].slice(0, 6)}...${accounts[0].slice(-4)}`
      );

      // Store connection in localStorage
      localStorage.setItem("isWalletConnected", "true");
    } catch (error) {
      console.error("Error connecting to MetaMask:", error);
      toast.error("Failed to connect wallet");
    } finally {
      setIsLoading(false);
    }
  };

  // Disconnect wallet
  const disconnectWallet = () => {
    setAccount(null);
    setProvider(null);
    setSigner(null);
    setIsConnected(false);
    setChainId(null);
    localStorage.removeItem("isWalletConnected");
    toast.success("Wallet disconnected");
  };

  // Check if user is registered
  const checkUserRegistration = async (address) => {
    try {
      const response = await fetch(`${API_BASE_URL}/users/${address}/exists`);
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

      // Get private key from user (for demo purposes - in production, use different approach)
      const privateKey = prompt(
        "Enter your private key for registration (DEMO ONLY - NEVER share your real private key!):"
      );

      if (!privateKey) {
        toast.error("Private key is required for registration");
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/users/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          address: account,
          name: name,
          private_key: privateKey,
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

      // Get private key (for demo - in production, use wallet signing)
      const privateKey = prompt(
        "Enter your private key to send message (DEMO ONLY):"
      );

      if (!privateKey) {
        toast.error("Private key is required to send message");
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/messages/send`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from_address: account,
          to_address: toAddress,
          content: content,
          is_media: false,
          private_key: privateKey,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("Message sent successfully!");
        return true;
      } else {
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
      const response = await fetch(`${API_BASE_URL}/messages/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user1_address: user1Address,
          user2_address: user2Address,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        return data.messages || [];
      } else {
        console.error("Failed to get chat messages:", data.detail);
        return [];
      }
    } catch (error) {
      console.error("Error getting chat messages:", error);
      return [];
    }
  };

  // Auto-connect if previously connected
  useEffect(() => {
    const wasConnected = localStorage.getItem("isWalletConnected");
    if (wasConnected === "true" && isMetaMaskInstalled()) {
      connectWallet();
    }
  }, [connectWallet]);

  // Listen for account changes
  useEffect(() => {
    if (isMetaMaskInstalled()) {
      const handleAccountsChanged = (accounts) => {
        if (accounts.length === 0) {
          disconnectWallet();
        } else if (accounts[0] !== account) {
          setAccount(accounts[0]);
          toast.info(
            `Switched to ${accounts[0].slice(0, 6)}...${accounts[0].slice(-4)}`
          );
        }
      };

      const handleChainChanged = (newChainId) => {
        setChainId(newChainId);
        if (newChainId !== SEPOLIA_CHAIN_ID) {
          toast.warning("Please switch to Sepolia network");
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
  }, [account]);

  const value = {
    account,
    provider,
    signer,
    isConnected,
    isLoading,
    chainId,
    isMetaMaskInstalled,
    isCorrectNetwork,
    connectWallet,
    disconnectWallet,
    switchToSepolia,
    checkUserRegistration,
    registerUser,
    sendMessage,
    getChatMessages,
  };

  return <Web3Context.Provider value={value}>{children}</Web3Context.Provider>;
};
