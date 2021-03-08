from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint

URL = "https://forcedrop.top/"
URL_PRICE = "https://lolz.guru/market/steam-value"
# Ссылки на steam профиль
steam_profiles = []
# Ссылки на Forcedrop профиль
players = []

# Запрет на загрузку картинок
profile = webdriver.FirefoxProfile()
profile.set_preference('permissions.default.image', 2)

driver = webdriver.Firefox(executable_path='/home/kirill/coding/python/Parser/geckodriver',
                           firefox_profile=profile)
driver.implicitly_wait(2)
driver.get(URL)

items = []

# Получение ссылок на профиль Forcedrop
while True:
    try:
        items = []
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "all-live-drop"))
        )
        driver.find_element_by_class_name("all-live-drop").click()
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "item-history"))
        )
        items = driver.find_elements_by_class_name("item-history")
        break
    except Exception as e:
        print(e)

for item in items:
    try:
        if item.get_attribute("href") not in players:
            players.append(item.get_attribute("href"))
    except Exception as ex:
        print(ex)

# Получение ссылки на профиль Steam
for player in players:
    driver.get(player)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "profile-main__steam"))
    )
    steam_profiles.append(
        driver.find_element_by_class_name("profile-main__steam").get_attribute("href")
        )

# Получени стоймости профиля Steam
driver.get(URL_PRICE)
price_account = dict()
for steam_profile in steam_profiles:
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "ProfileLinkInput"))
    )
    input_url = driver.find_element_by_class_name("ProfileLinkInput")
    input_url.clear()
    input_url.send_keys(steam_profile)
    input_url.send_keys(Keys.ENTER)
    try:
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "Value mainc"))
        )
        Steam_items = dict()
        Steam_item_elems = driver.find_element_by_class_name("lztSv--item")
        for Steam_item_elem in Steam_item_elems:
            # lztSv--item--title
    except Exception:
        price_account[steam_profile] = "Inventory Closed"

pprint(price_account)
driver.close()
