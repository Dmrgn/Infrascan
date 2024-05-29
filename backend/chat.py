import openai
import json
import msgpack

from constants import *

with open("./data/keys.json") as f:
    openai.api_key = json.load(f)["openai"]

def generate_response(request):
    # generate response
    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": request},
        {"role": "user", "content": DATA_PROMPT},
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
    text = {
        "grocery": "Not enough grocery information available for this location.",
        "community center": "Not enough community center information available for this location.",
        "park": "Not enough park information available for this location.",
        "shopping": "Not enough shopping information available for this location.",
        "transit": "Not enough transit information available for this location.",
        "school": "Not enough school information available for this location.",
        "restaurant": "Not enough restaurant information available for this location.",
        "conclusion": "No summary generated. There was not enough information available to create a summary."
    }
    for x in range(0, len(generated_text)):
        paragraph = generated_text.pop(0).split("]")
        if len(paragraph) != 2:
            continue
        factor = paragraph[0].split("[")[1]
        if factor in text:
            text[factor] = {
                "title": factor,
                "text": paragraph[1]
            }
    conclusion = text["conclusion"]["text"]
    del text["conclusion"]
    return {
        "overview": conclusion,
        "text": text
    }