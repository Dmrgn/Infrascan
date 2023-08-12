from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
import json

import finder
import chat
import database
from constants import *

app = Flask(__name__)

@app.route("/")
def index():
    return "Infrascan Server"

@app.route("/login")
def login():
    email = request.args.get("email")
    password = request.args.get("password")
    if email == None or password == None:
        response = jsonify({"error":"Either name, email or password were missing on the request"})
        return headerify(response)
    login_response = database.login(email, password)
    if login_response["error"] != None:
        response = jsonify(login_response)
        return headerify(response)
    response = jsonify({"secret": login_response["secret"]})
    return headerify(response)

@app.route("/register")
def register():
    name = request.args.get("name")
    email = request.args.get("email")
    password = request.args.get("password")
    if name == None or email == None or password == None:
        response = jsonify({"error":"Either name, email or password were missing on the request"})
        return headerify(response)
    register_response = database.register(name, email, password)
    if register_response["error"] != None:
        response = jsonify(register_response)
        return headerify(response)
    response = jsonify({"secret": register_response["secret"]})
    return headerify(response)

@app.route("/emailcode")
def emailcode():
    email_code = request.args.get("code")
    secret = request.args.get("secret")
    print(email_code, secret)
    if email_code == None or secret == None:
        response = jsonify({"error":"The email code was missing on the request or there was no secret"})
        return headerify(response)
    email_code_response = database.emailcode(email_code, secret)
    if email_code_response["error"] != None:
        response = jsonify(email_code_response)
        return headerify(response)
    response = jsonify({"secret": email_code_response["secret"]})
    return headerify(response)

# fetch the infrascan results for an address
@app.route("/fetch")
def fetch():
    address = request.args.get("address")
    secret = request.args.get("secret")
    if not address:
        return headerify(jsonify({"error":"Please specify an address"}))
    if not secret:
        return headerify(jsonify({"error":"No secret was attached to the request"}))
    
    validate_response = database.validate_user(secret)
    if validate_response["error"] != None:
        return headerify(jsonify(validate_response))

    # get geocode of the address
    geocode = finder.address_to_formatted_geocode(address, True)
    # perform analysis
    analysis = finder.analyze(geocode)

    # format analysis for turbo gpt
    formatted_analysis = chat.format_prompt_with_analysis(analysis)
    # ask turbo gpt for human readable analysis
    generated_text = chat.generate_response(geocode["a"], formatted_analysis)
    # break giant string into sections for the frontend
    formatted_generated_text = chat.format_generated_text(generated_text)
    
    # return formatted analysis
    # see ./data/sample_response.json for more details
    response = jsonify({
        "mapUrl": finder.create_map_url(geocode, analysis),
        "score": analysis["score"],
        "results": analysis,
        "overview": formatted_generated_text["overview"],
        "text": formatted_generated_text["text"],
        "address": geocode["a"]
    })
    return headerify(response)

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = Response()
        return headerify(response)
    
def headerify(response):
    # this is poor practice in production
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'ngrok-skip-browser-warning')
    return response