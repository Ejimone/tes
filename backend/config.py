"""
Configuration for backend deployment
"""
import os

# Blockchain RPC URL - can be overridden via environment variable
BLOCKCHAIN_RPC_URL = os.getenv(
    "BLOCKCHAIN_RPC_URL",
    "http://127.0.0.1:7545"  # Default to local Ganache
)

# Contract address - MUST be set via environment variable in production
CONTRACT_ADDRESS = os.getenv(
    "CONTRACT_ADDRESS",
    ""  # Will be set after deployment
)

# CORS origins - comma-separated list
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "*"  # Allow all in development, restrict in production
).split(",")

# Port
PORT = int(os.getenv("PORT", "8080"))

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
