# ===============================
# HOTEL BRAND INTELLIGENCE DB
# ===============================

HOTEL_BRANDS = {
    "hilton": ["hilton", "hiltonhotels", "hiltonworldwide"],
    "marriott": ["marriott", "marriotthotels", "bonvoy"],
    "hyatt": ["hyatt", "hyattworldwide"],
    "radisson": ["radisson", "radissonhotels"],
    "accor": ["accor", "all.accor", "sofitel", "ibis"],
    "ihg": ["ihg", "intercontinental", "holidayinn"],
    "four seasons": ["fourseasons", "fourseasonshotels"],
}


def detect_brand(hotel_name: str):
    """
    Detects likely hotel chain from name
    """

    name = hotel_name.lower()

    for brand, keywords in HOTEL_BRANDS.items():
        for kw in keywords:
            if kw in name:
                return brand

    return None


def get_brand_keywords(brand: str):
    return HOTEL_BRANDS.get(brand, [])
