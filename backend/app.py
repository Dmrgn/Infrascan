from flask import Flask
from flask import jsonify
from flask import request
from flask import Response

import finder
import chat
from constants import *

app = Flask(__name__)

# house_lat = 43.695770
# house_long = -79.433450

@app.route("/")
def index():
    return "Infrascan Server"

# fetch the infrascan results for an address
@app.route("/fetch")
def fetch():
    address = request.args.get("address")
    if not address:
        return "Please specify an address."
    geocode = finder.gmaps.geocode(address)[0]
    geocode = {
        "a":geocode["formatted_address"],
        "g":{
            "lat":geocode["geometry"]["location"]["lat"],
            "lng":geocode["geometry"]["location"]["lng"]
        },
    }

    # perform analysis
    analysis = finder.analyze(geocode)

    # format analysis for turbo gpt
    formatted_analysis = ""
    for result in analysis["results"]:
        formatted_analysis += "[{category}] ".format(category=result["description"])
        for item in result["results"]:
            formatted_analysis += "{name} is {distance} kilometers away with a user rating of {rating} and a community score of {score}. It is listed as being a: ".format(name=item["name"], distance=item["distance"], rating=item["rating"], score=item["score"])
            for type in item["types"]:
                formatted_analysis += "{thing},".format(thing=type)
            formatted_analysis += ". "
        formatted_analysis += "\n"
    description = chat.generate_response(geocode["a"], PROMPT.format(data=formatted_analysis)).split("\n")
    overview = description.pop(-1)
    text = []
    for x in range(0, len(description)):
        paragraph = description.pop(0).split("]")
        if len(paragraph) != 2:
            continue
        text.append({
            "title": paragraph[0].split("[")[1],
            "text": paragraph[1]
        })
    # see ./data/sample_response.json for more details
    response = jsonify({
        "mapUrl": finder.create_map_url(geocode, analysis),
        "score": analysis["score"],
        "results": analysis,
        "overview": overview,
        "text": text,
    }) 

    # this is poor practice in production
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = Response()
        # this is poor practice in production
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        return response