#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 16:53:20 2021

@author: admin
"""
import requests 
import random
import time

url = 'https://www.vivino.com/api/prices'

new_result = {}
a = list(df['id'])

def custom_sleep():
    s = random.randint(2000, 4000) / 1000
    time.sleep(s)

batch = 150

for i in range((len(a) // batch) + 1):
    print(i)
    temp = a[(i * batch): (i * batch + batch)]
    r = requests.get(url, params = {'vintage_ids[]': temp}, headers=HEADERS)
    if r.status_code < 400:
        new_result.update(r.json()['prices']['vintages'])
    else:
        print('Error!')
    custom_sleep()