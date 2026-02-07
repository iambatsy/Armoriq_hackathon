from fastmcp import FastMCP
from utils import verify_armor_intent
import os

# Create the MCP Server instance
mcp = FastMCP("TravelExecutor")

# Load the secret we defined in mcp.json
SECRET = os.getenv("ARMOR_IQ_SECRET")

@mcp.tool()
def book_flight(destination: str, price: float, armor_token: str) -> str:
    """
    High-stakes tool: Executes a flight booking.
    Requires a cryptographic 'armor_token' for intent verification.
    """
    # 1. Verification (Checks if ArmorIQ signed this exact request)
    is_valid = verify_armor_intent(
        message=f"book:{destination}:{price}",
        token=armor_token,
        secret=SECRET
    )

    if not is_valid:
        return "CRITICAL ERROR: Intent Token Verification Failed. Action Blocked."

    # 2. Hard-coded Safety Wall (The 'Deterministic' Guardrail)
    if price > 50000:
        return f"BLOCKED: Price ₹{price} exceeds the code-level safety cap."

    return f"SUCCESS: Flight to {destination} confirmed for ₹{price}."

if __name__ == "__main__":
    mcp.run()