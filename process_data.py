#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 16:34:32 2021

@author: admin
"""
import pandas as pd
import json

df = pd.read_csv('data/vivino_wines_full.csv')

wine_type_map = {1: 'Red', 2: 'White', 3: 'Sparkling', 4: 'Rose', 7: 'Dessert',
                 24: 'Fortified'}
df['type_name'] = df['type_id'].map(lambda x: wine_type_map[x])

def count_top_5(column):
    temp = column.value_counts().nlargest(5)
    return temp.to_dict()
    
df_unique = df.drop_duplicates(subset=['wine_id'])
df_country = df_unique.groupby('country_name', as_index=False).agg({
    'wine_id': 'nunique',
    'winery_id': 'nunique',
    'winery_name': lambda x: count_top_5(x),
    'price': lambda x: [p for p in x if pd.notnull(p)],
    'type_name': lambda x: x.value_counts().to_dict(),
    'style_varietal_name': lambda x: x.value_counts().to_dict()
    })
df_country.columns = ['country', 'wine_count', 'winery_count', 'top_5_winery', 'prices', 
                      'type_count', 'style_count']
df_country = df_country.set_index('country')
df_country_dict = df_country.to_dict('index')

with open('data/countries2.geojson', 'r') as f:
    jsondata = json.load(f)

for record in jsondata['features']:
    name = record['properties']['admin']
    record['country'] = name
    record['properties'] = {'name': name}
    if name in df_country_dict:
        record['properties'].update(df_country_dict[name])
    
country = df['country_name'].unique()
country_list = set([data['properties']['admin'] for data in jsondata['features']])

for c in country:
    if c not in country_list:
        print(c)

with open('data/countries2.geo.json', 'w') as f:
    json.dump(jsondata, f)