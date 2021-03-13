#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 17:43:12 2021

@author: huaishen.li
"""
import os
import pandas as pd
from common.utils import read_json_as_dict

directory_name = 'data'
directory = os.fsencode(directory_name)
data = []
for file in os.listdir(directory):
    file_name = os.fsdecode(file)
    print(file_name)
    temp = read_json_as_dict(directory_name, file_name)
    data += [value['explore_vintage']['matches'] for _, value in temp.items()]


def parse_wine(record):
    result = []
    result += [record['vintage']['id'],
               record['vintage']['year'],
               record['vintage']['name'],
               record['vintage']['statistics']['ratings_average'],
               record['vintage']['statistics']['ratings_count'],
               record['vintage']['wine']['name'],
               record['vintage']['wine']['id'],
               record['vintage']['wine']['type_id'],
               record['vintage']['wine']['taste']['flavor']]
    if record['vintage']['wine']['winery']:
        result += [record['vintage']['wine']['winery']['id'],
               record['vintage']['wine']['winery']['name']]
    else:
        result += [None] * 2 
        
    if record['price']:
        result += [record['price']['amount']]
    else:
        result += [None]
        
    if record['vintage']['wine']['region']:
        result += [record['vintage']['wine']['region']['name'],
                   record['vintage']['wine']['region']['id'],
                   record['vintage']['wine']['region']['country']['name'],
                   record['vintage']['wine']['region']['country']['code']]
    else:
        result += [None] * 4
    if record['vintage']['wine']['taste']['structure']:
        result += [record['vintage']['wine']['taste']['structure']['acidity'],
                   record['vintage']['wine']['taste']['structure']['fizziness'],
                   record['vintage']['wine']['taste']['structure']['intensity'],
                   record['vintage']['wine']['taste']['structure']['sweetness'],
                   record['vintage']['wine']['taste']['structure']['tannin']]
    else:
        result += [None] * 5
    if record['vintage']['wine']['style']:
        result += [record['vintage']['wine']['style']['id'],
                   record['vintage']['wine']['style']['name'],
                   record['vintage']['wine']['style']['regional_name'],
                   record['vintage']['wine']['style']['region']['id'] if record['vintage']['wine']['style'][
                       'region'] else None,
                   record['vintage']['wine']['style']['varietal_name'],
                   record['vintage']['wine']['style']['body'],
                   record['vintage']['wine']['style']['body_description'],
                   record['vintage']['wine']['style']['acidity'],
                   record['vintage']['wine']['style']['acidity_description'],
                   record['vintage']['wine']['style']['food'],
                   record['vintage']['wine']['style']['grapes']]
    else:
        result += [None] * 11
    return result


results = [parse_wine(record) for page in data for record in page]
df = pd.DataFrame(results)
df.columns = ['id', 'year', 'name', 'rating', 'rating_count', 'name', 'wine_id', 'type_id',
              'flavor', 'winery_id', 'winery_name', 'price',
              'region_name', 'region_id', 'country_name', 'country_code', 
              'acidity', 'fizziness', 'intensity', 'sweetness', 'tannin',
              'style_id', 'style_name', 'style_region_name', 'style_region_id', 'style_varietal_name',
              'style_body', 'style_body_desp', 'style_acidity',
              'style_acidity_desp', 'style_food', 'style_grapes']
df.drop_duplicates(subset='id')
df.to_excel('output/vivino_wines.xlsx', index=False)
