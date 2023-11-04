import json
import time

import database

def create_stats():
    return json.dumps({
        "devices": [],
        "searches": [],
        "tokens_used": 0,
        "account_age": time.time(),
        "last_login": time.time(),
    })

# retrieves statistics about the specific user account
def get_stats(email):
    # get user stats from database
    res = database.cur.execute("SELECT * FROM user WHERE email = (?)", (email,))
    user = res.fetchone()
    if not user:
        return {"error":"User statistics not found"}
    # parse stats
    stats = json.loads(user[4])
    stats["tokens"] = user[3]
    stats["name"] = user[0]
    return {"error": None, "stats": stats}

# updates the specified stat to be the specified value
def update_stat(email, stat, value):
    # fetch stats
    stats = get_stats(email)
    if not stats["error"] == None:
        return stats
    # make change
    stats = stats["stats"]
    stats[stat] = value
    stats = json.dumps(stats)
    # update stats in database
    database.cur.execute("UPDATE user SET stats = (?) WHERE email = (?)", (stats, email))
    database.con.commit()
    return {"error": None}

# appends the specified value to the specified list of stats
def append_stat(email, stat, value):
    # fetch stats
    stats = get_stats(email)
    if not stats["error"] == None:
        return stats
    # make change
    stats = stats["stats"]
    stats[stat].append(value)
    if len(stats[stat]) > 3:
        stats[stat] = stats[stat][-3:]
    stats = json.dumps(stats)
    # update stats in database
    database.cur.execute("UPDATE user SET stats = (?) WHERE email = (?)", (stats, email))
    database.con.commit()
    return {"error": None}