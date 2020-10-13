"""
1 关键词爬取淘宝网商品信息，selenium渲染的方式获取cookie，暂时只有一个账号密码，没有构建cookie池
2 关键词爬取的下来的商品信息，会有很多重复数据，需要去重操作
3 由于淘宝的内置推荐算法，每个账号推荐的商品信息会有所不同
"""

from bs4 import BeautifulSoup
import requests
import re
import json
from selenium import webdriver
import time
import random
import pymongo


def get_cookie():
    url = 'https://login.taobao.com/member/login.jhtml'
    options = webdriver.ChromeOptions()
    #无头模式
    options.set_headless()
    #开发者模式
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"')

    driver = webdriver.Chrome(executable_path=r'C:\Users\huangfei\Desktop\chromedriver.exe', chrome_options=options)
    # script = 'Object.defineProperty(navigator,"webdriver",{get:() => false,});'
    driver.get(url)
    script = 'Object.defineProperty(navigator,"webdriver",{get:() => undefined,});'
    driver.execute_script(script)
    user_name = 'user_name'
    password = 'password'
    driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(user_name)
    time.sleep(random.uniform(0, 2))
    driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
    time.sleep(random.uniform(0, 2))
    driver.find_element_by_xpath('//*[@id="login-form"]/div[4]/button').click()
    time.sleep(3)
    cookie_items = driver.get_cookies()
    cookie_str = ''
    for item_cookie in cookie_items:
        item_str = item_cookie["name"] + "=" + item_cookie["value"] + "; "
        cookie_str += item_str
    driver.quit()
    return cookie_str

def save_mongo(datas):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["taobao"]
    mycol = mydb["t2"]
    mycol.insert_many(datas)


keywords = '球鞋'
cookie = get_cookie()
for good_counts in range(0, 4401, 44):

    url = 'https://s.taobao.com/search?q={}&s={}'.format(keywords, good_counts)
    headers = {
        'cookie': cookie,
    }
    r = requests.get(url, headers=headers)
    html = r.text
    json_data = re.findall('g_page_config = ({.*})', html)[0]

    dict_data = json.loads(json_data)
    good_data = dict_data['mods']['itemlist']['data']['auctions']
    print(len(good_data))

    datas = []
    for good in good_data:
        data = {}
        data['good_id'] = good.get('nid')
        data['title'] = good.get('raw_title')
        data['price'] = good.get('view_price')
        data['sales_count'] = good.get('view_sales')
        data['comment_count'] = good.get('comment_count')
        data['isTmall'] = good.get('shopcard').get('isTmall')
        data['comment_url'] = good.get('comment_url')
        data['shopLink'] = good.get('shopLink')
        data['detail_url'] = good.get('detail_url')
        data['seller_name'] = good.get('nick')
        data['seller_id'] = good.get('user_id')
        datas.append(data)
    save_mongo(datas)