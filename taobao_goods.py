"""
问题1：
    商品详情页不需要登录，爬取频率多了后会有反爬，需要登录的操作，可以加代理，或者强制等待
问题2：
    关键词搜索页面也不需要登录，但是请求头里必须携带JS生成的cookie，比较难搞后面有时间搞，
    暂时考虑用selenium渲染的方式进行爬取
问题3：
    selenium渲染爬取的时候，
"""
from bs4 import BeautifulSoup
import requests
import re
import json
from selenium import webdriver
import time
import random
import pymongo


def get_proxy():
    host = ""
    port = ""
    user = ''
    password = ''

    proxy_meta = "http://%(user)s:%(password)s@%(host)s:%(port)s" % {
                "host": host,
                "port": port,
                "user": user,
                "password": password,
            }

    proxies = {
        "http": proxy_meta,
        "https": proxy_meta,
    }
    return proxies

def parse_taobao_good(good_id):
    url = 'https://item.taobao.com/item.htm?id={}'.format(good_id)
    print(url)
    proxies = get_proxy()
    r = requests.get(url,proxies=proxies)
    html = r.text
    # print(html)
    #图片url
    pic_url = re.findall('//gd.*?pic.jpg',html)
    pic_url1 = re.findall('//gd.*?\d{6,10}.jpg',html)
    pic_url.extend(pic_url1)
    pic_url = list(set(pic_url))
    print(len(pic_url), pic_url)

    soup = BeautifulSoup(html,'lxml')
    parameters_body = soup.select('ul.attributes-list')[0]
    parameters_list = parameters_body.select('li')
    #详情参数
    parameters_data = {}
    for parameter in parameters_list:
        parameter_data_list = parameter.text.split(':')
        parameter_data_dict = {parameter_data_list[0]:parameter_data_list[1].strip().replace('\xa0',' ')}
        parameters_data.update(parameter_data_dict)
    print(parameters_data)
    data = {'parameters_data': parameters_data, 'pic_url': pic_url}
    return data

def parse_tianmao_good(good_id):
    url = 'https://detail.tmall.com/item.htm?id={}'.format(good_id)
    print(url)
    proxies = get_proxy()
    r = requests.get(url, proxies=proxies)
    html = r.text
    # print(html)
    soup = BeautifulSoup(html,'lxml')
    pic_url = re.findall('//img.alicdn.com/.*?\d{8,12}.jpg',html)
    pic_url = list(set(pic_url))
    print(len(pic_url),pic_url)

    parameters_body = soup.select('ul#J_AttrUL')[0]
    parameters_list = parameters_body.select('li')
    # 详情参数
    parameters_data = {}
    for parameter in parameters_list:
        parameter_data_list = parameter.text.split(':')
        parameter_data_dict = {parameter_data_list[0]: parameter_data_list[1].strip().replace('\xa0',' ')}
        parameters_data.update(parameter_data_dict)
    print(parameters_data)
    data = {'parameters_data':parameters_data,'pic_url':pic_url}
    return data

def save_mongo(datas):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["taobao"]
    mycol = mydb["t1"]
    mycol.insert_many(datas)

def get_good_ids():
    keywords = '球鞋'
    for good_counts in range(0, 4401, 44):

        url = 'https://s.taobao.com/search?q={}&s={}'.format(keywords, good_counts)
        cookie = '_samesite_flag_=true; cookie2=12fa72a62a09e4418b6e55b9dd2e1ee5; t=c3d96fed76a6c9655adee419a335b07e; xlly_s=1; _m_h5_tk=fdc5ee5389609e8c2056dffce41c6dd1_1600833006493; _m_h5_tk_enc=59d4401857ec28afb64adb74c43e4d25; enc=yeJ0TsqpFa87hWaw5%2FMFlDNA2K%2F4gUywkQlEzcBVpKBFc3bQFSJU8at1o%2BHci7rxPQmNGSZgbqnBiPDYd4BZew%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; alitrackid=www.taobao.com; _tb_token_=e8a30ee5d3317; cna=wD7vFzFaN18CAbfPtqI6wRBZ; v=0; sgcookie=E100ZtvQZ11JtK7DPcELHnU%2FcmvgBpYJAvZA4T8K5XrChXhIp9YJI0%2F5awaj9Tq9giUxlNjYt9L5tqq4cLOUE8d7Eg%3D%3D; unb=1013689029; uc3=id2=UoH%2B5fsdAVDXhQ%3D%3D&vt3=F8dCufeMhGh6oFaemyg%3D&nk2=1A5va2gmbpe9&lg2=V32FPkk%2Fw0dUvg%3D%3D; csg=27299878; lgc=%5Cu98DE%5Cu513F%5Cu54E5132; cookie17=UoH%2B5fsdAVDXhQ%3D%3D; dnk=%5Cu98DE%5Cu513F%5Cu54E5132; skt=f7fbff519e2ffef8; existShop=MTYwMDg0MTE5NA%3D%3D; uc4=nk4=0%401t9%2BQFXlTqOu86Vd%2F18hSV2cQr4%3D&id4=0%40UOnhAXgGp7uOavnlTs92yiKloSQg; tracknick=%5Cu98DE%5Cu513F%5Cu54E5132; _cc_=VFC%2FuZ9ajQ%3D%3D; _l_g_=Ug%3D%3D; sg=293; _nk_=%5Cu98DE%5Cu513F%5Cu54E5132; cookie1=AnDQzJD83IFPvs0XAplXjeV4QWfKLl75H1h5DXp4WsI%3D; lastalitrackid=login.taobao.com; mt=ci=1_1; JSESSIONID=B69A2313993CA245A4D41B9ADB12C382; tfstk=c2mVBR_rmnKVq0E6JoZNfTVz3xEAaBonX3yUoVjwFw7FO940Ts4O68ml9Yka934c.; l=eBSNeEBcOHXdlv5tBOfZourza779bIRAguPzaNbMiOCP_05p5ijlWZrN9CT9CnGVh65eR3SxXm94BeYBqCj0JeHw2j-laTMmn; isg=BNnZ9epb4iLBTr62zvcJMnzr6MWzZs0YatL_bfuORoB_AvmUQ7cI6EQYBMZ0umVQ; uc1=cookie14=Uoe0bUAZiinQvQ%3D%3D&cookie15=URm48syIIVrSKA%3D%3D&cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&existShop=false&pas=0&cookie21=URm48syIYn73'
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

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['taobao']
mycol = mydb['t1']
datas = []
for x in mycol.find():
    isTmall = x['isTmall']
    title = x['title']
    print(title)
    good_id = x['good_id']
    print('good_id',good_id)
    if isTmall == True:
        for i in range(10):
            try:
                data_Tmall = parse_tianmao_good(good_id)
                break
            except:
                pass
        print('**********************','\n')
    else:
        good_id = x['good_id']
        for i in range(10):
            try:
                data_Tmall = parse_taobao_good(good_id)
                break
            except:
                pass
        print('**********************', '\n')


























