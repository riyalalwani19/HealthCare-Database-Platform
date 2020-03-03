import redis
import sys
from pymongo import MongoClient
from py2neo import Graph
import pandas as pd
from collections import Counter
from itertools import repeat, chain

## Intializations ###

result = []
result2 = []
disease = []
disease_final = []
disease_drug = []
disease_drug2 = []
disease_drug3 = []
disease_drug4 = []
temp_se = {}
result40 = []

graph = Graph(password="Information_Systems")

r= redis.Redis(db=0)
pipeline = r.pipeline()

### Redis Search - for all seacrhed topics####
val = input("Please enter Month(in 2 digit format) of your choice: ")

if len(val) != 2:
    print("You didn't enter a 2 digit month code hence terminating program")
    sys.exit(1)

if int(val) <=0 or int(val)>12:
    print("You didnt enter a valid month digit hence terminating program")
    sys.exit(1)

print("Please wait for few seconds...")
pattern = "*-"+val+"-*SEARCH"
x = r.keys(pattern=pattern)
for y in x:
    pipeline.lrange(y, 0, 100)

result = pipeline.execute()


for y in result:
    result2.append(y[0].decode('utf-8'))

result2 = list(chain.from_iterable(repeat(i, c) for i,c in Counter(result2).most_common()))
result3 = list(dict.fromkeys(result2))


### Mongo Search - for filter out diseases from search topics####
client = MongoClient()
for temp in result3:
    x = client.Information_System.disease.find({"Disease": temp}, {"Disease": 1, "_id": 0})
    for y in x:
        disease.append(y['Disease'])


### Neo Search - to find drug of the diseases####
for temp2 in disease:
    query = """match(n:Disease)<-[:Medicine_For]-(b) where n.name=\"""" + \
                temp2 + """\" return n.name as Disease,b.Drug_Name as Drug"""
    neo_result = graph.run(query).data()
    disease_drug.append(neo_result)

disease_drug2 = list2 = [x for x in disease_drug if x != []]



### Mongo Search for side effects of the drugs ###
for irr1 in disease_drug2:
    for irr2 in irr1:
        drug = irr2.get('Drug')
        disease5 = irr2.get('Disease')
        pipeline = [{"$match": {"Drug_Name": drug}},{"$project": {"Drug_Name": 1, "_id": 0, "Side_Effects": {
            "$switch": {"branches": [{"case": {"$eq": ["$Side_Effects", None]}, "then": "Blank"}],
                        "default": "$Side_Effects"}}}}]
        result4 = client.Information_System.Drugs.aggregate(pipeline)
        for irr3 in result4:
            irr3['Disease'] = disease5
            disease_drug3.append(irr3)

# print(disease_drug3)

### Grouping and filtering for final result ###
for curr in disease_drug3:
    temp_se={}
    side_effects = curr.get('Side_Effects')
    if side_effects == 'Blank':
        count_se = 0
    else:

        if "following:" in side_effects:
            side_effects2 = side_effects.split("following:")
            count_se =side_effects2[1].count('\n') - 1
        else:
            count_se = 1

    temp_se['Disease'] = curr.get('Disease')
    temp_se['Drug'] = curr.get('Drug_Name')
    temp_se['No_Of_SE'] = count_se
    disease_drug4.append(temp_se)

df_se = pd.DataFrame(disease_drug4)


df_se_2 = df_se.groupby(['Disease']).agg({'No_Of_SE':['min']}).reset_index()
df_se_2.columns = df_se_2.columns.droplevel(1)
df_se_3 = []
df_se_4 = pd.DataFrame([], columns=list(['Disease','Drug','No_Of_SE']))

for index, row in df_se_2.iterrows():
    filter_1 = df_se["Disease"] == row['Disease']
    filter_2 = df_se["No_Of_SE"] == row['No_Of_SE']
    df_se_4 = df_se[filter_1 & filter_2]
    for index, row in df_se_4.iterrows():
        temp_se_2 = {}
        temp_se_2['Disease'] = row['Disease']
        temp_se_2['Drug'] = row['Drug']
        temp_se_2['No_Of_SE'] = row['No_Of_SE']
        result40.append(temp_se_2)

result_df = pd.DataFrame(result40)
pd.set_option('display.max_colwidth',-1)
result_df = result_df.drop_duplicates()
final = result_df.groupby('Disease').agg({'Drug': ['min']}).reset_index()
final.columns = final.columns.droplevel(1)



for kor in disease_drug3:
    disease_final.append(kor['Disease'])

seen = set()
seen_add = seen.add
gog= [x for x in disease_final if not (x in seen or seen_add(x))]
gog2= gog[:10]

final2 = final[final['Disease'].isin(gog2)]

print(final2.to_string(index=False,justify = 'left'))
