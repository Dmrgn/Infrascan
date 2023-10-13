import sqlite3
import json
import time

from constants import *

con = sqlite3.connect("./data/cache.sqlite", check_same_thread=False)
cur = con.cursor()

cache_size = cur.execute("SELECT COUNT(*) FROM cache").fetchone()[0]

# cache is (address, data, age)

# takes a geocode formatted address and returns the
# cached data corresponding to its analysis
def get_address_data(address):
    global cache_size
    # query database for cached data
    res = cur.execute("SELECT * FROM cache WHERE address = (?)", (address,))
    address = res.fetchone()
    # check if cached data exists
    if address is None:
        return None
    # check age of cached data
    if time.time()-address[2] >= 60*60*24*MAX_CACHE_AGE:
        # remove cached data
        cur.execute("DELETE FROM cache WHERE address = (?)", (address[0],))
        con.commit()
        cache_size-=1
        return None
    # return cached data
    return json.loads(address[1])

# add the address and its associated analysis
# data to the cache
def add_address_data(address, data):
    global cache_size
    # check if cache is too big
    if cache_size >= MAX_CACHE_SIZE:
        res = cur.execute("""
                          SELECT * FROM (
                            SELECT * FROM cache ORDER BY age
                          ) LIMIT 5
                          """)
        to_delete = res.fetchall()
        # delete 5 oldest items
        for item in to_delete:
            cur.execute("DELETE FROM cache WHERE address = (?)", (item[0],))
        con.commit()
    # add data to cache
    data_string = json.dumps(data)
    cur.execute("INSERT INTO cache VALUES (?, ?, ?)", (address, data_string, time.time()))
    cache_size+=1
    con.commit()

# cur.execute("DROP TABLE cache")
# cur.execute("CREATE TABLE cache(address, data, age)")