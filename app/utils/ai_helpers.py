import re
from typing import Optional


CITY_KEYWORDS = [
    "jaipur", "delhi", "mumbai", "bangalore", "bengaluru",
    "pune", "hyderabad", "chennai", "kolkata", "ahmedabad",
    "gurgaon", "noida", "faridabad", "ghaziabad", "lucknow",
]

PROPERTY_TYPES = {
    "apartment": "Apartment",
    "flat": "Apartment",
    "villa": "Villa",
    "house": "House",
    "plot": "Plot",
    "land": "Plot",
    "office": "Office",
    "shop": "Shop",
}

AMENITY_KEYWORDS = {
    "parking": "Parking",
    "gym": "Gym",
    "pool": "Swimming Pool",
    "swimming": "Swimming Pool",
    "security": "Security",
    "lift": "Lift",
    "garden": "Garden",
    "playground": "Playground",
    "clubhouse": "Clubhouse",
}


def parse_budget(text: str) -> Optional[float]:
    text_lower = text.lower()

    lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|l\b)", text_lower)
    if lakh_match:
        return float(lakh_match.group(1)) * 100000

    crore_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:crore|cr\b)", text_lower)
    if crore_match:
        return float(crore_match.group(1)) * 10000000

    thousand_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:thousand|k\b)", text_lower)
    if thousand_match:
        return float(thousand_match.group(1)) * 1000

    plain_match = re.search(r"(?:under|below|upto|up to|max|maximum)\s+(\d{6,})", text_lower)
    if plain_match:
        return float(plain_match.group(1))

    return None


def parse_bhk(text: str) -> Optional[int]:
    match = re.search(r"(\d+)\s*(?:bhk|bedroom|bed\b|br\b)", text.lower())
    if match:
        return int(match.group(1))
    return None


def parse_city(text: str) -> Optional[str]:
    text_lower = text.lower()
    for city in CITY_KEYWORDS:
        if city in text_lower:
            return city.title()
    return None


def parse_property_type(text: str) -> Optional[str]:
    text_lower = text.lower()
    for keyword, ptype in PROPERTY_TYPES.items():
        if keyword in text_lower:
            return ptype
    return None


def parse_amenities(text: str) -> list:
    text_lower = text.lower()
    found = []
    for keyword, amenity in AMENITY_KEYWORDS.items():
        if keyword in text_lower and amenity not in found:
            found.append(amenity)
    return found


def extract_filters(text: str) -> dict:
    filters = {}

    bhk = parse_bhk(text)
    if bhk:
        filters["bhk"] = bhk

    budget = parse_budget(text)
    if budget:
        filters["max_budget"] = budget

    city = parse_city(text)
    if city:
        filters["city"] = city

    ptype = parse_property_type(text)
    if ptype:
        filters["property_type"] = ptype

    amenities = parse_amenities(text)
    if amenities:
        filters["amenities"] = amenities

    if "parking" in text.lower():
        filters["parking"] = True

    return filters


def build_reply(filters: dict, count: int) -> str:
    if count == 0:
        return "Sorry, I couldn't find any properties matching your criteria. Try adjusting the filters."

    parts = []
    if "bhk" in filters:
        parts.append(f"{filters['bhk']} BHK")
    if "property_type" in filters:
        parts.append(filters["property_type"])
    if "city" in filters:
        parts.append(f"in {filters['city']}")
    if "max_budget" in filters:
        parts.append(f"under ₹{int(filters['max_budget']):,}")

    summary = " ".join(parts) if parts else "your criteria"
    return f"I found {count} matching properties ({summary})."


def estimate_price(base_price_per_sqft: float, area: float, bhk: int,
                   age: int, city_factor: float = 1.0) -> float:
    base = base_price_per_sqft * area * city_factor

    bhk_bonus = 1 + (bhk - 2) * 0.05
    age_depreciation = max(0.7, 1 - (age * 0.02))

    estimated = base * bhk_bonus * age_depreciation
    return round(estimated, -3)