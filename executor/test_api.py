from amadeus import Client, ResponseError

# Initialize the Amadeus client
amadeus = Client(
    client_id='YOUR_AMADEUS_API_KEY',
    client_secret='YOUR_AMADEUS_API_SECRET'
)

def test_connection():
    try:
        print("Connecting to Amadeus API...")
        # A simple test: Search for the city of London (LON)
        response = amadeus.reference_data.locations.get(
            keyword='LON',
            subType='CITY'
        )
        
        # If we get data back, the API works!
        if response.data:
            print("✅ Success! API is working.")
            print(f"First result: {response.data[0]['name']} ({response.data[0]['iataCode']})")
        else:
            print("⚠️ Connected, but no data was found.")
            
    except ResponseError as error:
        print("❌ API Error Detected:")
        print(error)
        print("\nCheck if your API Key and Secret are correct and that your app is 'Active' in the Amadeus dashboard.")

if __name__ == "__main__":
    test_connection()