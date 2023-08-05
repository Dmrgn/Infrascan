# utilities for interacting with the gmaps api and analyzing the results
import googlemaps
import math
import json
import urllib
import requests
from bs4 import BeautifulSoup as bs

from constants import *
import filer

with open("./data/keys.json") as f:
    data = json.load(f)
    gmaps_api_key = data["gmaps"]
    mapbox_api_key = data["mapbox"]

gmaps = googlemaps.Client(key=gmaps_api_key)

def address_to_formatted_geocode_mapbox(address, extra_info=False):
    geocode = requests.get(f"https://api.mapbox.com/geocoding/v5/mapbox.places/{urllib.parse.quote(address)}.json?access_token={mapbox_api_key}").json()
    geocode = geocode["features"][0]
    data = {
        "a":geocode["place_name"],
        "g":{
            "lat":geocode["center"][1],
            "lng":geocode["center"][0]
        },
    }
    if extra_info:
        data["region"] = f'{geocode["context"][-3]["text"]}, {geocode["context"][-2]["text"]}, {geocode["context"][-1]["text"]}'
    print("\t", address, data["a"])
    return data

def address_to_formatted_geocode(address):
    geocode = gmaps.geocode(address)[0]
    return {
        "a":geocode["formatted_address"],
        "g":{
            "lat":geocode["geometry"]["location"]["lat"],
            "lng":geocode["geometry"]["location"]["lng"]
        },
    }

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
    # define the parameters for the static map image
    center = (geocode["g"]["lat"], geocode["g"]["lng"])
    zoom = 14.8  # specify the zoom level (1 to 20, where 1 shows the whole world and 20 is close-up)
    size = (1000, 1000)  # set the size of the image in pixels (width, height)
    map_type = 'roadmap' # choose the type of map ('roadmap', 'satellite', 'terrain', or 'hybrid')

    # start of im tired code
    markers = {}
    for category in analysis["results"]:
        # too many custom markers bugs it out according to the docs
        if category["description"] == "transit" or category["description"] == "park":
            continue 
        markers[category["description"]] = []
        for place in category["results"]:
            markers[category["description"]].append({
                "lat": place["g"]["lat"],
                "lng": place["g"]["lng"],
                "type": category["description"],
            })
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
        # get formatted geocode of address
        geocodes.append(address_to_formatted_geocode_mapbox(address))
    print("Saving")
    filer.save_msgpack("geocodes", geocodes)

# analyze the specified geocode based
# on the google maps api results from
# the specified search term
def analyze_geocode_with_term(geocode, term):
    places_nearby = gmaps.places_nearby(location=(geocode["g"]["lat"], geocode["g"]["lng"]), radius=1000, keyword=term)["results"]
    results = []
    term_score = 0
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
        term_score += results[-1]["score"]
    return {
        "score": term_score,
        "description": term,
        "results":results
    }

# web scrape for information about places matching 
# the specified search term nearby the specified
# address. Alternative to using (and paying for) the
# gmaps places nearby api
def analyze_address_with_term_no_gmaps(geocode, term):
    # create search url
    q = urllib.parse.quote(f"{term} near {geocode['a']}")
    search_url = f"https://www.google.ca/search?q={q}"
    # ask google for nearby locations
    search_results = requests.get(search_url).text
    with open("test.html", "w") as f:
        f.write(search_results)
    search_soup = bs(search_results, features="html.parser")
    # find html elements describing place results
    places_list = search_soup.select("#main>div>div>div>a>div>div")[:3]
    results = []
    term_score = 0
    for place in places_list:
        try:
            # get address of this place and geocode
            place_name = place.contents[0].select("h3>div")[0].text
            try:
                place_address = place.contents[1].select("div")[0].contents[2].text.split("\u22c5")[1].strip()
            except:
                place_address = place_name + ", " + geocode["region"]
            place_geocode = address_to_formatted_geocode_mapbox(place_address)
            distance = geo_distance((geocode["g"]["lat"], geocode["g"]["lng"]), (place_geocode["g"]["lat"], place_geocode["g"]["lng"]))
            if distance > 1.5:
                # keep only results that are < 1.5 km away
                continue
            try:
                rating = float(place.contents[1].select("div>span")[0].contents[1].text)
            except:
                rating = 3
            results.append({
                "name": place_name,
                "distance": distance,
                "g": {
                    "lat":place_geocode["g"]["lat"],
                    "lng":place_geocode["g"]["lng"]
                },
                "rating": rating,
                "types":[term],
                "score": 0
            })
            results[-1]["score"] = (results[-1]["rating"]/5)/min(max(results[-1]["distance"], 0.1), 1)
            term_score += results[-1]["score"]
        except:
            continue
    return {
        "score": term_score,
        "description": term,
        "results":results
    }

# interpret and find information about a place defined
# by the passed block of html which was scraped from 
# a webpage
def understand_place(search_term, origin_geocode, place, visited_place_names):
    # ensure the place is not empty, an ad,
    # or a prompt to search for more places
    place_string = str(place)
    if len(place_string) == 0 or place_string.find("More places") != -1 or len(place.contents) == 1:
        return None
    # search for characteristics of the place
    try: place_name = place.select(".BNeawe.deIvCb.AP7Wnd")[0].text
    except: 
        return None
    # check if this place name has already been visited
    if place_name in visited_place_names:
        print("\t", place_name, " already found")
        return None
    print(place_name)
    # add to visited list
    visited_place_names.add(place_name)
    try: place_rating = float(place.select("span.oqSTJd")[0].text)
    except:
        place_rating = 3
    try: 
        # look for the address after a "⋅"
        dot_split = place.select(".BNeawe.tAd8D.AP7Wnd")[0].text.split("⋅")
        if dot_split[1].find("$") != -1:
            # if [0] is a price rating, then look for [1]
            dot_split = dot_split[2]
        else:
            dot_split = dot_split[1]
        # scan until the start of some other data
        enders = ["<", ".", "\n", "Open", "Clos"]
        for ender in enders:
            if dot_split.find(ender) != -1:
                dot_split = dot_split[:dot_split.find(ender)]
        place_address = dot_split.strip()
        # ensure this is not empty
        if len(place_address) == 0:
            raise Exception()
        # get geocode info based on address
        place_geocode = address_to_formatted_geocode_mapbox(f"{place_address}, {origin_geocode['region']}")
    except:
        # get the description of the place if it is available
        try:
            place_description = place.select(".BNeawe.tAd8D.AP7Wnd")[0].text
            # if there is a tag present and this isnt just text
            if place_description.find("<") != -1:
                raise Exception()
        except:
            place_description = None
        # try to use geocoding to get the address
        # based off of the name of the location
        # and its available description
        place_geocode = address_to_formatted_geocode_mapbox(f"{place_name},{' '+place_description+', ' if not place_description is None else ''} {origin_geocode['region']}")
    # set the address to be the more accurate geocode 
    # address as opposed to the webscraped address
    place_address = place_geocode["a"]
    # get distance to origin
    print("\t", place_geocode["g"], origin_geocode["g"])
    place_distance = geo_distance((place_geocode["g"]["lat"], place_geocode["g"]["lng"]), (origin_geocode["g"]["lat"], origin_geocode["g"]["lng"]))
    # only keep results within 1.5km
    if place_distance > 2:
        print("\tResult was too far away at", place_distance)
        return None
    return {
        "name": place_name,
        "address": place_address,
        "distance": place_distance,
        "g": place_geocode["g"],
        "rating": place_rating,
        "types": [search_term],
        "score": (place_rating/5)/min(max(place_distance, 0.1), 1)
    }

def get_place_results_from_query(query):
    q = urllib.parse.quote(query)
    search_url = f"https://www.google.ca/search?q={q}"
    # ask google for the link to see more places
    search_results = requests.get(search_url).text
    search_soup = bs(search_results, features="html.parser")
    # # find the "more places" element
    # more_places_url = None
    # locs = search_soup.select("#main>div>div>div>a")
    # for loc in locs:
    #     if loc.attrs["href"].find("maps.google.ca") != -1:
    #         more_places_url = loc.attrs["href"]
    #         break
    # # now navigate to the more places page
    # search_results = requests.get(more_places_url).text
    # find html elements describing place results
    places_list = search_soup.select("#main>div>div>div>a>div>div")[:3] # take the first 3
    return places_list

# web scrape for information about places matching 
# the specified search term nearby the specified
# address. Alternative to using (and paying for) the
# gmaps places nearby api
# use the "more places" link generated by the first
# search page to get more results
def analyze_address_with_term_no_gmaps_large_list(geocode, term):
    # create search url
    shortened_address= geocode['a'].split(',')[0]
    search_queries = [
        f"{term} near {shortened_address}, {geocode['region']}",
        f"{term} within 2km of {shortened_address}, {geocode['region']}",
        f"{term} close to {shortened_address}, {geocode['region']}",
    ]
    places_list = []
    for search_query in search_queries:
        query_results = get_place_results_from_query(search_query)
        for place in query_results:
            places_list.append(place) 
    # set of addresses included in analysis
    # so that queries don't overlap
    visited_place_names = set()
    results = []
    term_score = 0
    # process each place result
    print(term, "=================:")
    for place in places_list:
        place_data = understand_place(term, geocode, place, visited_place_names)
        if place_data is None:
            # if there was an error processing the place html then skip it
            # or if it has already been processed
            continue
        # add score to total
        term_score += place_data["score"]
        # add this place to the list of results
        results.append(place_data)
        # exit if we already have the required number of results
        if len(results) == 3:
            break
    result = {
        "score": term_score,
        "description": term,
        "results":results
    }
    return result


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
        results.append(analyze_address_with_term_no_gmaps_large_list(geocode, term))
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