import overpy
import urllib
import requests
import json
import math

from constants import *

api = overpy.Overpass()

factors = {
    "grocery": ['"shop"="supermarket"', '"shop"="greengrocer"'],
    "park": ['"leisure"="park"'],
    "community center": ['"amenity"="community_centre"'],
    "shopping": ['"shop"="department_store"', '"shop"="clothes"', '"shop"="hardware"', '"shop"="mall"'],
    "transit": ['"highway"="bus_stop"'],
    "school": ['"amenity"="school"'],
    "restaurant": ['"amenity"="restaurant"'],
}

factor_weights = {
    "grocery": 0.2,
    "park": 0.2,
    "community center": 0.05,
    "shopping": 0.05,
    "transit": 0.2,
    "school": 0.2,
    "restaurant": 0.1,
}

individual_factor_weights = {
    "grocery": 1.25,
    "park": 1.25,
    "community center": 2,
    "shopping": 1.5,
    "transit": 1.5,
    "school": 1.5,
    "restaurant": 1.5,
}

def get_overpass_factor_results(distance, factor, geocode, depth):
    if len(factor) == 1:
        tag_query = factor[0]
    else:
        tag_query = f"{factor[0].split('=')[0]}~" + "\"" + "|".join([item.split("=")[1].replace("\"", "") for item in factor]) + "\""
    query = urllib.parse.quote(f"""
    [out:json][timeout:25];
    nwr(around:{distance}, {geocode[0]}, {geocode[1]})[{tag_query}];
    out geom;
    """)
    result = requests.get(f"https://overpass-api.de/api/interpreter?data={query}").json()
    if len(result["elements"]) == 0:
        if depth == MAX_SEARCH_RADIUS_INCREASES: return result
        return get_overpass_factor_results(distance+SEARCH_RADIUS_INCREMENT, factor, geocode, depth+1)
    else:
        return result

def analyze_geocode(geocode):
    # individual restruants, communit centers etc.
    # sorted into keys base on their respective categories
    element_results = {}
    # for each factor, grocery, park, shopping etc..
    for key, factor in factors.items():
        result = get_overpass_factor_results(SEARCH_RADIUS, factor, geocode, 0)
        # for each overpass element matching the request
        for element in result["elements"]:
            element_geocode = None
            element_geometry = None
            if element["type"] == "node":
                element_geocode = {"lat": element["lat"], "lng": element["lon"]}
                element_geometry = [element_geocode]
            elif element["type"] == "way":
                element_geocode = {"lat": element["bounds"]["minlat"], "lng": element["bounds"]["minlon"]}
                element_geometry = [{"lat": latlng["lat"], "lng": latlng["lon"]} for latlng in element["geometry"]]
            else:
                # this element is a relation and we can ignore it
                continue
            tags = element["tags"]
            name = tags["name"] if "name" in tags else f"A {key} with unknown name"
            # add the element to its corresponding category in element_results
            # "key" is an element of the factors, grocery, shopping etc..
            if not key in element_results: element_results[key] = []
            element_results[key].append({
                "name": name,
                "distance": geo_distance(geocode, (element_geocode["lat"], element_geocode["lng"])),
                "g": element_geocode,
                "geometry": element_geometry
            })
    # sort elements by distance
    # and generate overall score
    score = 0
    factor_scores = {}
    for factor, elements in element_results.items():
        element_results[factor] = sorted(element_results[factor], key=lambda element: element["distance"])
        # take max 5 elements from each factor category
        factor_score = 0
        elms = element_results[factor][:5] if len(element_results[factor]) >= 5 else element_results[factor]
        for element in elms:
            factor_score += element["distance"]
        factor_score /= len(elms)
        # average element distance
        factor_score = (4**(-factor_score*(1-len(elms)/6))) * ((len(elms)/5)**(1/5))
        # weigh score based on relavence of each factor
        score+=factor_score*factor_weights[factor]
        # make factor score pretty and save it
        factor_scores[factor] = min(100, round(factor_score*100))
    score = min(100, round(score*100))
    return {
        "results": [{"factor":key, "results": elements, "score": factor_scores[key]} for key, elements in element_results.items()],
        "score": score,
    }

# gets the geological distance between two
# points (lat, lng) (approximate to ~0.5%)
def geo_distance(coord1, coord2):
    distance_lat = d2r(coord2[0] - coord1[0])
    distance_lon = d2r(coord2[1] - coord1[1])
    angle = (
        math.sin(distance_lat/2) * math.sin(distance_lat/2) +
        math.cos(d2r(coord1[0])) * math.cos(d2r(coord2[0])) *
        math.sin(distance_lon/2) * math.sin(distance_lon/2)
    )
    curve = 2 * math.atan2(math.sqrt(angle), math.sqrt(1-angle))
    return EARTH_RADIUS * curve

# converts degrees to radians
def d2r(deg):
    return deg * (math.pi/180)