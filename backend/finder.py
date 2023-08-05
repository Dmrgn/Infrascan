# utilities for interacting with the gmaps api and analyzing the results
import googlemaps
import math
import json
import urllib
import requests
from bs4 import BeautifulSoup as bs

from constants import *

with open("./data/keys.json") as f:
    data = json.load(f)
    gmaps_api_key = data["gmaps"]
    mapbox_api_key = data["mapbox"]

gmaps = googlemaps.Client(key=gmaps_api_key)

def address_to_formatted_geocode(address, include_region_info=False):
    geocode = requests.get(f"https://api.mapbox.com/geocoding/v5/mapbox.places/{urllib.parse.quote(address)}.json?access_token={mapbox_api_key}").json()
    geocode = geocode["features"][0]
    data = {
        "a":geocode["place_name"],
        "g":{
            "lat":geocode["center"][1],
            "lng":geocode["center"][0]
        },
    }
    if include_region_info:
        data["region"] = f'{geocode["context"][-3]["text"]}, {geocode["context"][-2]["text"]}, {geocode["context"][-1]["text"]}'
    return data

def create_map_url(geocode, analysis):
    # define the parameters for the static map image
    center = (geocode["g"]["lat"], geocode["g"]["lng"])
    zoom = 14.8  # specify the zoom level (1 to 20, where 1 shows the whole world and 20 is close-up)
    size = (1000, 1000)  # set the size of the image in pixels (width, height)
    map_type = 'roadmap' # choose the type of map ('roadmap', 'satellite', 'terrain', or 'hybrid')

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
        return None
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
        place_geocode = address_to_formatted_geocode(f"{place_address}, {origin_geocode['region']}")
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
        place_geocode = address_to_formatted_geocode(f"{place_name},{' '+place_description+', ' if not place_description is None else ''} {origin_geocode['region']}")
    # set the address to be the more accurate geocode 
    # address as opposed to the webscraped address
    place_address = place_geocode["a"]
    # get distance to origin
    place_distance = geo_distance((place_geocode["g"]["lat"], place_geocode["g"]["lng"]), (origin_geocode["g"]["lat"], origin_geocode["g"]["lng"]))
    # only keep results within 1.5km
    if place_distance > 2:
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

# web scrape google search of the passed
# query for place results
def get_place_results_from_query(query):
    q = urllib.parse.quote(query)
    search_url = f"https://www.google.ca/search?q={q}"
    # ask google for the link to see more places
    search_results = requests.get(search_url).text
    search_soup = bs(search_results, features="html.parser")
    # find html elements describing place results
    places_list = search_soup.select("#main>div>div>div>a>div>div")[:3] # take the first 3
    return places_list

# web scrape for information about places matching 
# the specified search term nearby the specified
# address. Alternative to using (and paying for) the
# gmaps places nearby api
def analyze_address_with_term(geocode, term):
    # create search url
    shortened_address= geocode['a'].split(',')[0]
    search_queries = [query.format(term=term, shortened_address=shortened_address, geocode_region=geocode["region"]) for query in SEARCH_QUERIES]
    places_list = []
    # perform each query and collect place results
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
        results.append(analyze_address_with_term(geocode, term))
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