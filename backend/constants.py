import password_strength

# constants for changing program behaviour
DATABASE_FOLDER = "./data/" # location of msgpack data files and sqlite files
SEARCH_QUERIES = [
    "{term} near {shortened_address}, {geocode_region}",
    # "{term} within 2km of {shortened_address}, {geocode_region}",
    # "{term} close to {shortened_address}, {geocode_region}",
]
SEARCH_TERMS = [
    {"name":"grocery", "query":"grocery store"},
    {"name":"community center", "query":"community center"},
    {"name":"park", "query":"park"},
    {"name":"shopping", "query":"park"},
    {"name":"transit", "query":"bus station"},
    {"name":"school", "query":"school"},
    {"name":"restaurant", "query":"restaurant"}
]
SEARCH_RADIUS = 2000 # search radius around the address in meters
MAX_CACHE_SIZE = 30 # number of addresses that will be cached
EARTH_RADIUS = 6371 # radius of the earth in km
NUM_DEFAULT_TOKENS = 10 # tokens given to new accounts on creation
MAX_CACHE_AGE = 15 # max age in days allowed for cached data until we invalidate it
SESSION_LENGTH = 60 # session length in minutes before having to login again
VALID_NAME_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
PASSWORD_POLICY = password_strength.PasswordPolicy.from_names(
    length=8,
    uppercase=1, 
    numbers=1,
    special=1,
    nonletters=0,
)
EMAIL_ADDRESS = "infrascanmailer@gmail.com"
PROMPT = """
Write a paragraph about the predicted community environment given the following description of a neighbourhood. Avoid commenting on economics. The "score" field represents the computed community score in each respective category. Write a couple sentences pertaining to each category, ["grocery", "community center", "park", "shopping", "transit", "school", "restaurant"]. End with a concluding sentence that contains an overview of the community environment in the area.

Start each new section with the name of the category surrounded by square brackets. For example, the beginning of the grocery section should take the form "[grocery] local grocery information goes here". The conclusion should begin with "[conclusion]".

If applicable, in the conclusion, touch on areas of possible improvement based on categories with lower scores.

Here is an example:
Given the data segment "[school] Cedarvale Community School is 0.23 kilometers away with a user rating of 3 and a community score of 4. It is listed as being a: primary_school,school,point_of_interest,establishment,."
An appropriate response might be: "[school] Cedarvale Community School is within close proximity at just 230 meters away. With a predicted community score of 4, this school greatly contributes to the community landscape of the neighbourhood."

Here is your actual data:
{data}
"""