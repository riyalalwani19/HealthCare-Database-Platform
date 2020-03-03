import matplotlib.pyplot as plt
import redis
from pymongo import MongoClient
from py2neo import Graph
from collections import Counter
from itertools import repeat, chain


## Intializations ###
result = []
result2 = []
result3 = []
drug =[]
disease = []
disease_drug = []
disease_drug2 = []
Drugsofdiseaseslist = []
Sortedlistelements =[]
Top5Drugs=[]

#Neo Graph and password
print("Please enter password for the Neo4j Graph")
Neo4JPwd = input()
graph = Graph(password=Neo4JPwd)

#Redis connection
r= redis.Redis(db=0)
pipeline = r.pipeline()

val = input("Please enter season number for your choice(1-4)\n"
            "(1 - Rainy,\n 2 - Summer,\n 3 - Winter,\n 4-Spring): ")

if (val == "1"):
    patterns = "*-0[6-9]-*SEARCH*"
    season = "rainy"
elif (val == "2"):
    patterns = "*-0[3-5]-*SEARCH*"
    season = "summer"
elif (val == "3"):
    patterns = "*-[10][0-1]-*SEARCH*"
    season = "winter"
else:
    patterns = "*-0[2-3]-*SEARCH*"
    season = "spring"

### Redis Search - for all seacrhed topics####
x = r.keys(pattern=patterns)

for y in x:
    pipeline.lrange(y, 0, 100)

result = pipeline.execute()

for y in result:
    result2.append(y[0].decode('utf-8')) ###decoding the elements(removing eccoding)

# sorted(result2, key=result2.count, reverse=True)
result2 = list(chain.from_iterable(repeat(i, c) for i,c in Counter(result2).most_common())) ###sorting the elemts on basis of count
result3 = list(dict.fromkeys(result2))  ###removing duplicates

### Mongo Search - for filter out drugs from search topics####
conn = MongoClient()
db = conn.Information_Systems

drug = [y['Drug_Name'] for temp in result3 for y in db.Drugs.find({"Drug_Name": temp}, {"Drug_Name": 1, "_id": 0})]


## Mongo Search - for filter out diseases from search topics####
disease = [y['Disease']for temp in result3 for y in db.disease.find({"Disease": temp}, {"Disease": 1, "_id": 0})]

### Neo Search - to find drug of the diseases####

disease_drug = [graph.run("""match(n:Disease)<-[:Medicine_For]-(b) where n.name=\"""" + \
                temp2 + """\" return b.Drug_Name as Drug""").data() for temp2 in disease]

disease_drug2 = list2 = [x for x in disease_drug if x != []] ###remove null elements list

for irr1 in disease_drug2:
    for irr2 in irr1:
        drugs = irr2.get('Drug')
        Drugsofdiseaseslist.append(drugs)

def Sort_Tuple(tup):
    return (sorted(tup, key=lambda x: x[1],reverse=True))

counts = Counter(drug)
counts.update(Drugsofdiseaseslist)
Sortedlistelements =Sort_Tuple(counts.items())
Top5Drugs = Sortedlistelements[:10]
newdict = dict(Top5Drugs)
names = list(newdict.keys())
values = list(newdict.values())

# bar graph for top 5 drugs
plt.figure(figsize=(12, 12))
plt.bar(range(len(newdict)), values, tick_label=names)
plt.xticks(range(len(newdict)), names, rotation=90)
plt.xlabel('Drugs', fontsize=18)
plt.ylabel('Count of Drugs', fontsize=16)
plt.savefig(season + '.png', bbox_inches='tight')
print("Output Figure is saved with respective season name for more clarity")
print("displaying top 10 trending drugs for", season + " season")
plt.show()
# #