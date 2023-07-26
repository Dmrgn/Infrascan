from bs4 import BeautifulSoup as bs
import requests

import filer

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NAME_BY_LETTER_URL = "https://www.whitepagescanada.ca/nb/fredericton/a-z/{letter}/"
NAME_ADDRESS_URL = "https://www.whitepagescanada.ca/name/nb/fredericton/{last_name}/"

# fetch all the registered last names starting with the given letter
def fetch_names_of_letter(letter):
    leaderboard_soup = bs(requests.get(NAME_BY_LETTER_URL.format(letter=letter)).text, "html.parser") # get surname list page
    elements_list = leaderboard_soup.select("#wrapper>.container>.four.columns>ul>li>a") # find last names
    link_list = [x.attrs["href"].split("/")[6] for x in elements_list] # get the snakes' ids
    link_list = list(filter(lambda x: x != "Fredericton", link_list))
    return link_list

# get all the addresses of people with the given last name
def fetch_addresses_of_last_name(last_name):
    leaderboard_soup = bs(requests.get(NAME_ADDRESS_URL.format(last_name=last_name)).text, "html.parser") # get surname list address page
    elements_list = leaderboard_soup.find_all(attrs={"itemprop":"address"}) # find addresses
    address_list = [x.text for x in elements_list] # get the snakes' ids
    address_list = list(filter(lambda x: x != "Fredericton", address_list))
    return address_list

# scrape all addresses and save to file
# (this only searches the first page of results for each letter: ~3000 results total)
def scrape_addresses():
    for letter in letters:
        print("letter: " + letter)
        for last_name in fetch_names_of_letter(letter):
            print("\t" + last_name)
            for address in fetch_addresses_of_last_name(last_name):
                addresses.add(address)
    addresses = list(addresses)
    filer.save_msgpack("addresses", addresses)