"""Offline sample data used in demo mode (no API keys) and in the evaluation.

Landmark names and coordinates are real; hotel names, prices, flights and events
are illustrative samples and are labelled `"source": "demo"` everywhere.
"""

CITIES = {
    "new york": {"name": "New York", "iata": "JFK", "city_code": "NYC", "lat": 40.7128, "lng": -74.0060, "drive_hours": 4.0},
    "chicago": {"name": "Chicago", "iata": "ORD", "city_code": "CHI", "lat": 41.8781, "lng": -87.6298, "drive_hours": 15.0},
    "washington": {"name": "Washington DC", "iata": "DCA", "city_code": "WAS", "lat": 38.9072, "lng": -77.0369, "drive_hours": 7.5},
    "montreal": {"name": "Montreal", "iata": "YUL", "city_code": "YMQ", "lat": 45.5019, "lng": -73.5674, "drive_hours": 5.0},
    "san francisco": {"name": "San Francisco", "iata": "SFO", "city_code": "SFO", "lat": 37.7749, "lng": -122.4194, "drive_hours": 45.0},
    "boston": {"name": "Boston", "iata": "BOS", "city_code": "BOS", "lat": 42.3601, "lng": -71.0589, "drive_hours": 0.0},
    "philadelphia": {"name": "Philadelphia", "iata": "PHL", "city_code": "PHL", "lat": 39.9526, "lng": -75.1652, "drive_hours": 5.0},
}

CITY_ALIASES = {
    "nyc": "new york", "new york city": "new york", "manhattan": "new york",
    "dc": "washington", "washington dc": "washington", "washington d.c.": "washington",
    "sf": "san francisco", "bay area": "san francisco", "philly": "philadelphia",
    "chi": "chicago",
}

# name, lat, lng, tags, indoor, cost per person (USD), hours
ATTRACTIONS = {
    "new york": [
        ("Metropolitan Museum of Art", 40.7794, -73.9632, ["museum", "art"], True, 30, 3),
        ("Central Park", 40.7829, -73.9654, ["nature", "outdoors"], False, 0, 2),
        ("Statue of Liberty & Ellis Island", 40.6892, -74.0445, ["history", "landmark"], False, 25, 4),
        ("American Museum of Natural History", 40.7813, -73.9740, ["museum", "science", "family"], True, 28, 3),
        ("The High Line", 40.7480, -74.0048, ["outdoors", "architecture"], False, 0, 1.5),
        ("Brooklyn Bridge", 40.7061, -73.9969, ["landmark", "outdoors"], False, 0, 1.5),
        ("Museum of Modern Art", 40.7614, -73.9776, ["museum", "art"], True, 30, 2.5),
        ("Chelsea Market", 40.7424, -74.0060, ["food", "shopping"], True, 20, 1.5),
    ],
    "chicago": [
        ("Art Institute of Chicago", 41.8796, -87.6237, ["museum", "art"], True, 32, 3),
        ("Millennium Park & Cloud Gate", 41.8826, -87.6226, ["landmark", "outdoors"], False, 0, 1.5),
        ("Chicago Architecture River Cruise", 41.8888, -87.6233, ["architecture", "history"], False, 52, 1.5),
        ("Field Museum", 41.8663, -87.6170, ["museum", "science", "family"], True, 30, 3),
        ("Navy Pier", 41.8917, -87.6086, ["family", "outdoors"], False, 0, 2),
        ("Shedd Aquarium", 41.8676, -87.6140, ["family", "nature"], True, 45, 2.5),
        ("Lincoln Park Zoo", 41.9211, -87.6340, ["nature", "family", "outdoors"], False, 0, 2),
    ],
    "washington": [
        ("National Mall & Lincoln Memorial", 38.8893, -77.0502, ["history", "landmark", "outdoors"], False, 0, 2.5),
        ("Smithsonian National Air and Space Museum", 38.8882, -77.0199, ["museum", "science", "family"], True, 0, 3),
        ("Smithsonian National Museum of Natural History", 38.8913, -77.0261, ["museum", "science"], True, 0, 2.5),
        ("U.S. Capitol Visitor Center", 38.8899, -77.0091, ["history", "architecture"], True, 0, 1.5),
        ("National Gallery of Art", 38.8913, -77.0199, ["museum", "art"], True, 0, 2),
        ("Georgetown Waterfront", 38.9020, -77.0590, ["food", "outdoors"], False, 15, 2),
    ],
    "montreal": [
        ("Old Montreal (Vieux-Montréal)", 45.5075, -73.5540, ["history", "architecture", "food"], False, 0, 2.5),
        ("Notre-Dame Basilica", 45.5045, -73.5560, ["history", "architecture"], True, 15, 1),
        ("Mount Royal Park", 45.5048, -73.5874, ["nature", "outdoors"], False, 0, 2),
        ("Montreal Museum of Fine Arts", 45.4985, -73.5794, ["museum", "art"], True, 24, 2.5),
        ("Jean-Talon Market", 45.5363, -73.6146, ["food", "shopping"], False, 15, 1.5),
        ("Montreal Biodome", 45.5597, -73.5497, ["family", "nature", "science"], True, 22, 2),
    ],
    "san francisco": [
        ("Golden Gate Bridge", 37.8199, -122.4783, ["landmark", "outdoors"], False, 0, 1.5),
        ("Alcatraz Island", 37.8270, -122.4230, ["history"], False, 45, 3),
        ("California Academy of Sciences", 37.7699, -122.4661, ["museum", "science", "family"], True, 45, 3),
        ("Ferry Building Marketplace", 37.7955, -122.3937, ["food", "shopping"], True, 20, 1.5),
        ("SFMOMA", 37.7857, -122.4011, ["museum", "art"], True, 30, 2.5),
        ("Golden Gate Park", 37.7694, -122.4862, ["nature", "outdoors"], False, 0, 2),
    ],
    "boston": [
        ("Freedom Trail", 42.3550, -71.0656, ["history", "outdoors"], False, 0, 2.5),
        ("Museum of Fine Arts, Boston", 42.3394, -71.0940, ["museum", "art"], True, 27, 3),
        ("New England Aquarium", 42.3591, -71.0493, ["family", "nature"], True, 38, 2),
        ("Faneuil Hall Marketplace", 42.3600, -71.0568, ["food", "shopping", "history"], True, 15, 1.5),
        ("Boston Public Garden", 42.3541, -71.0702, ["nature", "outdoors"], False, 0, 1),
    ],
    "philadelphia": [
        ("Independence Hall & Liberty Bell", 39.9489, -75.1500, ["history", "landmark"], True, 0, 2),
        ("Philadelphia Museum of Art", 39.9656, -75.1810, ["museum", "art"], True, 30, 3),
        ("Reading Terminal Market", 39.9533, -75.1590, ["food", "shopping"], True, 20, 1.5),
        ("The Franklin Institute", 39.9582, -75.1731, ["museum", "science", "family"], True, 33, 3),
        ("Fairmount Park", 39.9890, -75.2000, ["nature", "outdoors"], False, 0, 2),
    ],
}

# tier, name suffix, nightly price, rating
HOTEL_TIERS = [
    ("budget", "Hostel & Pods", 75, 4.0),
    ("budget", "Express Inn", 129, 3.8),
    ("mid", "Central Hotel", 219, 4.3),
    ("mid", "Riverside Suites", 249, 4.4),
    ("luxury", "Grand Plaza", 459, 4.7),
]

# weekday (0=Mon), title, tags, price, start time
EVENTS = [
    (4, "Friday Night Jazz", ["music", "nightlife"], 35, "20:00"),
    (5, "Saturday Farmers & Makers Market", ["food", "shopping", "family"], 0, "10:00"),
    (5, "Indie Rock Showcase", ["music", "nightlife"], 45, "21:00"),
    (6, "Sunday Afternoon Symphony", ["music", "art"], 60, "15:00"),
    (2, "Comedy Club Open Mic", ["comedy", "nightlife"], 15, "19:30"),
    (3, "Museum Late Night", ["art", "museum"], 0, "18:00"),
]

AIRLINES = ["JetBlue", "Delta Air Lines", "American Airlines", "United Airlines"]
