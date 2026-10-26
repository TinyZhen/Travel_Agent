"""Offline sample data used in demo mode (no API keys) and in the evaluation.

Landmark names and coordinates are real; hotel names, prices, flights and events
are illustrative samples and are labelled `"source": "demo"` everywhere.
"""

CITIES = {
    "new york": {"name": "New York", "iata": "JFK", "city_code": "NYC", "lat": 40.7128, "lng": -74.0060, "tz": "America/New_York"},
    "chicago": {"name": "Chicago", "iata": "ORD", "city_code": "CHI", "lat": 41.8781, "lng": -87.6298, "tz": "America/Chicago"},
    "washington": {"name": "Washington DC", "iata": "DCA", "city_code": "WAS", "lat": 38.9072, "lng": -77.0369, "tz": "America/New_York"},
    "montreal": {"name": "Montreal", "iata": "YUL", "city_code": "YMQ", "lat": 45.5019, "lng": -73.5674, "tz": "America/Toronto"},
    "san francisco": {"name": "San Francisco", "iata": "SFO", "city_code": "SFO", "lat": 37.7749, "lng": -122.4194, "tz": "America/Los_Angeles"},
    "boston": {"name": "Boston", "iata": "BOS", "city_code": "BOS", "lat": 42.3601, "lng": -71.0589, "tz": "America/New_York"},
    "detroit": {"name": "Detroit", "iata": "DTW", "city_code": "DTT", "lat": 42.3314, "lng": -83.0458, "tz": "America/Detroit"},
    "philadelphia": {"name": "Philadelphia", "iata": "PHL", "city_code": "PHL", "lat": 39.9526, "lng": -75.1652, "tz": "America/New_York"},
}

CITY_ALIASES = {
    "nyc": "new york", "new york city": "new york", "manhattan": "new york",
    "dc": "washington", "washington dc": "washington", "washington d.c.": "washington",
    "sf": "san francisco", "bay area": "san francisco", "philly": "philadelphia",
    "chi": "chicago", "motor city": "detroit",
}

# A US state is not a destination we can plan; ask which city (with a few suggestions).
US_STATES = {
    "alabama": [], "alaska": ["Anchorage"], "arizona": ["Phoenix", "Sedona", "Tucson"], "arkansas": [],
    "california": ["San Francisco", "Los Angeles", "San Diego"], "colorado": ["Denver", "Boulder"],
    "connecticut": ["New Haven", "Hartford"], "delaware": [], "florida": ["Miami", "Orlando", "Tampa"],
    "georgia": ["Atlanta", "Savannah"], "hawaii": ["Honolulu"], "idaho": [], "illinois": ["Chicago"],
    "indiana": ["Indianapolis"], "iowa": [], "kansas": [], "kentucky": ["Louisville"], "louisiana": ["New Orleans"],
    "maine": ["Portland, ME"], "maryland": ["Baltimore"], "massachusetts": ["Boston", "Salem"],
    "michigan": ["Detroit", "Ann Arbor", "Grand Rapids"], "minnesota": ["Minneapolis"], "mississippi": [],
    "missouri": ["St. Louis", "Kansas City"], "montana": [], "nebraska": [], "nevada": ["Las Vegas"],
    "new hampshire": [], "new jersey": [], "new mexico": ["Santa Fe"], "north carolina": ["Charlotte", "Asheville"],
    "north dakota": [], "ohio": ["Cleveland", "Columbus"], "oklahoma": [], "oregon": ["Portland"],
    "pennsylvania": ["Philadelphia", "Pittsburgh"], "rhode island": ["Providence"], "south carolina": ["Charleston"],
    "south dakota": [], "tennessee": ["Nashville", "Memphis"], "texas": ["Austin", "Houston", "San Antonio"],
    "utah": ["Salt Lake City"], "vermont": ["Burlington"], "virginia": ["Richmond"], "washington state": ["Seattle"],
    "west virginia": [], "wisconsin": ["Milwaukee", "Madison"], "wyoming": [],
}

# Attractions that only operate in some months (first, last month).
SEASONAL = {"Chicago Architecture River Cruise": (4, 11), "Campus Martius Park ice rink": (11, 3)}

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
    "detroit": [
        ("Detroit Institute of Arts", 42.3594, -83.0645, ["museum", "art"], True, 20, 2.5),
        ("The Henry Ford Museum of American Innovation", 42.3036, -83.2336, ["museum", "history", "science"], True, 32, 3),
        ("Motown Museum", 42.3640, -83.0884, ["museum", "music", "history"], True, 20, 1.5),
        ("Guardian Building", 42.3297, -83.0459, ["architecture", "history"], True, 0, 1),
        ("Eastern Market", 42.3471, -83.0410, ["food", "shopping"], False, 15, 1.5),
        ("Campus Martius Park ice rink", 42.3317, -83.0466, ["outdoors", "family", "winter"], False, 15, 1.5),
        ("Detroit Riverwalk", 42.3293, -83.0398, ["outdoors", "nature"], False, 0, 1.5),
        ("Belle Isle Conservatory & Aquarium", 42.3388, -82.9861, ["nature", "family"], True, 0, 2),
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

# Major US/Canada airports (IATA, lat, lng) for finding the nearest airport to any city.
AIRPORTS = [
    ("ATL", 33.64, -84.43), ("BOS", 42.37, -71.01), ("BWI", 39.18, -76.67), ("CLE", 41.41, -81.85),
    ("CLT", 35.21, -80.94), ("CMH", 39.998, -82.89), ("CVG", 39.05, -84.67), ("DCA", 38.85, -77.04),
    ("DEN", 39.86, -104.67), ("DFW", 32.90, -97.04), ("DTW", 42.21, -83.35), ("EWR", 40.69, -74.17),
    ("FLL", 26.07, -80.15), ("GRR", 42.88, -85.52), ("HNL", 21.32, -157.92), ("IAD", 38.95, -77.46),
    ("IAH", 29.98, -95.34), ("IND", 39.72, -86.29), ("JFK", 40.64, -73.78), ("LAS", 36.08, -115.15),
    ("LAX", 33.94, -118.41), ("LGA", 40.78, -73.87), ("MCI", 39.30, -94.71), ("MCO", 28.43, -81.31),
    ("MDW", 41.79, -87.75), ("MIA", 25.79, -80.29), ("MKE", 42.95, -87.90), ("MSP", 44.88, -93.22),
    ("MSY", 29.99, -90.26), ("ORD", 41.98, -87.90), ("PDX", 45.59, -122.60), ("PHL", 39.87, -75.24),
    ("PHX", 33.43, -112.01), ("PIT", 40.49, -80.23), ("RDU", 35.88, -78.79), ("SAN", 32.73, -117.19),
    ("SAT", 29.53, -98.47), ("SEA", 47.45, -122.31), ("SFO", 37.62, -122.38), ("SLC", 40.79, -111.98),
    ("STL", 38.75, -90.37), ("TPA", 27.98, -82.53), ("AUS", 30.19, -97.67), ("BNA", 36.12, -86.68),
    ("BUF", 42.94, -78.73), ("BUR", 34.20, -118.36), ("BTV", 44.47, -73.15), ("PWM", 43.65, -70.31),
    ("PVD", 41.72, -71.43), ("ALB", 42.75, -73.80), ("SYR", 43.11, -76.11), ("ROC", 43.12, -77.67),
    ("MHT", 42.93, -71.44), ("BDL", 41.94, -72.68), ("RIC", 37.51, -77.32), ("ORF", 36.89, -76.20),
    ("SAV", 32.13, -81.20), ("CHS", 32.90, -80.04), ("JAX", 30.49, -81.69), ("RSW", 26.54, -81.76),
    ("MEM", 35.04, -89.98), ("SDF", 38.17, -85.74), ("OKC", 35.39, -97.60), ("TUL", 36.20, -95.89),
    ("OMA", 41.30, -95.89), ("DSM", 41.53, -93.66), ("MSN", 43.14, -89.34), ("GRB", 44.48, -88.13),
    ("TVC", 44.74, -85.58), ("LAN", 42.78, -84.59), ("FNT", 42.97, -83.74), ("ABQ", 35.04, -106.61),
    ("SJC", 37.36, -121.93), ("OAK", 37.72, -122.22), ("SMF", 38.70, -121.59), ("BOI", 43.56, -116.22),
    ("ANC", 61.17, -149.99), ("ASE", 39.22, -106.87), ("EGE", 39.64, -106.92), ("JAC", 43.61, -110.74),
    ("YUL", 45.47, -73.74), ("YYZ", 43.68, -79.63), ("YVR", 49.19, -123.18), ("YOW", 45.32, -75.67),
    ("YQB", 46.79, -71.39), ("YYC", 51.13, -114.01),
]

# Specific activities a traveler can ask for: Google Maps query, search radius (km),
# typical cost per person (USD, est.), hours, tags.
ACTIVITIES = {
    "skiing": ("ski resorts", 150, 90, 4, ["skiing", "winter", "outdoors"]),
    "hiking": ("hiking trails", 80, 0, 3, ["hiking", "nature", "outdoors"]),
    "ice skating": ("ice skating rinks", 25, 15, 1.5, ["winter", "family", "outdoors"]),
    "kayaking": ("kayak rentals", 80, 50, 3, ["outdoors", "nature"]),
    "beach": ("beaches", 80, 0, 3, ["outdoors", "nature"]),
    "golf": ("golf courses", 40, 70, 4, ["outdoors"]),
    "spa": ("day spas", 20, 120, 2.5, ["spa"]),
    "snow tubing": ("snow tubing", 120, 30, 2.5, ["winter", "outdoors", "family"]),
}
ACTIVITY_WORDS = {
    "skiing": ["ski", "skiing", "snowboard", "snowboarding", "slopes"],
    "hiking": ["hike", "hiking", "trek", "trekking"],
    "ice skating": ["ice skate", "ice skating", "skating"],
    "kayaking": ["kayak", "kayaking", "canoe", "canoeing", "paddling"],
    "beach": ["beach", "beaches"],
    "golf": ["golf", "golfing"],
    "spa": ["spa"],
    "snow tubing": ["snow tubing", "tubing", "sledding"],
}
