import os
import sys
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime

load_dotenv()

#MONGODB
try:
    client = MongoClient("mongodb+srv://"+os.getenv("MONGODB_USERNAME")+\
        ":"+os.getenv("MONGODB_PASSWORD")+"@"+os.getenv("MONGODB_DOMAIN")+\
            "/"+os.getenv("MONGODB_DBNAME")+"?retryWrites=true&w=majority")
except Exception as e:
    raise e

#SCRAPING
URLS = client["booking"]["hotels"].find()
for URL in URLS:
    print(URL)
    resp = Request(URL["url"], headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"})
    page = urlopen(resp)
    soup = BeautifulSoup(page, 'html.parser')

    hotel_names = []
    hotel_prices = []
    hotel_locations = []
    hotel_rates = []

    #Hotel name
    names = soup.find_all('div', class_ = "fcab3ed991 a23c043802")
    for name in names:
        hotel_names.append(name.getText())

    #Hotel price
    prices = soup.find_all('span', class_ = "fcab3ed991 bd73d13072")
    for price in prices:
        hotel_prices.append(price.getText().replace(u'\xa0', u''))

    #Hotel location
    locations = soup.find_all('span', class_ = "f4bd0794db b4273d69aa")
    for i in range(0,len(locations),2):
            hotel_locations.append(locations[i].getText())

    # #Hotel rates
    rates = soup.find_all('div', class_ = "b5cd09854e d10a6220b4")
    for rate in rates:
        hotel_rates.append(rate.getText())

    for i in range(0,len(hotel_names)):    
        data = {
            "name": hotel_names[i],
            "price": hotel_prices[i],
            "location": hotel_locations[i],
            "rate": hotel_rates[i],
            "url": URL["url"],
            "update_at": datetime.datetime.now()
        }

    client["booking"]["output_data"].update_many({"url": data['url']}, {"$set": data}, upsert=True) 
