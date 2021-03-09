from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint


url_driver = '/home/kirill/coding/python/Parser/geckodriver'
URL = "https://forcedrop.top/"
URL_PRICE = "https://lolz.guru/market/steam-value"
# Ссылки на steam профиль
steam_profiles = []
# Ссылки на Forcedrop профиль
players = []


def load_webdriver():
    # Запрет на загрузку картинок
    profile = webdriver.FirefoxProfile()
    profile.set_preference('permissions.default.image', 2)

    fireOptions = webdriver.FirefoxOptions()
    # Отключение браузера
    # fireOptions.add_argument("--headless")

    return webdriver.Firefox(executable_path=url_driver,
                             options=fireOptions, firefox_profile=profile)


def get_steam_account():
    # Получение ссылок на профиль Forcedrop
    items = []
    while True:
        try:
            items = []
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "all-live-drop"))
            )
            driver.find_element_by_class_name("all-live-drop").click()
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "item-history"))
            )
            items = driver.find_elements_by_class_name("item-history")
            break
        except Exception as e:
            print(e)
            driver.get(URL)

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
            driver.find_element_by_class_name(
                "profile-main__steam").get_attribute("href")
        )


def item_price():
    # Получени стоймости профиля Steam
    driver.get(URL_PRICE)
    for steam_profile in steam_profiles:
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, "ProfileLinkInput"))
        )
        input_url = driver.find_element_by_class_name("ProfileLinkInput")
        input_url.clear()
        input_url.send_keys(steam_profile)
        input_url.send_keys(Keys.ENTER)
        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "lztSv--item"))
            )

            Steam_items = dict()
            Steam_item_elems = driver.find_elements_by_xpath(
                "/html/body/div[2]/div/div/div/div[2]/div[2]/div[3]/div"
            )
            for Steam_item_elem in Steam_item_elems:
                if Steam_item_elem.find_elements_by_class_name(
                        "notTradable") == []:
                    title = Steam_item_elem.find_element_by_xpath(
                        ".//div[1]").text
                    price = Steam_item_elem.find_element_by_xpath(
                        ".//div[2]").text
                    Steam_items[title] = price
                elif Steam_item_elem.find_element_by_xpath(
                        ".//div[2]").text == '0 руб.':
                    break
        except Exception:
            driver.get(URL_PRICE)
            continue
        print(summa_items(Steam_items))


def summa_items(Sitems):
    sum = 0
    for i in Sitems:
        if len(Sitems[i].split()) == 5:
            sum += float(Sitems[i].split()[0].replace(',','.')) * int(Sitems[i].split()[3])
        else:
            sum += float(Sitems[i].split()[0].replace(',','.'))
    print(sum)


def hours_play():


if __name__ == '__main__':
    driver = load_webdriver()
    driver.implicitly_wait(0)
    driver.get(URL)

    get_steam_account()
    item_price()
    driver.close()
    # /html/body/div[2]/div/div/div/div[2]/div[2]/div[3]/div[2]/div[1]/div
