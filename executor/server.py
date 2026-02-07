import os
import hmac
import hashlib
from dotenv import load_dotenv
from fastmcp import FastMCP
from amadeus import Client, ResponseError

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize the Server and Clients
mcp = FastMCP("TravelExecutor")

amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)

# Shared secret for ArmorIQ token verification
ARMOR_SECRET = os.getenv("ARMOR_IQ_SECRET")

# --- UTILS (Integrated directly for simplicity) ---
def verify_armor_token(message: str, token: str) -> bool:
    """Verifies the HMAC signature from ArmorIQ."""
    if not token or not ARMOR_SECRET:
        return False
    expected = hmac.new(
        ARMOR_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, token)

# --- TOOLS ---

@mcp.tool()
def search_flights(origin: str, destination: str, date: str) -> str:
    """
    Fetches LIVE flight offers from Amadeus.
    Format: origin='BOM', destination='LON', date='2026-06-15'
    """
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            max=3
        )
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
        # Get list of hotels in the city
        response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
        if not response.data:
            return f"No hotels found in {city_code}."
            
        hotels = [f"🏨 {h['name']} (ID: {h['hotelId']})" for h in response.data[:5]]
        return f"Hotels in {city_code}:\n" + "\n".join(hotels)
    except ResponseError as e:
        return f"Hotel Search Error: {e}"

@mcp.tool()
def book_travel(item_id: str, price: float, armor_token: str) -> str:
    """
    HIGH-STAKES: Confirms a booking. Requires a valid ArmorIQ token.
    """
    # 1. Verify the 'intent' wasn't tampered with
    is_valid = verify_armor_token(f"book:{item_id}:{price}", armor_token)
    
    if not is_valid:
        return "CRITICAL SECURITY ERROR: Unauthorized intent token. Action Blocked."

    # 2. Hard-coded safety cap
    if price > 100000:
        return f"POLICY BLOCKED: Price {price} exceeds extreme safety limit."

    # 3. Proceed to final API call (Simulated for demo)
    return f"SUCCESS: Booking for {item_id} confirmed at {price}. Token Verified."

if __name__ == "__main__":
    mcp.run()