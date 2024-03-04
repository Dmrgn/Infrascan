# utilities for interacting with the gmaps api and analyzing the results
import math
import json
import urllib
import requests

from constants import *
import overpass
import chat
import cache
import database
import stats

with open("./data/keys.json") as f:
    data = json.load(f)
    mapbox_api_key = data["mapbox"]

# performs entire analysis on the passed
# address and returns it
def analyze(address, secret, email, use_text=True):
    # get geocode of the address
    geocode = address_to_geocode(address)

    # check cache for existing data
    cache_data = cache.get_address_data(geocode["a"])
    if cache_data != None:
        cache_data["wasCached"] = True
        cache_data["stats"] = stats.get_stats(email)["stats"]
        return cache_data

    # charge the user a token
    use_token_response = database.use_token(secret)
    if use_token_response["error"] != None:
        return use_token_response

    # perform analysis
    analysis = overpass.analyze_geocode(geocode["g"])

    # format analysis for turbo gpt
    formatted_analysis = chat.format_prompt_with_analysis(analysis)
    # ask turbo gpt for human readable analysis
    generated_text = chat.generate_response(geocode["a"], formatted_analysis)
    # break giant string into sections for the frontend
    formatted_generated_text = chat.format_generated_text(generated_text)

    # add the search term to the list of 
    # things the user has searched
    stats.append_stat(email, "searches", address)
    
    # return formatted analysis
    # see ./data/sample_response.json for more details
    response = {
        "score": analysis["score"],
        "results": analysis,
        "overview": formatted_generated_text["overview"],
        "text": formatted_generated_text["text"],
        "location": geocode,
    }
    
    # add to cache
    if cache_data == None:
        cache.add_address_data(geocode["a"], response)

    # append user stats
    response["stats"] = stats.get_stats(email)["stats"]
    return response

# converts the passed address into a geocode using the mapbox api
def address_to_geocode(address):
    geocode = requests.get(f"https://api.mapbox.com/geocoding/v5/mapbox.places/{urllib.parse.quote(address)}.json?access_token={mapbox_api_key}").json()
    print(geocode)
    geocode = geocode["features"][0]
    data = {
        "a":geocode["place_name"],
        "g":(geocode["center"][1], geocode["center"][0])
    }
    return data