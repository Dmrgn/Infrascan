import password_strength

# constants for changing program behaviour
TEXT_DS_FILE = "./data/text_ds.txt" # data set file that the word2vec is trained on
VAL_DS_FILE = "./data/val_ds.txt" # data set validation file that the word2vec is trained on
DATABASE_FOLDER = "./data/"

SEARCH_RADIUS = 2000 # distance in meters to search around an address for amenities
EARTH_RADIUS = 6371 # radius of the earth in km
MAX_CACHE_SIZE = 30 # number of addresses that will be cached
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

SYSTEM_PROMPT = """
Your job is to assist in the analysis of the accessibility of community infrastructure in a given neighborhood. You will either be given some information about infrastructure in the area, or asked to analyze the information you’ve been given. 
"""

DATA_PROMPT = """
Write a paragraph about the accessibility of community infrastructure in the area. You will be given 0-5 places in each category. Write a couple sentences pertaining to each category, ["grocery", "community center", "park", "shopping", "transit", "school", "restaurant"]. If there is little to no infrastructure in a category, you should comment on the effect that its absence might have on the community. If there are some good options, suggest how this might enhance the community environment. End with a concluding sentence that contains an overview of the community infrastructure in the area. Start each new section with the name of the category surrounded by square brackets. For example, the beginning of the grocery section should take the form "[grocery] local grocery information goes here". The conclusion should begin with "[conclusion]".
"""