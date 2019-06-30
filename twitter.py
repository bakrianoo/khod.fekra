from config import *
from utilities import *

from time import sleep
import json
from pathlib import Path
from datetime import datetime

import pymongo
client = pymongo.MongoClient(f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_url}")
db = client.jumia

try:
    current_path = os.path.dirname(os.path.abspath(__file__))
except:
    current_path = '.'

driver = init_driver(gecko_driver, user_agent=user_agent, is_headless=headless)

# login to your account
is_login = load_cookies(driver)
if is_login == False:
    twitter_login(driver)
    
# publish your products
driver.get(twitter_url)
if len(driver.find_elements_by_css_selector('#tweet-box-home-timeline')) > 0:
    products = list( db.products.find( {'published_at': False, 'discount_percentage' : {'$gt': 20} } ).limit(5) )
    for product in products:
        _ = publish_product(driver, product)
        sleep(page_load_timeout)

driver.quit()