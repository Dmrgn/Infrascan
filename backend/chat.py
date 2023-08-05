import openai
import json
import msgpack

from constants import *

with open("./data/keys.json") as f:
    openai.api_key = json.load(f)["openai"]

def format_address(address):
    return "_".join(address.split(" "))

def generate_response(address, request):
    # open cache manifest file
    with open("./data/cached/manifest.json") as f:
        manifest = json.load(f)
        f.close()

    formatted_address = format_address(address)

    # if the address is cached
    if (formatted_address in manifest):
        # open cached file
        with open("./data/cached/{}.msgpack".format(formatted_address), "rb") as f:
            response = msgpack.load(f)
            f.close()
            # return cached data
            return response
    
    # if the address is not cached
    # generate response
    conversation = [
        {"role": "user", "content": request}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        
    )
    content = response['choices'][0]['message']['content']
    # cache response
    with open("./data/cached/{}.msgpack".format(formatted_address), "wb") as f:
        msgpack.dump(content, f)
        f.close()
    with open("./data/cached/manifest.json", "w") as f:
        manifest[formatted_address] = True
        json.dump(manifest, f)
        f.close()
        # return response
    return content

def format_prompt_with_analysis(analysis):
    formatted_analysis = ""
    for result in analysis["results"]:
        formatted_analysis += "[{category}] ".format(category=result["description"])
        for item in result["results"]:
            formatted_analysis += "{name} is {distance} kilometers away with a user rating of {rating} and a community score of {score}. It is listed as being a: ".format(name=item["name"], distance=item["distance"], rating=item["rating"], score=item["score"])
            for type in item["types"]:
                formatted_analysis += "{thing},".format(thing=type)
            formatted_analysis += ". "
        formatted_analysis += "\n"
    return PROMPT.format(data=formatted_analysis)

def format_generated_text(generated_text):
    generated_text = generated_text.split("\n")
    overview = generated_text.pop(-1)
    text = []
    for x in range(0, len(generated_text)):
        paragraph = generated_text.pop(0).split("]")
        if len(paragraph) != 2:
            continue
        text.append({
            "title": paragraph[0].split("[")[1],
            "text": paragraph[1]
        })
    return {
        "overview": overview,
        "text": text
    }