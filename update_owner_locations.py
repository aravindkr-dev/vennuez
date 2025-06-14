import requests
from app import app, db
from models import Owner

def geocode_address(address):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data and len(data) > 0:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
    return None, None

with app.app_context():
    owners = Owner.query.all()
    for owner in owners:
        if owner.address and (owner.latitude is None or owner.longitude is None):
            lat, lon = geocode_address(owner.address)
            if lat and lon:
                print(f"Updating {owner.gaming_center_name} ({owner.address}) to lat={lat}, lon={lon}")
                owner.latitude = lat
                owner.longitude = lon
                db.session.commit()
            else:
                print(f"Could not geocode address for {owner.gaming_center_name}: {owner.address}") 