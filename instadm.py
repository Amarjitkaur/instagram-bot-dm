import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from random import randint, uniform
from time import time, sleep
from functools import lru_cache
import logging
import sqlite3

from firebase import save_message

DEFAULT_IMPLICIT_WAIT = 30

USER_AGENTS = [
    "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "Mozilla/5.0 (Linux; U; Android 4.0.3; de-ch; HTC Sensation Build/IML74K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "Mozilla/5.0 (Linux; U; Android 2.3.5; zh-cn; HTC_IncredibleS_S710e Build/GRJ90) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-sa; HTC_DesireHD_A9191 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
]

# PROXY = ''
class InstaDM(object):

    def __init__(self, username, password, headless=True, instapy_workspace=None, profileDir=None, proxy=None):
        self.selectors = {
            "accept_cookies": "//button[text()='Accept All']",
            "home_to_login_button": "//button[text()='Log In']",
            "username_field": "username",
            "password_field": "password",
            "button_login": "//button/*[text()='Log In']",
            "login_check": "//*[@aria-label='Home'] | //button[text()='Save Info'] | //button[text()='Not Now']",
            "search_user": "queryBox",
            "select_user": '//div[text()="{}"]',
            "name": "((//div[@aria-labelledby]/div/span//img[@data-testid='user-avatar'])[1]//..//..//..//div[2]/div[2]/div)[1]",
            "next_button": "//button/*[text()='Next']",
            "textarea": "//textarea[@placeholder]",
            "send": "//button[text()='Send']",
            "not_now_notification":"/html/body/div[6]/div/div/div/div[3]/button[2]",
        }

        # Selenium config
        options = webdriver.ChromeOptions()

        if profileDir:
            options.add_argument("user-data-dir=profiles/" + profileDir)

        if headless:
            options.add_argument("--headless")

        mobile_emulation = {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
            # "userAgent": choice(USER_AGENTS)
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        print(proxy,"===============================")
        # webdriver.DesiredCapabilities.CHROME['proxy'] = {
        #     "httpProxy":proxy,
        #     "ftpProxy":proxy,
        #     "sslProxy":proxy,
        #     "proxyType":"MANUAL",
        # }
        # proxy setting
        self.curr_proxy = proxy
        if proxy:
            options.add_argument('--proxy-server=http://%s' % proxy)
        # options.add_argument('--proxy-server=ftp://%s' % proxy)
        # options.add_argument('--proxy-server=ssl://%s' % proxy)
        self.driver = webdriver.Chrome(executable_path=CM().install(), options=options)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(414, 736)

        # Instapy init DB
        self.instapy_workspace = instapy_workspace
        self.conn = None
        self.cursor = None
        self.conn = sqlite3.connect("db/instabot.db")
        self.cursor = self.conn.cursor()

        cursor = self.conn.execute("""
            SELECT count(*)
            FROM sqlite_master
            WHERE type='table'
            AND name='followers';
        """)
        count = cursor.fetchone()[0]

        if count == 0:
            self.conn.execute("""
                CREATE TABLE "followers" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "username"    TEXT NOT NULL UNIQUE,
                    "scraped_from"    TEXT DEFAULT NULL,
                    "message_sent"    BOOLEAN DEFAULT 0
                );
            """)

        try:
            self.__random_sleep__(1, 2)
            self.login(username, password)
        except Exception as e:
            logging.error(e)
            print(str(e))

    def login(self, username, password):
        # homepage
        self.bot_name = username
        self.driver.get('https://instagram.com/?hl=en')
        self.__random_sleep__(3, 5)
        if self.__wait_for_element__(self.selectors['accept_cookies'], 'xpath', 10):
            self.__get_element__(self.selectors['accept_cookies'], 'xpath').click()
            self.__random_sleep__(3, 5)
        if self.__wait_for_element__(self.selectors['home_to_login_button'], 'xpath', 10):
            self.__get_element__(self.selectors['home_to_login_button'], 'xpath').click()
            self.__random_sleep__(3, 5)

        # login
        logging.info(f'Login with {username}')
        self.__scrolldown__()
        if not self.__wait_for_element__(self.selectors['username_field'], 'name', 10):
            print('Login Failed: username field not visible')
        else:
            self.driver.find_element_by_name(self.selectors['username_field']).send_keys(username)
            self.driver.find_element_by_name(self.selectors['password_field']).send_keys(password)
            self.__get_element__(self.selectors['button_login'], 'xpath').click()
            self.__random_sleep__(3, 5)
            if self.__wait_for_element__(self.selectors['login_check'], 'xpath', 10):
                print('Login Successful')
            else:
                print('Login Failed: Incorrect credentials')

    def createCustomGreeting(self, greeting):
        # Get username and add custom greeting
        if self.__wait_for_element__(self.selectors['name'], "xpath", 10):
            user_name = self.__get_element__(self.selectors['name'], "xpath").text
            if user_name:
                greeting = greeting + " " + user_name + ", \n\n"
        else: 
            greeting = greeting + ", \n\n"
        return greeting

    def typeMessage(self, user, message):
        # Go to page and type message
        if self.__wait_for_element__(self.selectors['next_button'], "xpath"):
            self.__get_element__(self.selectors['next_button'], "xpath").click()
            self.__random_sleep__(3 , 5)

        if self.__wait_for_element__(self.selectors['textarea'], "xpath"):
            # self.__type_slow__(self.selectors['textarea'], "xpath", message)
            self.driver.find_element_by_xpath(self.selectors['textarea']).send_keys(message)
            self.__random_sleep__(3 , 5)

        if self.__wait_for_element__(self.selectors['send'], "xpath"):
            self.__get_element__(self.selectors['send'], "xpath").click()
            self.__random_sleep__(3, 5)
            print('Message sent successfully')

    def sendMessage(self, user, message, greeting=None):
        logging.info(f'Send message to {user}')
        print(f'Send message to {user}')
        self.driver.get('https://www.instagram.com/direct/new/?hl=en')
        self.__random_sleep__(3, 5)
        if self.__wait_for_element__(self.selectors['not_now_notification'], 'xpath', 3):
            self.__get_element__(self.selectors['not_now_notification'], 'xpath').click()
            self.__random_sleep__(3, 5)
        try:
            self.__wait_for_element__(self.selectors['search_user'], "name")
            self.__type_slow__(self.selectors['search_user'], "name", user)
            self.__random_sleep__(3, 5)

            if greeting != None:
                greeting = self.createCustomGreeting(greeting)

            # Select user from list
            elements = self.driver.find_elements_by_xpath(self.selectors['select_user'].format(user))
            if elements and len(elements) > 0:
                elements[0].click()
                self.__random_sleep__(3 , 5)

                if greeting != None:
                    self.typeMessage(user, greeting + message)
                else:
                    self.typeMessage(user, message)
                
                save_message(self.bot_name, user, message, self.curr_proxy)
                self.__random_sleep__(2 , 5)

                return True

            # In case user has changed his username or has a private account
            else:
                print(f'User {user} not found! Skipping.')
                return False
            
        except Exception as e:
            logging.error(e)
            return False


    def sendGroupMessage(self, users, message):
        logging.info(f'Send group message to {users}')
        print(f'Send group message to {users}')
        self.driver.get('https://www.instagram.com/direct/new/?hl=en')
        self.__random_sleep__(5, 7)
        if self.__wait_for_element__(self.selectors['not_now_notification'], 'xpath', 10):
            self.__get_element__(self.selectors['not_now_notification'], 'xpath').click()
            self.__random_sleep__(3, 5)

        try:
            usersAndMessages = []
            for user in users:

                self.__wait_for_element__(self.selectors['search_user'], "name")
                self.__type_slow__(self.selectors['search_user'], "name", user)
                self.__random_sleep__()

                # Select user from list
                elements = self.driver.find_elements_by_xpath(self.selectors['select_user'].format(user))
                if elements and len(elements) > 0:
                    elements[0].click()
                    self.__random_sleep__()
                else:
                    print(f'User {user} not found! Skipping.')

            self.typeMessage(user, message)
            # self.__random_sleep__(50, 60)
            # self.__random_sleep__(50, 60)

            return True
        
        except Exception as e:
            logging.error(e)
            return False
            
    def sendGroupIDMessage(self, chatID, message):
        logging.info(f'Send group message to {chatID}')
        print(f'Send group message to {chatID}')
        self.driver.get('https://www.instagram.com/direct/inbox/')
        self.__random_sleep__(5, 7)
        
        # Definitely a better way to do this:
        actions = ActionChains(self.driver) 
        actions.send_keys(Keys.TAB*2 + Keys.ENTER).perform()
        actions.send_keys(Keys.TAB*4 + Keys.ENTER).perform()

            
        if self.__wait_for_element__(f"//a[@href='/direct/t/{chatID}']", 'xpath', 10):
            self.__get_element__(f"//a[@href='/direct/t/{chatID}']", 'xpath').click()
            self.__random_sleep__(3, 5)

        try:
            usersAndMessages = [chatID]

            if self.__wait_for_element__(self.selectors['textarea'], "xpath"):
                self.__type_slow__(self.selectors['textarea'], "xpath", message)
                self.__random_sleep__()
            
            if self.__wait_for_element__(self.selectors['send'], "xpath"):
                self.__get_element__(self.selectors['send'], "xpath").click()
                self.__random_sleep__(3, 5)
                print('Message sent successfully')
            
            self.__random_sleep__(50, 60)

            return True
        
        except Exception as e:
            logging.error(e)
            return False

    @lru_cache
    def getAuthHeaders(self):
        cookie = ""
        for i in self.driver.get_cookies():
            cookie += i['name'] +'='+i['value'] + ';'

        headers = {
            'cookie':cookie,
            'x-ig-app-id': '1217981644879628'
        }
        return headers

    @lru_cache
    def getUserIdFromUserName(self , username):
        print('============================ Getting  user id ============================')
        headers = self.getAuthHeaders()
        res = requests.get('https://www.instagram.com/{}/?__a=1'.format(username) , headers=headers)
        user_id = res.json().get('graphql')['user']['id']
        print("============================ User id done ============================")
        return user_id

    def getFollowers(self , user, max_id=''):
        '''
        user  : IG username
        max_id : pass max_id to get next results
        '''
        count = 10000 # number of accounts to fetch in each api call

        try:
            user_id = self.getUserIdFromUserName(user)            
            headers = self.getAuthHeaders()
            url = "https://i.instagram.com/api/v1/friendships/{}/followers/?count={}&max_id={}&search_surface=follow_list_page".format(user_id, count ,max_id)
            print("============================ Getting user followers ============================")
            res = requests.get(url , headers=headers)
            followers = res.json().get('users')
            max_id = res.json().get('next_max_id')
            print('============================ Getting followers done ============================')
            return (followers, max_id)

        except Exception as e:
            logging.error(e)
            return False

    def __get_element__(self, element_tag, locator):
        """Wait for element and then return when it is available"""
        try:
            locator = locator.upper()
            dr = self.driver
            if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_id(element_tag))
            elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_name(element_tag))
            elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_xpath(element_tag))
            elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTOR, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_css_selector(element_tag))
            else:
                logging.info(f"Error: Incorrect locator = {locator}")
        except Exception as e:
            logging.error(e)
        logging.info(f"Element not found with {locator} : {element_tag}")
        return None

    def is_element_present(self, how, what):
        """Check if an element is present"""
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def __wait_for_element__(self, element_tag, locator, timeout=30):
        """Wait till element present. Max 30 seconds"""
        result = False
        self.driver.implicitly_wait(0)
        locator = locator.upper()
        for i in range(timeout):
            initTime = time()
            try:
                if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                    result = True
                    break
                elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                    result = True
                    break
                elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                    result = True
                    break
                elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTORS, element_tag):
                    result = True
                    break
                else:
                    logging.info(f"Error: Incorrect locator = {locator}")
            except Exception as e:
                logging.error(e)
                print(f"Exception when __wait_for_element__ : {e}")

            sleep(1 - (time() - initTime))
        else:
            print(f"Timed out. Element not found with {locator} : {element_tag}")
        self.driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)
        return result

    def __type_slow__(self, element_tag, locator, input_text=''):
        """Type the given input text"""
        try:
            self.__wait_for_element__(element_tag, locator, 5)
            element = self.__get_element__(element_tag, locator)
            actions = ActionChains(self.driver)
            actions.click(element).perform()
            for s in input_text:
                element.send_keys(s)
                sleep(uniform(0.25, 0.75))

        except Exception as e:
            logging.error(e)
            print(f'Exception when __typeSlow__ : {e}')

    def __random_sleep__(self, minimum=10, maximum=20):
        t = randint(minimum, maximum)
        logging.info(f'Wait {t} seconds')
        sleep(t)

    def __scrolldown__(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def teardown(self):
        self.driver.close()
        self.driver.quit()
