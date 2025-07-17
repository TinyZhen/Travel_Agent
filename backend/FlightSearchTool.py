import os
import requests
from dotenv import load_dotenv
from smolagents import tool
from collector import collected_results

load_dotenv()
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_API_KEY")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_SECRET")

def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

@tool
def search_flight_amadeus(origin: str, destination: str, date: str) -> list:
    """
    Search for top 3 flights using Amadeus API.

    Args:
        origin: IATA code of departure (e.g., "JFK")
        destination: IATA code of arrival (e.g., "LAX")
        date: Departure date (YYYY-MM-DD)

    Returns:
        A list of flights with airline, departure/arrival time, price.
    """
    IATA_AIRLINES = {
        "AA": "American Airlines",
        "DL": "Delta Air Lines",
        "UA": "United Airlines",
        "B6": "JetBlue",
        "F9": "Frontier Airlines",
        "WN": "Southwest Airlines",
        "NK": "Spirit Airlines",
        "SY": "Sun Country Airlines",
        "AS": "Alaska Airlines",
        "HA": "Hawaiian Airlines",
        "9K": "Cape Air"
    }

    print(f"✈️ Calling Amadeus with origin={origin}, destination={destination}, date={date}")

    try:
        token = get_amadeus_token()
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": date,
            "adults": 1,
            "currencyCode": "USD",
            "max": 20
        }

        print("📤 Request params:", params)

        res = requests.get(url, headers=headers, params=params)

        if res.status_code != 200:
            print(f"🚨 Amadeus API Error {res.status_code}: {res.text}")
            return []

        data = res.json()
        offers = data.get("data", [])
        flights = []

        for offer in offers:
            segments = offer["itineraries"][0]["segments"]
            if not segments:
                continue

            first_seg = segments[0]
            last_seg = segments[-1]

            if first_seg["departure"]["iataCode"] != origin or last_seg["arrival"]["iataCode"] != destination:
                continue

            carrier = first_seg.get("carrierCode", "Unknown")
            price = offer["price"]["total"]

            flights.append({
                "airline": IATA_AIRLINES.get(carrier, carrier),
                "from": first_seg["departure"]["iataCode"],
                "to": last_seg["arrival"]["iataCode"],
                "departure_time": first_seg["departure"]["at"],
                "arrival_time": last_seg["arrival"]["at"],
                "price": float(price)
            })

        flights = sorted(flights, key=lambda f: f["price"])
        collected_results["flights"] = flights[:6]

        print("✅ Flights collected:")
        for f in flights[:6]:
            print("  -", f)

        return flights[:6]

    except Exception as e:
        print("🔥 Exception during Amadeus call:", str(e))
        return []
