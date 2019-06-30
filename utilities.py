from config import *

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import pymongo

import os
from time import sleep
from math import ceil
from datetime import datetime
from pathlib import Path
import json
import random

client = pymongo.MongoClient(f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_url}")
db = client.jumia

try:
    current_path = os.path.dirname(os.path.abspath(__file__))
except:
    current_path = '.'
    
    
def init_driver(gecko_driver='', user_agent='', load_images=True, is_headless=False):
    firefox_profile = webdriver.FirefoxProfile()
    
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
    firefox_profile.set_preference("media.volume_scale", "0.0")
    firefox_profile.set_preference("dom.webnotifications.enabled", False)
    if user_agent != '':
        firefox_profile.set_preference("general.useragent.override", user_agent)
    if not load_images:
        firefox_profile.set_preference('permissions.default.image', 2)

    options = Options()
    options.headless = is_headless
    
    driver = webdriver.Firefox(options=options,
                               executable_path=f'{current_path}/{gecko_driver}',
                               firefox_profile=firefox_profile)
    
    return driver
    
def get_url(page_url, driver):
    driver.get(page_url)
    
    sleep(page_load_timeout)
    
    close_popup = driver.find_elements_by_css_selector('.-close_popup')
    if len(close_popup) > 0:
        close_popup[0].click()
        
    return True

def get_products(driver):
    products = driver.find_elements_by_css_selector('section.products .sku')

    products_info = []

    for product in products:

        product_title = ''
        if len(product.find_elements_by_css_selector('h2.title span.name')) > 0:
            product_title = product.find_elements_by_css_selector('h2.title span.name')[0].text

        product_url = ''
        if len(product.find_elements_by_css_selector('a.link')) > 0:
            product_url = product.find_elements_by_css_selector('a.link')[0].get_attribute('href')
        
        current_price = 0
        if len(product.find_elements_by_css_selector('span.price-box .price span')) > 0:
            current_price = product.find_elements_by_css_selector('span.price-box .price span')[0].get_attribute('data-price')
            current_price = ceil( float(current_price) )    


        old_price = 0
        if len(product.find_elements_by_css_selector('span.price-box .-old span')) > 0:
            old_price = product.find_elements_by_css_selector('span.price-box .-old span')[0].get_attribute('data-price')
            old_price = ceil( float(old_price) )


        discount_percentage = 0
        discount_quantity = 0

        if current_price != 0 and old_price != 0 and current_price < old_price:
            discount_quantity = round( old_price - current_price )
            discount_percentage = round( 100 - ( (current_price / old_price) * 100 ) )

        
        if product_title == '' or product_url == '' or current_price == 0:
            continue
        
        product_info = {
            'product_title': product_title,
            'product_url': product_url,
            'current_price': current_price,
            'old_price': old_price,
            'discount_percentage': discount_percentage,
            'discount_quantity': discount_quantity,
            'inserted_at': datetime.now(),
            'updated_at': datetime.now(),
            'published_at': False
        }
        
        if db.products.count_documents( { '$or': [ {'product_title': product_title}, {'product_url':product_url} ]  } ) == 0:
            _ = db.products.insert_one( product_info )
        else:
            pd = db.products.find_one( { '$or': [ {'product_title': product_title}, {'product_url':product_url} ]  } )
            if pd['current_price'] != current_price or pd['old_price'] != old_price:
                # update prices
                db.products.update_one( {'_id': pd['_id'] },{'$set': 
                                                             {'current_price': current_price,
                                                             'old_price': old_price,
                                                             'discount_percentage': discount_percentage,
                                                             'discount_quantity':discount_quantity,
                                                             'updated_at': datetime.now(),
                                                             'published_at': False} }  )

        products_info.append( product_info )
    
    return products_info


def load_cookies(driver):
    
    driver.get(twitter_url)
    
    cookie_file = f"{current_path}/{twitter_cookies_path}"
    cookies = ''
    
    if Path(cookie_file).is_file():
        with open(cookie_file, 'r', encoding='utf8') as ck_file:
            cookies = ck_file.read()
        
    if cookies != '':
        cookies = json.loads(cookies)
        
        if len(cookies) > 0:
            for cookie in cookies:
                driver.add_cookie(cookie)
        
        sleep(5)
        
        driver.get(f"{twitter_url}/settings/account")
        if len(driver.find_elements_by_css_selector('input.js-username-field')) > 0:
            _ = open(cookie_file, 'w').truncate()
            return False
        else:
            return True
        
    return False

def twitter_login(driver):
    driver.get(twitter_login_page)
    
    if len(driver.find_elements_by_css_selector('input.js-username-field')) > 0 and len(driver.find_elements_by_css_selector('input.js-password-field')) > 0:
        email = driver.find_elements_by_css_selector('input.js-username-field')[0]
        password = driver.find_elements_by_css_selector('input.js-password-field')[0]

        email.clear()
        password.clear()

        email.send_keys( twitter_email )
        password.send_keys( twitter_password )

        sleep(3)
        login_btn = driver.find_elements_by_css_selector('button[type="submit"]')[0].click()

        sleep(5)
        cookies_list = driver.get_cookies()

        ck_file = open(f"{current_path}/{twitter_cookies_path}",'w', encoding='utf8')
        ck_file.write( json.dumps( cookies_list ) )
        ck_file.close()
    
    return True


def publish_product(driver, product):
    
    driver.get(twitter_url)
    sleep(5)
    
    if len(driver.find_elements_by_css_selector('#tweet-box-home-timeline')) > 0:
        tweet_box = driver.find_elements_by_css_selector('#tweet-box-home-timeline')[0]
        tweet_box.click()
        sleep(2)
    
        messages_templates = [
             f"""
                     الحق خصم 
                     {product['discount_percentage']}%
                     على 
                     {product['product_title']}
                """,
              f"""
                     جوميا عاملالك خصم 
                     {product['discount_percentage']}%
                     على 
                     {product['product_title']}
                """,
              f"""
                    لو حابب تشتري 
                    {product['product_title']}
                    الحق بسرعة عشان جوميا موفرة عليك
                     {product['discount_percentage']}%
                     و حتشتريه بـ
                     {product['current_price']}
                     بدل من
                     {product['old_price']} 
                     جنيه

                """,
               f"""
                     متفكرش كتير. خصم
                     {product['discount_percentage']}%
                     على 
                     {product['product_title']}
                """,

        ]

        msg = random.choice( messages_templates )

        msg = " ".join([ word for word in msg.replace('\n', ' ').strip().split(' ')  if word.strip() != '' ] )

        msg += f"<br /> {product['product_url']}"

        driver.execute_script(f"""
            document.querySelector('#tweet-box-home-timeline').innerHTML = '{msg}';
        """)

        sleep(5)

        if len(driver.find_elements_by_css_selector('button.tweet-action')) > 0:
            tweet_btn = driver.find_elements_by_css_selector('button.tweet-action')[0]
            tweet_btn.click()

            # update product
            db.products.update_one( {'_id':product['_id']}, {'$set': {'published_at':datetime.now() } } )

            return True
    
    return False


