#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 16:34:32 2021

@author: admin
"""
import pandas as pd
import json
import numpy as np

df = pd.read_csv('data/vivino_wines_full.csv')
wine_type_map = {1: 'Red', 2: 'White', 3: 'Sparkling', 4: 'Rose', 7: 'Dessert',
                 24: 'Fortified'}
# df['price'] = df['id'].map(lambda x:None if str(x) not in new_result \
#                            else (new_result[str(x)]['price']['amount'] if pd.notnull(new_result[str(x)]['price']) else new_result[str(x)]['median']['amount']) )
df['type_name'] = df['type_id'].map(lambda x: wine_type_map[x])

def count_top_5(column):
    temp = column.value_counts().nlargest(5).to_dict()
    return [{'name': k, 'value': v} for k, v in temp.items()]

def count_freq(column):
    temp = column.value_counts().to_dict()
    return [{'name': k, 'value': v} for k, v in temp.items()]

def count_element_freq(column):
    temp = [d for c in column.values if len(c) > 0 for d in c]
    result = {}
    for t in temp:
        wid = t['id']
        if wid not in result:
            result[wid] = {'name': t['name'], 'count': 1}
        else:
            result[wid]['count'] += 1
    return list(result.values())

df_unique = df.drop_duplicates(subset=['wine_id'])
df_unique_output = df_unique.set_index('wine_id').rename(columns={'name.1': 'wine_name'})
df_unique_output = df_unique_output[['wine_name', 'rating', 'rating_count', 'price',
                                     'flavor', 'winery_id', 'winery_name', 'region_id',
                                     'region_name', 'country_name', 'style_name', 
                                     'style_varietal_name', 'type_name', 'style_grapes']]
df_unique_output['style_grapes'] = df_unique_output['style_grapes'].map(lambda x: eval(x) if pd.notnull(x) else [])
df_unique_output['flavor'] = df_unique_output['flavor'].map(lambda x: eval(x) if pd.notnull(x) else [])
#df_unique_json = df_unique_output.to_json(orient='index')

df_country = df_unique.groupby('country_name', as_index=False).agg({
    'wine_id': 'nunique',
    'winery_id': 'nunique',
    'winery_name': lambda x: count_top_5(x),
    'price': lambda x: [p for p in x if pd.notnull(p)],
    'type_name': lambda x: count_freq(x),
    'style_name': lambda x: count_freq(x)
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

# country = df['country_name'].unique()
# country_list = set([data['properties']['admin'] for data in jsondata['features']])

# for c in country:
#     if c not in country_list:
#         print(c)

with open('processed/countries.geo.json', 'w') as f:
    json.dump(jsondata, f)
    
# with open('processed/wine_data.json', 'w') as f:
#     json.dump(df_unique_json, f)

df_winery = df_unique_output.groupby(['country_name', 'region_name', 'winery_name'], as_index=False).agg({'rating': 'count', 
      'price': np.median,
      'type_name': lambda x: count_freq(x), 
      'style_grapes': lambda x: count_element_freq(x)})
df_winery.columns = ['country_name', 'region_name', 'winery_name', 'wine_count', 'price', 'type_count', 'grape_count']
df_winery['rank'] = df_winery.groupby('country_name')['wine_count'].rank('min', ascending=False)
df_winery_100 = df_winery[df_winery['rank'] <= 50].drop(columns=['rank']).set_index(['country_name', 'region_name', 'winery_name'])

df_winery_country = df_unique_output.groupby('country_name').agg({'rating': 'count', 
      'winery_id': 'nunique',
      'price': np.median,
      'type_name': lambda x: count_freq(x), 
      'style_grapes': lambda x: count_element_freq(x)})
df_winery_country.columns = ['wine_count', 'winery_count', 'price', 'type_count', 'grape_count']

df_winery_region = df_unique_output.groupby(['country_name', 'region_name']).agg({'rating': 'count', 
      'winery_id': 'nunique',    
      'price': 'mean',                                                                        
      'type_name': lambda x: count_freq(x), 
      #'style_name': lambda x:count_freq(x), 
      'style_grapes': lambda x: count_element_freq(x)})
df_winery_region.columns = ['wine_count', 'winery_count', 'price', 'type_count', 'grape_count']

df_winery_dict = df_winery_country.to_dict(orient='index')
for country, values in df_winery_dict.items():
    values['name'] = country
    df_temp = df_winery_region[df_winery_region.index.get_level_values('country_name') == country].droplevel(0)
    values['children'] = []
    dict_temp = df_temp.to_dict('index')
    for region, v in dict_temp.items():
        region_temp = df_winery_100[(df_winery_100.index.get_level_values('country_name') == country) & (df_winery_100.index.get_level_values('region_name') == region)].droplevel([0, 1])
        if region_temp.shape[0] == 0:
            continue
        region_temp['name'] = region_temp.index
        v['name'] = region
        v['children'] = list(region_temp.to_dict('index').values())
        values['children'].append(v)
        
winery_output = list(df_winery_dict.values())
with open('processed/wine_data.json', 'w') as f:
    json.dump(winery_output, f)