from datetime import timedelta
import os
import requests
from dotenv import load_dotenv
from smolagents import tool
from collector import collected_results

load_dotenv()
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")

def fetch_ticketmaster_events(location: str, keyword: str = "", size: int = 5) -> str:
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "keyword": keyword,
        "size": size,
        "city": location,
        "sort": "date,asc"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"

    data = response.json()
    events = data.get("_embedded", {}).get("events", [])

    if not events:
        return "No events found."

    results = []
    for event in events:
        name = event["name"]
        date = event["dates"]["start"].get("localDate", "No date")
        time = event["dates"]["start"].get("localTime", "No time")
        url = event["url"]
        venue = event["_embedded"]["venues"][0].get("name", "Unknown venue")
        results.append(f"- {name} at {venue} on {date} {time} → {url}")

    return "\n".join(results)

@tool
def search_ticketmaster_events(location: str, date: str, keyword: str = "") -> list:
    """
    Search Ticketmaster for events in a city on a specific date.

    Args:
        location: City name (e.g., "Boston")
        date: Date string in YYYY-MM-DD format
        keyword: Optional keyword (e.g., "music")

    Returns:
        List of events: name, date, venue, and url
    """
    from datetime import datetime

    # Convert "YYYY-MM-DD" to ISO8601 datetime string (start of that day)
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return [{"error": "Invalid date format. Use YYYY-MM-DD"}]

    start_dt = parsed_date.strftime("%Y-%m-%dT00:00:00-05:00")
    end_dt = (parsed_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00-05:00")

    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "keyword": keyword,
        "size": 10,
        "city": location,
        "startDateTime": start_dt,
        "sort": "date,asc"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return [{"error": f"Ticketmaster API Error {response.status_code}"}]

    events = response.json().get("_embedded", {}).get("events", [])
    results = []

    for event in events:
        name = event.get("name", "Unknown Event")
        date_info = event.get("dates", {}).get("start", {})
        date_str = date_info.get("localDate", "No Date")
        time_str = date_info.get("localTime", "")
        venue = event.get("_embedded", {}).get("venues", [{}])[0].get("name", "Unknown Venue")
        url = event.get("url", "#")

        results.append({
            "name": name,
            "date": f"{date_str} {time_str}".strip(),
            "venue": venue,
            "url": url,
            "image": event.get("images", [{}])[0].get("url", "")
        })
    collected_results["events"] = results[:6]
    return results[:6]

