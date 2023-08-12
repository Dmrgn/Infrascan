# constants for changing program behaviour
DATABASE_FOLDER = "./data/" # location of msgpack data files
SEARCH_QUERIES = [
    "{term} near {shortened_address}, {geocode_region}",
    "{term} within 2km of {shortened_address}, {geocode_region}",
    "{term} close to {shortened_address}, {geocode_region}",
]
EARTH_RADIUS = 6371
EMAIL_ADDRESS = "infrascanmailer@gmail.com"
PROMPT = """
Write a paragraph about the predicted community environment given the following description of a neighbourhood. Avoid commenting on economics. The "score" field represents the computed community score in each respective category. Write a couple sentences pertaining to each category, ["grocery", "community center", "park", "shopping", "transit", "school", "restaurant"]. End with a concluding sentence that contains an overview of the community environment in the area.

Start each new section with the name of the category surrounded by square brackets. For example, the beginning of the grocery section should take the form "[grocery] local grocery information goes here". The conclusion should begin with "[conclusion]".

The data is provided with an abitrary number of decimal points. Please round distance values to the tens place (e.g 1.123214 kilometers becomes 1.1 kilometers and 0.419231123 kilometers becomes 400 meters). Community score should be rounded to the nearest integer values whole number.

Here is an example:
Given the data segment "[school] Cedarvale Community School is 0.23049585663757122 kilometers away with a user rating of 3 and a community score of 1.015418340977652. It is listed as being a: primary_school,school,point_of_interest,establishment,."
An appropriate response might be: "[school] Cedarvale Community School is within close proximity at just 200 meters away. With a predicted community score of 1, this school greatly contributes to the community landscape of the neighbourhood."

Here is your actual data:
{data}
"""