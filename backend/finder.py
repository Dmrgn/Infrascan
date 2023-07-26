# utilities for interacting with the gmaps api
import googlemaps
import math
import json

from constants import *
import filer

with open("./data/keys.json") as f:
    gmaps_api_key = json.load(f)["gmaps"]

gmaps = googlemaps.Client(key=gmaps_api_key)

# takes an array of geocodes and returns 
# a subset of the passed array that has
# all geocodes at least (distance) apart from
# each other
def filter_geocodes(geocodes, distance=0.5):
    valid_geocodes = []
    for geocode in geocodes:
        is_valid_geocode = True
        index = 0
        while is_valid_geocode and index < len(valid_geocodes):
            if geo_distance(
                (valid_geocodes[index]["g"]["lat"], valid_geocodes[index]["g"]["lng"]), 
                (geocode["g"]["lat"], geocode["g"]["lng"])) < distance:
                is_valid_geocode = False
                break
            index += 1
        if is_valid_geocode:
            valid_geocodes.append(geocode)
    return valid_geocodes

def create_map_url(geocode, analysis):
    # Define the parameters for the static map image
    center = (geocode["g"]["lat"], geocode["g"]["lng"])  # Replace with the coordinates of the center of the map
    zoom = 14.8  # Specify the zoom level (1 to 20, where 1 shows the whole world and 20 is close-up)
    size = (1000, 1000)  # Set the size of the image in pixels (width, height)
    map_type = 'roadmap'  # Choose the type of map ('roadmap', 'satellite', 'terrain', or 'hybrid')

    markers = {}
    for category in analysis["results"]:
        # too many markers bugs it out 
        if category["description"] == "transit" or category["description"] == "shopping":
            continue 
        markers[category["description"]] = []
        for place in category["results"]:
            markers[category["description"]].append({
                "lat": place["g"]["lat"],
                "lng": place["g"]["lng"],
                "type": category["description"],
            })
    # start of im tired code
    markers["home"] = []
    markers["home"].append({
        "lat": geocode["g"]["lat"],
        "lng": geocode["g"]["lng"],
        "type": "home"
    })
    # end of im tired code

    # maps the category to the icon on the generated map
    color_codes = {
        "grocery":"https://img.icons8.com/offices/30/ingredients.png",
        "community center":"https://img.icons8.com/offices/30/children.png",
        "park":"https://img.icons8.com/offices/30/park-bench.png",
        "school":"https://img.icons8.com/offices/30/school.png",
        "restaurant":"https://img.icons8.com/offices/30/restaurant-pickup.png",
        "shopping":"https://img.icons8.com/offices/30/cash-register.png",
        "transit":"https://img.icons8.com/offices/30/train.png",
        "home":"https://img.icons8.com/offices/30/cottage.png"
    }
   
    # Generate the URL for the static map image
    static_map_url = f'https://maps.googleapis.com/maps/api/staticmap?center={center[0]},{center[1]}&zoom={zoom}&size={size[0]}x{size[1]}&maptype={map_type}'
    for key, value in markers.items():
        static_map_url += f"&markers=icon:{color_codes[key]}"
        for item in value:
            static_map_url += f"|{item['lat']},{item['lng']}"
    static_map_url += "&key="+gmaps_api_key
    return static_map_url

# fetches the geocode data from a list of addresses
# and saves it to the geocodes file
def addresses_to_geocodes():  
    addresses = filer.open_msgpack("addresses")
    geocodes = []
    num = 0
    for address in addresses:
        num+=1
        print("Processing address: " + str(num) + "/" + str(len(addresses)) + " " + address)
        # get geocode of address
        geocode_data = gmaps.geocode(address)
        # skip bad results
        if len(geocode_data) == 0:
            continue
        # add to array
        geocodes.append({
            "a":geocode_data[0]["formatted_address"],
            "g":{
                "lat":geocode_data[0]["geometry"]["location"]["lat"],
                "lng":geocode_data[0]["geometry"]["location"]["lng"]
            },
        })
    print("Saving")
    filer.save_msgpack("geocodes", geocodes)

# analyze the specified geocode based
# on the google maps api results from
# the specified search term
def analyze_geocode_with_term(geocode, term):
    places_nearby = gmaps.places_nearby(location=(geocode["g"]["lat"], geocode["g"]["lng"]), radius=1000, keyword=term)["results"]
    results = []
    total_score = 0
    # take the first 3 places for analysis
    for i in range(min(len(places_nearby), 3)):
        results.append({
            "name": places_nearby[i]["name"],
            "distance": geo_distance((geocode["g"]["lat"], geocode["g"]["lng"]), (places_nearby[i]["geometry"]["location"]["lat"], places_nearby[i]["geometry"]["location"]["lng"])),
            "g": {
                "lat":places_nearby[i]["geometry"]["location"]["lat"],
                "lng":places_nearby[i]["geometry"]["location"]["lng"]
            },
            "rating":3 if places_nearby[i]["rating"] == 0 else places_nearby[i]["rating"],
            "types":[x for x in places_nearby[i]["types"]],
            "score": 0
        })
        results[-1]["score"] = (results[-1]["rating"]/5)/min(max(results[-1]["distance"], 0.1), 1)
        total_score += results[-1]["score"]
    return {
        "score": total_score,
        "description": term,
        "results":results
    }

# get information from the gmaps api about the
# specified geocode and return it as a python object
def analyze(geocode):
    # get results in the following stats
    search_terms = [
        "grocery",
        "community center",
        "park",
        "shopping",
        "transit",
        "school",
        "restaurant"
    ]
    results = []
    score = 0
    # analyze each category and add to total score
    # keep track of analysis data for later
    for term in search_terms:
        results.append(analyze_geocode_with_term(geocode, term))
        score += results[-1]["score"]
    return {
        "results": results,
        "score": min((score/7)*20, 100) # make score between 0-100 (kinda abitrary values after experimentation)
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