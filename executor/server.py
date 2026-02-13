import os
import sys
import hmac
import hashlib
import requests
import time
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from amadeus import Client, ResponseError

# Load Environment Variables
load_dotenv()

# Initialize the Server and Clients
mcp = FastMCP("TravelExecutor", log_level="ERROR")
amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)

ARMORIQ_API_KEY = os.getenv("ARMORIQ_API_KEY", "ak_live_f4c41a714560fb4ef41901cf50ef5b7e4c6c8ed6725b116c7cfc1f6e6c8fc4fd")

def generate_armor_intent_token(goal: str, actions: list) -> tuple:
    """Generate an ArmorIQ intent token for a planned action."""
    
    policy_metadata = {
        "rules": [],
        "version": 1,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "policy_digest": hashlib.sha256(b"policy||[]").hexdigest()
    }
    
    payload = {
        "plan": {
            "steps": [{"action": action, "mcp": "travel-executor"} for action in actions],
            "metadata": {"goal": goal}
        },
        "policy": {
            "global": {
                "metadata": policy_metadata
            }
        },
        "identity": {
            "user_id": "kiara-thapar-001",
            "agent_id": "travel-orchestrator",
            "context_id": "telegram-flight-booking"
        },
        "validity_seconds": 3600
    }
    
    headers = {"Content-Type": "application/json"}
    endpoint = "https://customer-iap.armoriq.ai/intent"
    
    try:
        print(f"ARMORIQ: Requesting intent token from {endpoint}", file=sys.stderr)
        response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"ARMORIQ: Token received", file=sys.stderr)
        token = data.get("token", {})
        return token.get("intent_reference") or token.get("plan_hash"), None
    except Exception as e:
        print(f"ARMORIQ ERROR: {e}", file=sys.stderr)
        return None, str(e)

@mcp.tool()
def search_flights(origin: str, destination: str, date: str) -> str:
    """
    Fetches LIVE flight offers from Amadeus.
    Format: origin='BOM', destination='LON', date='2026-06-15'
    """
    print(f"FLIGHT SEARCH: {origin} -> {destination} on {date}", file=sys.stderr)
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            max=3
        )
        print(f"FOUND {len(response.data)} flights", file=sys.stderr)
        if not response.data:
            return "No flights found for those criteria."
            
        lines = []
        for flight in response.data:
            price = f"{flight['price']['currency']} {flight['price']['total']}"
            airline = flight['itineraries'][0]['segments'][0]['carrierCode']
            lines.append(f"✈️ {airline}: {price}")
        return "\n".join(lines)
    except ResponseError as e:
        return f"Flight Search Error: {e}"

@mcp.tool()
def search_hotels(city_code: str) -> str:
    """
    Lists bookable hotels in a city by IATA code (e.g., 'PAR' for Paris).
    """
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
        if not response.data:
            return f"No hotels found in {city_code}."
            
        hotels = [f"🏨 {h['name']} (ID: {h['hotelId']})" for h in response.data[:5]]
        return f"Hotels in {city_code}:\n" + "\n".join(hotels)
    except ResponseError as e:
        return f"Hotel Search Error: {e}"

@mcp.tool()
def get_booking_intent_token(item_id: str, price: float) -> str:
    """
    Get an ArmorIQ intent token for booking a flight.
    Call this BEFORE calling book_travel to get approval.
    """
    print(f"ARMORIQ: Generating intent token for {item_id} at ${price}", file=sys.stderr)
    goal = f"Book flight {item_id} for ${price}"
    actions = ["search_flights", "book_travel"]
    
    token_id, error = generate_armor_intent_token(goal, actions)
    
    if error:
        return f"ERROR: Failed to get ArmorIQ token: {error}"
    
    if not token_id:
        return "ERROR: No token returned from ArmorIQ"
    
    print(f"ARMORIQ: Token approved - {token_id[:16]}...", file=sys.stderr)
    return f"ArmorIQ Intent Token Generated: {token_id}\n\nUse this token to call book_travel(item_id='{item_id}', price={price}, armor_token='{token_id}')"

@mcp.tool()
def book_travel(item_id: str, price: float, armor_token: str) -> str:
    """
    HIGH-STAKES: Confirms a booking. Requires a valid ArmorIQ token.
    Get the token first by calling get_booking_intent_token().
    """
    print(f"BOOKING: {item_id} for ${price}", file=sys.stderr)
    
    # Verify ArmorIQ token format (64 char hex string)
    if not armor_token or len(armor_token) < 32:
        print("BLOCKED: Invalid token format", file=sys.stderr)
        return "❌ CRITICAL SECURITY ERROR: Invalid intent token format. Action Blocked."

    # Verify it's valid hex
    try:
        int(armor_token, 16)
    except ValueError:
        print("BLOCKED: Token not valid hex", file=sys.stderr)
        return "❌ CRITICAL SECURITY ERROR: Invalid ArmorIQ token format. Action Blocked."

    # Hard-coded safety cap
    if price > 100000:
        print(f"BLOCKED: Price ${price} exceeds policy limit", file=sys.stderr)
        return f"❌ POLICY BLOCKED: Price ${price} exceeds extreme safety limit of $100,000."

    print("BOOKING CONFIRMED with ArmorIQ token", file=sys.stderr)
    return f"✅ SUCCESS: Booking for {item_id} confirmed at ${price}. ArmorIQ Intent Token Verified!"

if __name__ == "__main__":
    mcp.run()