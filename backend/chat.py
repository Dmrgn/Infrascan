import openai
import json
import msgpack

from constants import *

with open("./data/keys.json") as f:
    openai.api_key = json.load(f)["openai"]

def generate_response(address, request):
    # generate response
    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": request},
        {"role": "user", "content": DATA_PROMPT}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation, 
    )

    content = response['choices'][0]['message']['content']
    # return response
    return content

def format_prompt_with_analysis(analysis):
    formatted_analysis = ""
    for result in analysis["results"]:
        formatted_analysis += f"[{result['factor']}] "
        for item in (result["results"][:5] if len(result["results"]) >= 5 else result["results"]):
            formatted_analysis += f"{item['name']} is {round(item['distance']*10)/10} kilometers away. "
        formatted_analysis += "\n"
    return formatted_analysis

def format_generated_text(generated_text):
    generated_text = generated_text.split("\n")
    overview = generated_text.pop(-1)
    text = {}
    for x in range(0, len(generated_text)):
        paragraph = generated_text.pop(0).split("]")
        if len(paragraph) != 2:
            continue
        text[paragraph[0].split("[")[1]] = {
            "title": paragraph[0].split("[")[1],
            "text": paragraph[1]
        }
    return {
        "overview": overview,
        "text": text
    }