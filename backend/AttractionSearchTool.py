import os
import requests
from dotenv import load_dotenv
from smolagents import tool
from collector import collected_results

# Load the Google Places API key from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_coordinates(city_name):
    """Get latitude and longitude of a city name using Google Geocoding API."""
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city_name, "key": GOOGLE_API_KEY}
    res = requests.get(geocode_url, params=params).json()
    if res["status"] != "OK":
        return None
    location = res["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]

def fetch_popular_attractions(location: str, radius=5000, max_results=10):
    """Use Google Places API to fetch nearby tourist attractions."""
    coords = get_coordinates(location)
    if not coords:
        return [{"error": "Couldn't determine coordinates for that location."}]

    lat, lng = coords
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "tourist_attraction",
        "key": GOOGLE_API_KEY
    }

    res = requests.get(url, params=params).json()
    if res["status"] != "OK":
        return [{"error": f"API Error: {res['status']}"}]

    attractions = res.get("results", [])[:max_results]
    results = []

    for place in attractions:
        results.append({
            "name": place.get("name"),
            "lat": place["geometry"]["location"]["lat"],
            "lng": place["geometry"]["location"]["lng"],
            "address": place.get("vicinity"),
            "type": place.get("types", []),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
        })

    return results

@tool
def get_popular_attractions(location: str) -> list:
    """
    Gets top-rated popular attractions in a city.

    Args:
        location: City name (e.g., "Los Angeles")

    Returns:
        A list of attractions (max 5), each with name, rating, user ratings, and category,
        including latitude and longitude.
    """
    coords = get_coordinates(location)
    if not coords:
        return [{"error": "Could not determine coordinates."}]

    lat, lng = coords
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 5000,
        "type": "tourist_attraction",
        "key": GOOGLE_API_KEY
    }

    res = requests.get(url, params=params).json()
    if res["status"] != "OK":
        return [{"error": f"API Error: {res['status']}"}]

    attractions = res.get("results", [])

    filtered = []
    for a in attractions:
        rating = a.get("rating", 0)
        reviews = a.get("user_ratings_total", 0)
        if rating >= 4.2 and reviews >= 50:
            loc = a["geometry"]["location"]
            if "photos" in a:
                photo_ref = a["photos"][0]["photo_reference"]
                image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={GOOGLE_API_KEY}"
            else:
                image_url = None
            filtered.append({
                "name": a.get("name"),
                "lat": loc["lat"],             # ✅ added
                "lng": loc["lng"],             # ✅ added
                "rating": rating,
                "reviews": reviews,
                "category": ", ".join(a.get("types", [])[:2]),
                "image": image_url,
                "maps_url": f"https://www.google.com/maps/place/?q=place_id:{a['place_id']}"

            })

    collected_results["attractions"] = filtered[:6]
    return filtered[:6]

