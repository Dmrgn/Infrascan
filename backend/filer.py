# ultilities for opening msgpack files
import msgpack

from constants import *
import finder

# loads the list of test addresses from file
# and fetches and saves all the geocode data 
# from the gmaps api
#   this was from when I got chatgpt to generate streets
#   which turned on to be inefficient and slow
#   now I'm using a web scraper and the fredricton 
#   white pages :)
# def preprocess_test_addresses():
#     sample_data = []
#     # open file
#     with open(RAW_TEST_ADDRESSES_FILE) as f:
#         # read each line
#         while line := f.readline():
#             # clean text
#             line = line.split(",")[0] + ", NB, Canada"
#             # validate addresses
#             geocode_results = finder.gmaps.geocode(line)
#             # check if the address exists
#             if len(geocode_results) == 0:
#                 continue
#             # add address to sample data
#             sample_data.append(geocode_results[0])
#             # save data to msgpack file
#         save_msgpack(MSGPACK_TEST_ADDRESSES_FILE, sample_data)
    

# reads a msgpack file with the specified name
# and returns the created python object
def open_msgpack(file_name):
    with open(DATABASE_FOLDER + file_name + ".msgpack", "rb") as f:
        data = msgpack.load(f)
    f.close()
    return data

# saves a msgpack file with the specified name
# and the specified python object
def save_msgpack(file_name, data):
    with open(DATABASE_FOLDER + file_name + ".msgpack", "wb") as f:
        msgpack.dump(data, f)
    f.close()
