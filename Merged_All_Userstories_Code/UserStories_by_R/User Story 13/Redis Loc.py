#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 22:32:40 2020

@author: abhinavparashar
"""

import redis
from pymongo import MongoClient
from py2neo import Graph
import pandas as pd

## Initialization ##
result = []
result2 = []
location = []

r= redis.Redis(db=0, decode_responses = True)

## Redis Search for Locations ##
x = r.keys(pattern="*SEARCH*")
for y in x:
    key_loc = y.split(':')[0]
    
    location.append(key_loc)
    
    result.append(r.lrange(y, 0, 100))

for y in result:
    result2.append(y[0])


result3 = list(dict.fromkeys(result2))


df = pd.DataFrame(zip(location,result), columns = ('Location','Search'))

rows = []
_ = df.apply(lambda row: [rows.append([row['Location'], nn]) for nn in row['Search']], axis = 1)

df_new = pd.DataFrame(rows, columns=df.columns)

df_new.to_csv("Downloads/Redis_D.csv")