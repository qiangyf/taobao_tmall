
from selenium import webdriver
import random
import time


def get_cookie():
    url = 'https://login.taobao.com/member/login.jhtml'
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"')

    driver = webdriver.Chrome(executable_path=r'C:\Users\huangfei\Desktop\chromedriver.exe',chrome_options=options)
    # script = 'Object.defineProperty(navigator,"webdriver",{get:() => false,});'
    driver.get(url)
    script = 'Object.defineProperty(navigator,"webdriver",{get:() => undefined,});'
    driver.execute_script(script)
    user_name = 'username'
    password = 'password'
    driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(user_name)
    time.sleep(random.uniform(0,2))
    driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
    time.sleep(random.uniform(0,2))
    driver.find_element_by_xpath('//*[@id="login-form"]/div[4]/button').click()
    time.sleep(3)
    cookie_items = driver.get_cookies()
    cookie_str = ''
    for item_cookie in cookie_items:
        item_str = item_cookie["name"] + "=" + item_cookie["value"] + "; "
        cookie_str += item_str
    return cookie_str





