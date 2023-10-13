import overpy
import urllib
import requests

from constants import *

api = overpy.Overpass()

def nearby(geocode, amenity):
    query = urllib.parse.quote(f"""
    [out:json][timeout:25];
    nwr(around:{SEARCH_RADIUS}, {geocode[0]}, {geocode[1]})["shop"="{amenity}"];
    out geom;
    """)
    result = requests.get(f"https://overpass-api.de/api/interpreter?data={query}").json()
    results = []
    for element in result["elements"]:
        geocode = None
        print("here")
        if element["type"] == "node":
            geocode = {"lat": element["lat"], "lng": element["lon"]}
        elif element["type"] == "way":
            geocode = {"lat": element["bounds"]["minlat"], "lng": element["bounds"]["minlon"]}
        else:
            print("other")
            continue
        tags = element["tags"]
        results.append({
            "name": tags["name"],
            "g": geocode,
        })
        if len(results) == 10: break
    return results


print(nearby((43.694414, -79.432297), "greengrocer"))