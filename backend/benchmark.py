import msgpack
import json
import random
import time

import finder

places = [
    {"name":"School", "query":"School"},
    {"name":"Park", "query":"Park"},
    {"name":"Transit station", "query":"Transit station"},
    {"name":"Restaurant", "query":"Restaurant"},
    {"name":"Grocery store", "query":"Grocery store"},
    {"name":"Library", "query":"Library"},
    {"name":"Post office", "query":"Post office"},
    {"name":"Hospital", "query":"Hospital"},
    {"name":"Police station", "query":"Police station"},
    {"name":"Fire station", "query":"Fire station"},
    {"name":"Community center", "query":"Community center"},
    {"name":"Shopping mall", "query":"Shopping mall"},
    {"name":"Gym", "query":"Gym"},
    {"name":"Coffee shop", "query":"Coffee shop"},
    {"name":"Movie theater", "query":"Movie theater"},
    {"name":"Bank", "query":"Bank"},
    {"name":"Pharmacy", "query":"Pharmacy"},
    {"name":"Gas station", "query":"Gas station"},
    {"name":"Church", "query":"Church"},
    {"name":"Mosque", "query":"Mosque"},
    {"name":"Temple", "query":"Temple"},
    {"name":"Playground", "query":"Playground"},
    {"name":"Sports field", "query":"Sports field"},
    {"name":"Barber shop or hair salon", "query":"Barber shop or hair salon"},
    {"name":"Laundromat", "query":"Laundromat"},
    {"name":"Daycare center", "query":"Daycare center"},
    {"name":"Senior center", "query":"Senior center"},
    {"name":"Art gallery or museum", "query":"Art gallery or museum"},
    {"name":"Farmer's market", "query":"Farmer's market"},
    {"name":"Bookstore", "query":"Bookstore"},
    {"name":"Pet store", "query":"Pet food store"},
    {"name":"Hardware store", "query":"Hardware store"},
]
speed = 0

# with open("./data.msgpack", "rb") as f:
#     addresses = msgpack.load(f)
# with open("./data.json", "w") as f:
#     json.dump(addresses, f)

with open("./research_data/final_geocodes.msgpack", "rb") as f:
    addresses = msgpack.load(f)

print(f"Legth of addresses: {len(addresses)}")

for address in addresses:
    address["region"] = "Fredericton, New Brunswick, " + address["a"].split(",")[-1]

already = set()
data = {}
for x in range(len(addresses)):
    print(f"\tAddress {addresses[x]['a']} {x+1}/{len(addresses)}")
    start = time.time()
    for y in range(len(places)):
        print(f"\t\tPlace {places[y]['name']} {y+1}/{len(places)}")
        if not places[y]['name'] in data: data[places[y]['name']] = []
        results = finder.analyze_address_with_term(addresses[x], places[y])["results"]
        print(f"\t\tFound {len(results)} results")
        for result in results:
            if not result["address"] in already:
                data[places[y]['name']].append(result)
                already.add(result["address"])
    if speed == 0: speed = time.time() - start 
    else: speed = ((speed*x)+time.time()-start)/(x+1)
    print(f"\tDone")
    print(f"\tAvg speed: {speed}")
    if x % 5 == 0:
        with open("./data.msgpack", "wb") as f:
            msgpack.dump(data, f)
        with open("./already.msgpack", "wb") as f:
            msgpack.dump(list(already), f)
