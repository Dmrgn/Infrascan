from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
import json

import finder
import chat
from constants import *

app = Flask(__name__)

@app.route("/")
def index():
    return "Infrascan Server"

# fetch the infrascan results for an address
@app.route("/fetch")
def fetch():
    address = request.args.get("address")
    if not address:
        return "Please specify an address."
    geocode = finder.address_to_formatted_geocode_mapbox(address, True)

    # perform analysis
    analysis = finder.analyze(geocode)

    # format analysis for turbo gpt
    formatted_analysis = chat.format_prompt_with_analysis(analysis)
    # ask turbo gpt for human readable analysis
    generated_text = chat.generate_response(geocode["a"], formatted_analysis)
    # break giant string into sections for the frontend
    formatted_generated_text = chat.format_generated_text(generated_text)
    
    # see ./data/sample_response.json for more details
    response = {
        "mapUrl": finder.create_map_url(geocode, analysis),
        "score": analysis["score"],
        "results": analysis,
        "overview": formatted_generated_text["overview"],
        "text": formatted_generated_text["text"],
        "address": geocode["a"]
    }
    
    with open("./response.json", "w") as f:
        json.dump(response, f)

    response = jsonify(response)


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