from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

geolocator = Nominatim(user_agent="wastetrack-app")

def get_coordinates_from_address(address: str):
    try:
        location = geolocator.geocode(address)
        if location:
            return str(location.latitude), str(location.longitude)
    except (GeocoderUnavailable, GeocoderTimedOut):
        pass
    return None, None
