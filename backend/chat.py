import openai
import json
import msgpack

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
