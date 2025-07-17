import os
import requests
from dotenv import load_dotenv
from smolagents import tool
from requests.models import PreparedRequest
from collector import collected_results

load_dotenv()
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_API_KEY")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_SECRET")

def enrich_hotel_with_google_data(hotel_name: str, city: str = ""):
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": f"{hotel_name} {city}".strip(),
        "inputtype": "textquery",
        "fields": "place_id,photos,name,formatted_address",
        "key": os.getenv("GOOGLE_API_KEY")
    }

    res = requests.get(url, params=params).json()
    candidates = res.get("candidates", [])
    if not candidates:
        return {"image": None, "maps_url": None}

    hotel = candidates[0]
    place_id = hotel.get("place_id")

    # Optional image
    if "photos" in hotel:
        photo_ref = hotel["photos"][0]["photo_reference"]
        image_url = (
            f"https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth=400&photoreference={photo_ref}&key={os.getenv('GOOGLE_API_KEY')}"
        )
    else:
        image_url = None

    maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    return {"image": image_url, "maps_url": maps_url}

def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET,
    }
    res = requests.post(url, headers=headers, data=data)
    return res.json()["access_token"]


def get_hotel_ids_by_city(city_code: str, token: str, radius_km: int = 5) -> list:
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    params = {
        "cityCode": city_code,
        "radius": radius_km,
        "radiusUnit": "KM",
        "hotelSource": "ALL"
    }
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print("❌ Hotel ID fetch failed", res.status_code, res.text)
        return []

    hotel_ids = [h["hotelId"] for h in res.json().get("data", []) if "hotelId" in h]
    return hotel_ids[:20]


@tool
def search_hotels_from_city(city_code: str, checkin_date: str) -> list:
    """
    Get hotel offers from a city by fetching hotel IDs first.

    Args:
        city_code: IATA code like "NYC"
        checkin_date: "2025-05-10"

    Returns:
        List of hotel dicts (name, price, rating, address)
    """
    token = get_amadeus_token()
    hotel_ids = get_hotel_ids_by_city(city_code, token)
    if not hotel_ids:
        return [{"error": "No hotel IDs found."}]

    url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "hotelIds": ",".join(hotel_ids),
        "checkInDate": checkin_date,
        "adults": 1,
        "roomQuantity": 1,
        "bestRateOnly": True
    }

    req = PreparedRequest()
    req.prepare_url(url, params)
    # print("🔗 Request URL:", req.url)

    res = requests.get(url, headers=headers, params=params)
    # print("📦 Raw response:", res.text)

    if res.status_code != 200:
        return [{"error": f"Hotel offer error {res.status_code}"}]

    data = res.json().get("data", [])
    results = []
    seen = set()
    results = []
    seen = set()
    for h in data:
        hotel_info = h.get("hotel", {})
        name = hotel_info.get("name")
        
        # ❌ Skip test or demo hotels
        if not name or "test" in name.lower() or "demo" in name.lower():
            continue

        if name not in seen:
            seen.add(name)
            enrichment = enrich_hotel_with_google_data(name, city=city_code)
            results.append({
                "name": name,
                "image": enrichment["image"],
                "url": enrichment["maps_url"]
            })

    collected_results["hotels"] = results[:6]
    return results[:6]