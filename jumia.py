from config import *
from utilities import *

try:
    current_path = os.path.dirname(os.path.abspath(__file__))
except:
    current_path = '.'
    
driver = init_driver(gecko_driver, user_agent=user_agent, is_headless=headless)

categories = ['phones-tablets', 'electronics']

for category in categories:
    category_url = f"{jumia_base_url}/{category}"
    for page in range(1,6):
        page_url = f"{category_url}/?page={str(page)}"
        _ = get_url(page_url, driver)
        products = get_products(driver)