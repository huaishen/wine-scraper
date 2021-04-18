#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 16:34:32 2021

@author: admin
"""
import pandas as pd
import json
import math
import re
import numpy as np
from shapely.geometry import Point
from shapely_geojson import dumps, Feature, FeatureCollection

df = pd.read_csv('data/vivino_wines_updated.csv')
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

df_unique = df.drop_duplicates(subset=['wine_id']).rename(columns={'name.1': 'wine_name'})
df_unique_output = df_unique.set_index('wine_id')
df_unique_output = df_unique_output[['wine_name', 'rating', 'rating_count', 'price',
                                     'flavor', 'winery_id', 'winery_name', 'region_id',
                                     'region_name', 'country_name', 'style_id', 'style_name', 
                                     'style_varietal_name', 'type_name', 'style_grapes', 'style_food']]
df_unique_output['style_grapes'] = df_unique_output['style_grapes'].map(lambda x: eval(x) if pd.notnull(x) else [])
df_unique_output['style_food'] = df_unique_output['style_food'].map(lambda x: eval(x) if pd.notnull(x) else [])
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


with open('processed/countries.geo.json', 'w') as f:
    json.dump(jsondata, f)
    

df_winery = df_unique_output.groupby(['country_name', 'region_name', 'winery_name'], as_index=False).agg({'rating': 'count', 
      'price': np.median,
      'type_name': lambda x: count_freq(x), 
      'style_grapes': lambda x: count_element_freq(x)})
df_winery.columns = ['country_name', 'region_name', 'winery_name', 'wine_count', 'price', 'type_count', 'grape_count']
df_winery['rank'] = df_winery.groupby('country_name')['wine_count'].rank('min', ascending=False)
df_winery_100 = df_winery[df_winery['rank'] <= 50].drop(columns=['rank']).set_index(['country_name', 'region_name', 'winery_name'])
df_winery_100['price'] = df_winery_100['price'].fillna(0)

df_winery_country = df_unique_output.groupby('country_name').agg({'rating': 'count', 
      'winery_id': 'nunique',
      'price': np.median,
      'type_name': lambda x: count_freq(x), 
      'style_grapes': lambda x: count_element_freq(x)})
df_winery_country.columns = ['wine_count', 'winery_count', 'price', 'type_count', 'grape_count']
df_winery_country['price'] = df_winery_country['price'].fillna(0)

df_winery_region = df_unique_output.groupby(['country_name', 'region_name']).agg({'rating': 'count', 
      'winery_id': 'nunique',    
      'price': np.median,                                                                        
      'type_name': lambda x: count_freq(x), 
      #'style_name': lambda x:count_freq(x), 
      'style_grapes': lambda x: count_element_freq(x)})
df_winery_region.columns = ['wine_count', 'winery_count', 'price', 'type_count', 'grape_count']
df_winery_region['price'] = df_winery_region['price'].fillna(0)

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

# Price
df_price = df_unique_output[['country_name', 'region_name', 'winery_name', 'type_name', 'price']].dropna()
price_dict = df_price.to_dict('records')
with open('processed/wine_price.json', 'w') as f:
    json.dump(price_dict, f)

# Location
import googlemaps
api_key = 'AIzaSyBN5DGexhkC9Nlz73J27tqawb5FCrJfBfA'
g = googlemaps.Client(key='AIzaSyBN5DGexhkC9Nlz73J27tqawb5FCrJfBfA')
failed_row = set()
for _, row in df_winery_region.iloc.iterrows():
    location = row.name
    print(location)
    country = location[0]
    region = location[1]
    r = g.geocode(f'{region}, {country}')
    if len(r) == 0:
        failed_row.add(location)
        continue
    result = r[0]['geometry']['location']
    df_winery_region.loc[location, 'latitude'] = result['lat']
    df_winery_region.loc[location, 'longitude'] = result['lng']
    
features = []
for _, row in df_winery_region.iterrows():
    feature = Feature(Point(row['longitude'], row['latitude']), {'type_count': row["type_count"],
                                                                 'wine_count': row["wine_count"],
                                                                 'winery_count': row["winery_count"]})
    features.append(feature)
feature_collection = FeatureCollection(features)


with open('processed/wine_geo.json', 'w') as f:
    json.dump(dumps(feature_collection, indent=2), f)

# Style food
#df_style_food = df_unique.groupby(['style_id', 'style_name'], as_index=False)['style_food'].max().dropna()
food_dict = {}
food_link_dict = {}
def parse_style_food(x):
    for i, v in enumerate(x):
        vid = v['id']
        if vid not in food_dict:
            food_dict[vid] = v
            food_dict[vid]['count'] = 1
        else:
            food_dict[vid]['count'] += 1
        for j in range(i + 1, len(x)):
            vid2 = x[j]['id']
            v1 = food_link_dict.get((vid, vid2), 0) 
            v2 = food_link_dict.get((vid2, vid), 0) 
            if ((v1 + v2) == 0) or (v1 != 0):
                food_link_dict[(vid, vid2)] = v1 + 1
            else:
                food_link_dict[(vid2, vid)] = v2 + 1
        
        
def match_food_category(x, category_list):
    for key, value in category_list.items():
        if x in value:
            return key 
        
with open('food_style_match.json', 'r') as f:
    food_style_match = json.loads(f.read())
df_unique_output['style_food'].map(parse_style_food)
food_list = list(food_dict.values())
food_df = pd.DataFrame(food_list)
prefix = '//images.vivino.com/backgrounds/foods/thumbs/' 
pattern = '(?<=foods/)(.+)(?=\.png)'
food_df['image'] = food_df['background_image'].map(lambda x: prefix + re.search(pattern, x['location'])[0] + '_932x810.png')
food_df['group'] = food_df['id'].apply(lambda x: match_food_category(x, food_style_match))

wine_style_food = df_unique_output.groupby(['style_id', 'style_name'], as_index=False) \
.agg({'style_food': 'first', 'wine_name': 'count', 'type_name': 'first'}).rename(columns={'wine_name': 'count'})
wine_style_food = wine_style_food[wine_style_food['style_food'].map(len) != 0].sort_values('count', ascending=False)

wine_type = wine_style_food.groupby('type_name')['count'].count().to_dict()
wine_style_output = pd.DataFrame()
frac = 0.5
for type_name, count in wine_type.items():
    temp = wine_style_food[wine_style_food['type_name'] == type_name]
    if temp.shape[0] >= 30:
        wine_style_output = pd.concat([wine_style_output, temp.iloc[:35].sample(15, random_state=2)])
    else:
        num = min(math.ceil(temp.shape[0] * 0.5), 4)
        wine_style_output = pd.concat([wine_style_output, temp[:8].sample(num, random_state=2)])
wine_style_output['group'] = 'Wine'
wine_style_output.columns = ['id', 'name', 'style_food', 'count', 'type_name', 'group']
wine_style_output['id'] = wine_style_output['id'].map(lambda x: 'w' + str(int(x)))

food_wine_df = pd.concat([food_df, wine_style_output])[['id', 'name', 'image', 'group', 'type_name']]
food_wine_df.to_json('processed/style_food_data.json', 'records')

def count_topN_orderBy(df, column, n, ascending=False):
    return df.sort_values(column, ascending=ascending).head(n).to_dict('records')
wine_style_ids = wine_style_output['id'].apply(lambda x: int(x.split('w')[1]))
df_food_wine = df_unique[df_unique['style_id'].isin(wine_style_ids)]
df_food_wine_gb = df_food_wine.groupby('style_id').apply(lambda x: count_topN_orderBy(x, 'rating', 5)).reset_index()
df_food_wine_gb['style_id'] = df_food_wine_gb['style_id'].map(lambda x: 'w' + str(int(x)))
df_food_wine_gb.columns = ['id', 'wines']
df_food_wine_gb.to_json('processed/style_wines.json', 'records')


def parse_style_food_link(x, column_name):
    for i, v in enumerate(x[column_name]):
        pair = (x['id'], v['id']) 
        if pair not in food_link_dict:
            food_link_dict[pair] = x['count']

wine_style_output.apply(lambda x: parse_style_food_link(x, 'style_food'), axis=1)
food_link_df = pd.DataFrame([[key[0], key[1], value] for key, value in food_link_dict.items()], columns=['source', 'target', 'count'])
food_link_df.to_json('processed/style_food_link.json', 'records')



## Radar Chart
def count_top_n(column, n):
    temp = column.value_counts().nlargest(n).to_dict()
    return list(temp.keys())
radar_count_map = {'Red': 8, 'White':8, "Sparkling": 4, 'Rose': 4, 'Fortified': 4, 'Dessert': 4}
radar_cols = ['rating', 'price', 'acidity', 'intensity', 'fizziness', 'sweetness', 'tannin', 'style_varietal_name',
              'type_name', 'type_id']
df_radar = df_unique[pd.notnull(df_unique['style_varietal_name']) & (~df['style_varietal_name'].isin(radar_count_map.keys()))][radar_cols].reset_index(drop=True)
df_radar_type = df_radar.groupby('type_name').apply(lambda x: count_top_n(x['style_varietal_name'], 
                                                                          radar_count_map[max(x['type_name'])])).to_dict()
df_radar['keep'] = df_radar.apply(lambda x: x['style_varietal_name'] in df_radar_type[x['type_name']], axis=1)
df_radar[df_radar.keep].to_csv('processed/sliced.csv', index=False)


