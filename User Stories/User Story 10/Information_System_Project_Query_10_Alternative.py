import redis
import pandas as pd
from datetime import datetime, timedelta
from matplotlib import pyplot
import json
import re
import numpy as np

r = redis.Redis(db=0, decode_responses=True)

dates = []
keys = []
values = []
locations = []
frequency = []
for key in r.scan_iter("*08-12-2019*:USER"):
    if key.split(":")[2] != 'USER':
        pattern = ":(.*?):USER"
        key_date = datetime.strptime(re.search(pattern, key).group(1), "%d-%m-%Y:%H:%M:%S")
        dates.append(key_date)
        frequency.append(int(1))
        keys.append(key)
        return_value= r.smembers(key)
        value = [str(data) for data in return_value]
        values.append(value)
        locations.append(key.split(':')[0])

if keys == []:
    print("Keys doesnot exist in redis for the given pattern. please change the pattern and try again")
    exit()

df = pd.DataFrame(zip(keys, dates, values, locations), columns= ('keys', 'dates', 'values', 'locations'))

rows = []
_ = df.apply(lambda row: [rows.append([row['keys'], row['dates'], nn, row['locations']]) for nn in row['values']], axis = 1)

df_new = pd.DataFrame(rows, columns=df.columns).set_index('dates')

df_date = df_new.groupby([pd.Grouper(freq='1H')], axis=1)['values'].apply(list).reset_index(name = 'users')
df_date['dates'] = df_date['dates'].dt.time

df_date = df_date.groupby('dates')['users'].apply(list).reset_index(name = 'users')
df_date = df_date.set_index('dates')

values_f = []
values_c = []
dates_f = []
i =0
max_lim = 8

while i<len(df_date) and max_lim<=len(df_date):
    if i<max_lim:
        data = df_date['users'][i:max_lim][0:8].explode()
        values_f.append([q for q in data])
        date = str(df_date.index[i]) + '-' + str(df_date.index[max_lim-1]).replace('00:00','59:59')
        dates_f.append(date)
    i = i+1
    max_lim = max_lim+1

df_f = pd.DataFrame(zip(dates_f, values_f), columns = ('time','users'))

vals = df_f['users'].values.tolist()
rs = [len(r) for r in vals]    
a = np.repeat(df_f['time'], rs)

df = pd.DataFrame(np.column_stack((a, np.concatenate(vals))), columns=df_f.columns)

rows = []
_ = df.apply(lambda row: [rows.append([row['time'], nn]) for nn in row['users']], axis = 1)

df_fc = pd.DataFrame(rows, columns=df_f.columns)
df_fc = df_fc.groupby('time')['users'].nunique().reset_index(name = 'count').nlargest(5, 'count')

print(df_fc)

df_date = df_new.groupby([pd.Grouper(freq='8H')])['values'].apply(list).reset_index(name='users')
df_date['dates'] = df_date['dates'].dt.time
rows = []
_ = df_date.apply(lambda row: [rows.append([row['dates'], nn]) for nn in row['users']], axis = 1)
df_8h = pd.DataFrame(rows, columns=df_date.columns)
df_8h = df_8h.groupby('dates')['users'].nunique().reset_index(name = 'count')
df_8h['time']= ['00:00:00-07:59:59','08:00:00-15:59:59','16:00:00-23:59:59']

fig, axes = pyplot.subplots(nrows=1, ncols=2)

ax = df_fc.plot(kind='bar',x='time',y='count', color = 'Turquoise', ax=axes[0])
axes[0].set_xlabel('Best 8 hours bucket (continuous next)')
axes[0].set_ylabel('Number of unique users')
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
fig.autofmt_xdate()

ax = df_8h.plot(kind='bar',x='time',y='count', color = 'Gold',ax=axes[1])
axes[1].set_xlabel('Best 8 hours bucket')
axes[1].set_ylabel('Number of unique users')
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
fig.autofmt_xdate()

df_loc = df_new.groupby(['locations'])['values'].nunique().sort_values(ascending=False).reset_index(name = 'count').nlargest(10,'count')

df_datloc=df_new.groupby([pd.Grouper(freq='1H'),'locations'])['values'].nunique().reset_index(name = 'count')
df_datloc['dates'] = df_datloc['dates'].dt.time
ax = df_datloc.groupby(['dates','locations']).mean().unstack().plot(kind='line', stacked=True)
pyplot.xlabel('Hourly trend')
pyplot.ylabel('Locations')
pyplot.legend(df_datloc['locations'].unique())
pyplot.xticks(rotation=0)
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))

print(df_loc.head())


ax = df_loc.plot(kind='bar',x='locations',y='count')
pyplot.xlabel('Locations')
pyplot.ylabel('Number of unique users')
pyplot.xticks(rotation=0)
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))

pyplot.show()
