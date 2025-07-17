from smolagents import tool

@tool
def generate_trip_json(events: list, flights: list, hotels: list, attractions: list) -> dict:
    """
    Assemble a full structured trip plan into a JSON object.

    Args:
        events (list): List of event dicts (with keys: name, venue, date, url)
        flights (list): List of flight dicts (with keys: from, to, price, airline, departure_time)
        hotels (list): List of hotel dicts (with keys: name, price, rating, address, link)
        attractions (list): List of attraction dicts (with keys: name, rating, category, location)

    Returns:
        dict: Full trip plan as structured JSON
    """
    return {
        "events": events or [],
        "flights": flights or [],
        "hotels": hotels or [],
        "attractions": attractions or []
    }
