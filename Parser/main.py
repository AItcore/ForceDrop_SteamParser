from selenium import webdriver
from threading import Thread
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint


class ParserSite(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.accounts_used = []
        self.quitFlag = False
        self.url_driver = '/home/kirill/coding/python/Parser/geckodriver'
        self.driver = self.load_webdriver()
        self.driver.implicitly_wait(0)
        self.URL = "https://forcedrop.top/"
        self.URL_PRICE = "https://lolz.guru/market/steam-value"
        # Ссылки на steam профиль
        self.steam_profiles = []
        # Ссылки на Forcedrop профиль
        self.players = []
        self.accounts = []

    def run(self):
        while True:
            self.driver.get(self.URL)
            self.steam_profiles = []
            self.get_steam_account()
            for steam_profile in self.steam_profiles:
                if self.quitFlag:
                    try:
                        self.driver.quit()
                    except Exception:
                        print("try exit")
                if steam_profile not in self.accounts_used:
                    account = {
                        'URL': steam_profile,
                        'items_price': str(round(
                            self.item_price(steam_profile), 2)) + " руб.",
                        'hours_play': self.hours_play(steam_profile),
                        'is_ban_trade': self.is_ban_trade(steam_profile)
                    }
                    pprint(account)
                    print()
                    self.accounts_used.append(steam_profile)
                    self.accounts.append(account)
                else:
                    continue

    def load_webdriver(self):
        # Запрет на загрузку картинок
        profile = webdriver.FirefoxProfile()
        profile.set_preference('permissions.default.image', 2)

        fireOptions = webdriver.FirefoxOptions()
        # Отключение визуала браузера
        # fireOptions.add_argument("--headless")

        return webdriver.Firefox(executable_path=self.url_driver,
                                 options=fireOptions, firefox_profile=profile)

    def get_steam_account(self):
        # Получение ссылок на профиль Forcedrop
        items = []
        while True:
            try:
                items = []
                WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, "all-live-drop"))
                )
                self.driver.find_element_by_class_name("all-live-drop").click()
                WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located(
                        (By.CLASS_NAME, "item-history"))
                )
                items = self.driver.find_elements_by_class_name("item-history")
                break
            except Exception:
                self.driver.get(self.URL)

        for item in items:
            try:
                if item.get_attribute("href") not in self.players:
                    self.players.append(item.get_attribute("href"))
            except Exception:
                pass
        # Получение ссылки на профиль Steam
        for player in self.players:
            self.driver.get(player)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "profile-main__steam"))
            )
            self.steam_profiles.append(
                self.driver.find_element_by_class_name(
                    "profile-main__steam").get_attribute("href")
            )

    def item_price(self, steam_profile):
        # Получени стоймости профиля Steam
        try:
            self.driver.get(self.URL_PRICE)
        except Exception:
            pass
        WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, "ProfileLinkInput"))
        )
        input_url = self.driver.find_element_by_class_name("ProfileLinkInput")
        input_url.clear()
        input_url.send_keys(steam_profile)
        input_url.send_keys(Keys.ENTER)
        try:
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "lztSv--item"))
            )

            Steam_items = dict()
            Steam_item_elems = self.driver.find_elements_by_xpath(
                "/html/body/div[2]/div/div/div/div[2]/div[2]/div[3]/div"
            )
            for Steam_item_elem in Steam_item_elems:
                if Steam_item_elem.find_elements_by_class_name(
                        "notTradable") == []:
                    title = Steam_item_elem.find_element_by_class_name(
                        "lztSv--item--title").text
                    price = Steam_item_elem.find_element_by_class_name(
                        "lztSv--item--price").text
                    Steam_items[title] = price
                elif Steam_item_elem.find_element_by_class_name(
                        "lztSv--item--price").text == '0 руб.':
                    break
        except Exception:
            self.driver.get(self.URL_PRICE)
            return "Inventory closed"
        return(self.summa_items(Steam_items))

    def summa_items(self, Sitems):
        sum = 0
        for i in Sitems:
            if len(Sitems[i].split()) == 5:
                sum += float(
                    Sitems[i].split()[0].replace(
                        ',', '.')) * int(Sitems[i].split()[3])
            else:
                sum += float(Sitems[i].split()[0].replace(',', '.'))
        return sum

    def hours_play(self, steam_profile):
        dota2hours = 0
        csgohours = 0
        try:
            self.driver.get(steam_profile+"/games/?tab=all")
        except Exception:
            print("Slow internet")
            return None
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "game_570"))
            )
            dota2hours = self.driver.find_element_by_id(
                "game_570").find_element_by_class_name(
                    "hours_played").text.split()[0]
        except Exception:
            dota2hours = "dont play dota 2 / profile closed"
        try:
            csgohours = self.driver.find_element_by_id(
                "game_730").find_element_by_class_name(
                    "hours_played").text.split()[0]
        except Exception:
            csgohours = "dont play csgo / profile closed"
        return {'csgo': csgohours, 'dota2': dota2hours}

    def is_ban_trade(self, steam_profile):
        self.driver.get(steam_profile)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "profile_ban_status"))
            )
        except Exception:
            return False
        return True

    def end_work(self):
        try:
            self.quitFlag = True
        except Exception:
            print("Quit")


if __name__ == '__main__':
    SiteParser = ParserSite()
    SiteParser.start()
    while True:
        if input() == 'q':
            SiteParser.end_work()
            break
    # /html/body/div[2]/div/div/div/div[2]/div[2]/div[3]/div[2]/div[1]/div
