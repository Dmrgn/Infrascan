from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
import json
import user_agents

import finder
import chat
import database
import stats
from constants import *

app = Flask(__name__)

@app.route("/")
def index():
    return "Infrascan Server"

@app.route("/login")
def login():
    email = request.args.get("email")
    password = request.args.get("password")
    device = user_agents.parse(request.headers.get('User-Agent')).device
    if email == None or password == None:
        return headerify(jsonify({"error":"Either email or password were missing on the request"}))
    login_response = database.login(email, password, device)
    if login_response["error"] != None:
        return headerify(jsonify(login_response))
    response = jsonify({"secret": login_response["secret"], "stats": login_response["stats"]})
    return headerify(response)

@app.route("/register")
def register():
    name = request.args.get("name")
    email = request.args.get("email")
    password = request.args.get("password")
    if name == None or email == None or password == None:
        return headerify(jsonify({"error":"Either name, email or password were missing on the request"}))
    register_response = database.register(name, email, password)
    if register_response["error"] != None:
        return headerify(jsonify(register_response))
    response = jsonify({"secret": register_response["secret"]})
    return headerify(response)

@app.route("/emailcode")
def emailcode():
    email_code = request.args.get("code")
    secret = request.args.get("secret")
    device = user_agents.parse(request.headers.get('User-Agent')).device
    if email_code == None or secret == None:
        return headerify(jsonify({"error":"The email code was missing on the request or there was no secret"}))
    email_code_response = database.emailcode(email_code, secret, device)
    if email_code_response["error"] != None:
        return headerify(jsonify(email_code_response))
    response = jsonify({"secret": email_code_response["secret"], "stats": email_code_response["stats"]})
    return headerify(response)

@app.route("/userstats")
def userstats():
    secret = request.args.get("secret")
    if secret == None:
        return headerify(jsonify({"error":"No secret was attached to the request"}))
    # confirm credentials
    validate_response = database.validate_user(secret)
    if validate_response["error"] != None:
        return headerify(jsonify(validate_response))
    # return user stats
    return headerify(jsonify(stats.get_stats(validate_response["email"])["stats"]))


# fetch the infrascan results for an address
@app.route("/fetch")
def fetch():
    address = request.args.get("address")
    latlng = request.args.get("latlng")
    secret = request.args.get("secret")
    if not address and not latlng:
        return headerify(jsonify({"error":"Please specify an address or latlng"}))
    if not secret:
        return headerify(jsonify({"error":"No secret was attached to the request"}))
    
    # confirm credentials
    validate_response = database.validate_user(secret)
    if validate_response["error"] != None:
        return headerify(jsonify(validate_response))
    
    geocode = None
    # if a latlng was specified, turn it into an address, latlng pair
    if not latlng is None:
        latlng = finder.latlng_from_string(latlng)
        if latlng is None:
            return headerify(jsonify({"error":"Unable to parse geocode"}))
        geocode = finder.latlng_to_geocode(latlng)
    else:
        # if an address was specified, turn it into an address, latlng pair
        geocode = finder.address_to_geocode(address)

    # analyze and package for the browser
    # pass secret so that tokens can be charged
    analysis = finder.analyze(geocode, secret, validate_response["email"])

    return headerify(jsonify(analysis))

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = Response()
        return headerify(response)
    
def headerify(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'ngrok-skip-browser-warning')
    return response