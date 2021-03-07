#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 17:43:12 2021

@author: huaishen.li
"""

import pandas as pd
from common.utils import read_json_as_dict

data = read_json_as_dict('data', 'sg_data_120_150.json')

results = [
    (
        t["vintage"]["wine"]["winery"]["name"],
        f'{t["vintage"]["wine"]["name"]} {t["vintage"]["year"]}',
        t["vintage"]["wine"]["id"],
        t["vintage"]["statistics"]["ratings_average"],
        t["vintage"]["statistics"]["ratings_count"],
        t["price"]["amount"]

    )
    for _, r in data.items()
    for t in r["explore_vintage"]["matches"]
]

df = pd.DataFrame(results)
df.columns = ["winery", "name", "id", "rating", "rating_count", "price"]
print(df.head())
print(df.shape)
print(df["name"].nunique())
print(df["id"].nunique())
print(df["price"].min(), df["price"].max())