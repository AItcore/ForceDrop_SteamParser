from selenium import webdriver
from threading import Thread
import sqlite3
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ParserSite(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.conn = sqlite3.connect("Account.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setName("Parser")
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
        self.isComplete = False
        self.forcedropURL = dict()
        self.players = []
        self.accounts = []

    def run(self):
        print("Start")
        while True:
            if self.quitFlag:
                try:
                    break
                except Exception:
                    print("try exit")
            try:
                self.driver.get(self.URL)
            except Exception:
                print("cjcb")
                self.driver.quit()
                break
            self.steam_profiles = []
            self.get_steam_account()
            for steam_profile in self.steam_profiles:
                if self.quitFlag:
                    try:
                        break
                    except Exception:
                        print("try exit")
                if steam_profile not in self.accounts_used:
                    account = {
                        'URL': steam_profile,
                        'forcedrop_url': self.forcedropURL[steam_profile],
                        'items_price': str(round(
                            self.item_price(steam_profile), 2)) + " руб.",
                        'hours_play': self.hours_play(steam_profile),
                        'is_ban_trade': self.is_ban_trade(steam_profile),
                        'nick': self.getNick(),
                        'lvl': self.lvlAcc(),
                        'last_online': self.lastOnline(),
                        'friend_count': self.friend_count()
                    }
                    if self.isComplete and self.isValid(account['URL']) and not account['items_price'] == "0 руб.":
                        self.isComplete = False
                        self.cursor.execute(f""" INSERT INTO accounts(
                            url,
                            forcedrop_url,
                            items_price,
                            csgo_hours,
                            dota2_hours,
                            is_ban_trade,
                            nick,
                            lvl,
                            last_online,
                            friend_count)
                            VALUES (?,?,?,?,?,?,?,?,?,?)
                            """, (
                            str(account['URL']),
                            str(account['forcedrop_url']),
                            str(account['items_price']),
                            str(account['hours_play']
                                ['csgo']),
                            str(account['hours_play']
                                ['dota2']),
                            str(account['is_ban_trade']),
                            str(account['nick']),
                            str(account['lvl']),
                            str(account['last_online']),
                            str(account['friend_count']))
                        )
                        self.conn.commit()
                        print("Add_user")
                    self.accounts_used.append(steam_profile)
                    self.accounts.append(account)
                else:
                    continue
        self.driver.quit()

    def load_webdriver(self):
        # Запрет на загрузку картинок
        try:

            profile = webdriver.FirefoxProfile()
            profile.set_preference('permissions.default.image', 2)

            fireOptions = webdriver.FirefoxOptions()
            # Отключение визуала браузера
            fireOptions.add_argument("--headless")

            return webdriver.Firefox(executable_path=self.url_driver,
                                     options=fireOptions,
                                     firefox_profile=profile)
        except Exception:
            fireOptions = webdriver.ChromeOptions()
            # Отключение визуала браузера
            fireOptions.add_argument("--headless")
            fireOptions.add_experimental_option(
                "prefs", {"profile.managed_default_content_settings.images": 2}
            )
            return webdriver.Chrome(executable_path=".\\chromedriver.exe",
                                    options=fireOptions)

    def isValid(self, url):
        sql = "SELECT url FROM accounts WHERE url ='" + url + "'"
        urls = self.cursor.execute(sql)
        if urls.fetchall() == []:
            return True
        return False

    def get_steam_account(self):
        if self.quitFlag:
            try:
                return None
            except Exception:
                print("try exit")
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
                if self.quitFlag:
                    break
                    return None
            except Exception:
                pass
        # Получение ссылки на профиль Steam
        for player in self.players:
            self.driver.get(player)
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, "profile-main__steam"))
                )
                self.steam_profiles.append(
                    self.driver.find_element_by_class_name(
                        "profile-main__steam").get_attribute("href")
                )
                self.forcedropURL[self.driver.find_element_by_class_name(
                    "profile-main__steam").get_attribute("href")] = player
                if self.quitFlag:
                    break
                    return None
            except Exception:
                pass

    def item_price(self, steam_profile):
        if self.quitFlag:
            try:
                return 0
            except Exception:
                print("try exit")
        # Получени стоймости профиля Steam
        try:
            self.driver.get(self.URL_PRICE)
        except Exception:
            pass
        try:
            WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "ProfileLinkInput"))
            )
            input_url = self.driver.find_element_by_class_name(
                "ProfileLinkInput")
            input_url.clear()
            input_url.send_keys(steam_profile)
            input_url.send_keys(Keys.ENTER)
        except Exception:
            return 0
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
            return 0
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
        if self.quitFlag:
            try:
                return None
            except Exception:
                print("try exit")
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
        if self.quitFlag:
            try:
                return None
            except Exception:
                print("try exit")
        self.driver.get(steam_profile)
        self.isComplete = True
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "profile_ban_status"))
            )
        except Exception:
            return False
        return True

    def lvlAcc(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "persona_level"))
            )
        except Exception:
            return "Профиль скрыт"
        return self.driver.find_element_by_class_name("persona_level").text

    def getNick(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "actual_persona_name"))
            )
        except Exception:
            return "Чёто пошло не так..."
        return self.driver.find_element_by_class_name("actual_persona_name").text

    def lastOnline(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "profile_in_game_header"))
            )
        except Exception:
            return "Профиль скрыт"
        return self.driver.find_element_by_class_name("profile_in_game_header").text

    def friend_count(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "profile_friend_links"))
            )
        except Exception:
            return "Профиль скрыт"
        friend = self.driver.find_element_by_class_name("profile_friend_links")
        return friend.find_element_by_class_name("profile_count_link_total").text

    def end_work(self):
        self.quitFlag = True

    def parserQuit(self):
        self.driver.quit()

    def resume_word(self):
        self.quitFlag = False
        self.driver = self.load_webdriver()
