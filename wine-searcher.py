#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 20:28:21 2021

@author: admin
"""

import random
import time
import requests 
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller

def custom_sleep():
    s = random.randint(3000, 5000) / 1000
    time.sleep(s)
    
headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'Referer': 'https://www.wine-searcher.com',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'cookie': 'cookie_enabled=true; cookie_enabled=true; COOKIE_ID=SGFKCDW027T00L4; visit=SGFKCDW027T00L4%7C20210207161037%7C%2Fwine-scores%7Chttps%253A%252F%252Fwww.google.com%252F%7Cend%20; user_status=A%7C; _csrf=vGdCC5N02Fh1sr-zxtPFfo9uzgbD_nE-; _pxhd=5652cab8b701ae3c077db970ba352e67d013abfa8f2b7cc98946f3f711d589df:0398d790-695f-11eb-acf5-ef16d0b47751; _pxvid=0398d790-695f-11eb-acf5-ef16d0b47751; __gads=ID=2dc0216572117356:T=1612714238:S=ALNI_Ma527xrcXwwN3_3j1RfCH1jXD6Nuw; ID=3WBMCLDC250003C; IDPWD=I48150015; _gid=GA1.2.1423382995.1615206177; geoinfo=1.348|103.7032|Jurong+West|Singapore|SG|218.212.18.106|1881955|IP|Jurong+West%2C+Singapore; vtglist_expand_yn=y; price=35; price_r=35; fflag=flag_store_manager%3A0%2Cend; _ga_M0W3BEYMXL=GS1.1.1615218390.4.1.1615230138.0; _pxff_tm=1; _gat_UA-216914-1=1; _ga=GA1.2.2050195081.1612714238; _px3=738ac915cda85af8224cf7f30603fdf827759967b316dc9eb26daff39aa93ad3:rqr7BN2GnIWZtYixOD5ixzBGSuOg+zhokkarDFSPvZF6LoFCjCw4++WtYcd2vI1dVWYcNuS/sflqJJUjZo05wQ==:1000:azYxSevG7lIJFmUN9/U80UkGnYf9enZl3/XRPfiGGuuw0b0+sWNOKIftNBxkngZdiNHUxBXXqXsrTzqp57MCWmxiJMq9qaYFySN5NubL8/q/toR9t4PdymMSsQbx5v/RhYvVZE57LjzMmmcdNxpT4y0uoVISX0Yv0eeSdNj0HHY=; _px2=eyJ1IjoiY2RlNzFkNzAtODA0MC0xMWViLWJiZWItZGY4M2M1NzVjOTkxIiwidiI6IjAzOThkNzkwLTY5NWYtMTFlYi1hY2Y1LWVmMTZkMGI0Nzc1MSIsInQiOjE2MTUyMzA0NDI2NTksImgiOiI3NDk4ODRlNTg5NmE0ODFlZjViZTUwM2I1YWM0ZTY3NWI3OWU3NTgwZGI3ZGI2NzQyOTM2YTg1OTE2ZjgzYTM0In0=; _pxde=cf82500214e186095a780290e39918987f6fe7941cd2b03e7d2afe9c8e34f44c:eyJ0aW1lc3RhbXAiOjE2MTUyMzAxNDI2NTksImZfa2IiOjAsImlwY19pZCI6W119; find_tab=%23t5; search=start%7Chighcharts.js.map%7C1%7Cany%7CSGD%7C%7C%7C%7C%7C%7C%7C%7C%7Ce%7C%7C%7C%7CN%7C%7Ca%7C%7C%7C%7CCUR%7Cend',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document'}

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3722.400 QQBrowser/10.5.3739.400',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36']



def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session

def renew_ip():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password='password')
        controller.signal(Signal.NEWNYM)

def scrape_regions(c_soup):
    if c_soup.find('ul', {'class': 'top-level'}):
        sub_list = c_soup.find('ul', {'class': 'top-level'}).find_all('a')
        for sub in sub_list:
            new_soup = BeautifulSoup(session.get(base_url + sub.get('href'),headers=headers).content)
            print('Scraping sub-region: ' + sub.text)
            custom_sleep()
            scrape_regions(new_soup)
    else:
        next_page = scrape_wine_page(c_soup)
        while next_page:
            time.sleep(10)
            c_soup = BeautifulSoup(session.get(next_page, headers=headers).content)
            scrape_wine_page(c_soup)
            
        
def scrape_wine_page(c_soup):
    wines = c_soup.find_all('a', {'class':'wine-suggest-link'})
    for wine in wines:
        wine_dict = {}
        wine_url = base_url + wine.get('href')
        if wine_url in wines_dict:
            continue
        name = wine.text
        wine_dict['name'] = name
        print('Scraping wine ' + name + '\n')
        wine_dict.update(scrape_wines(wine_url))
        wines_dict[wine_url] = wine_dict 
        print(len(wine_dict))
        footer = c_soup.find('div', {'class': 'pager-container'})
        if footer:
            next_page = footer.find('a', {'title': 'Next page'})
            if next_page:
                return base_url + next_page.get('href')

def scrape_wines(wine_url):
    result = {}
    try:
        response = session.get(wine_url + '/#t2',headers=headers)
        w_soup = BeautifulSoup(response.content)
        profile = w_soup.find('div', {'class':'about-the-product'})
        fields = profile.find_all('div', {'class':'col-md-12'})
        for field in fields:
            title = field.find('span', {'class': 'smallish'}).text
            value = field.find('b').text
            result[title] = value 
        time.sleep(1)
        response2 = session.get(wine_url + '/#t5',headers=headers)
        custom_sleep()
        v_soup = BeautifulSoup(response2.content)
        vintages = v_soup.find('div', {'class': 'vintages-compare-list'})
        va = vintages.find_all('a', {'href': True})
        years = []
        for v in va:
            year = []
            for s in v.find_all('span'):
                year.append(s.text)
            years.append(year)
        result['years'] = years
    except:
        pass
    return result 

wines_dict = {}
base_url = 'https://www.wine-searcher.com'
url = 'https://www.wine-searcher.com/regions'
session = requests.session()
response = session.get(url, headers=headers)
soup = BeautifulSoup(response.content)
country_list = soup.find_all('ul', {'class': 'top-level'})[1]
countries = country_list.find_all('a')
for country in countries:
    country_url = base_url + country.get('href')
    c_soup = BeautifulSoup(session.get(country_url, headers=headers).content)
    scrape_regions(c_soup)
            
        



