import sys
import redis
import pandas as pd
from py2neo import Graph
import matplotlib.pyplot as plt

graph = Graph(password="Information_Systems")
drug_in = input("Please enter your Drug Name: ")
result3 = graph.run("match (a:Drug)-[:Medicine_For]->()<-[:Medicine_For]-(b:Drug) where a.Drug_Name='"+ drug_in +"' return b.Drug_Name").data()

if not result3:
    print("Drug Name entered didn't match any drug names in the database. Hence ending script.")
    sys.exit(1)

print("This will take around 30 seconds...")

plt.style.use("ggplot")

r = redis.Redis(db=0)
pipeline = r.pipeline()

result = []
disease_list = []
trend_list = []
result2 = []
x = r.keys(pattern="*SEARCH*")

for y in x:
    temp = {}
    temp['Key'] = y.decode("utf-8").split(":")[1][3:]
    pipeline.lrange(y, 0, 100)
    result.append(temp)

pip = pipeline.execute()

for var,car in zip(result,pip):
    temp = {}
    temp['Key'] = var['Key']
    temp['Value'] = car[0].decode("utf-8")
    result2.append(temp)


df1 = pd.DataFrame(result2)
df1['Key'] = pd.to_datetime(df1['Key'],format='%m-%Y')

for z in result3:
    disease_list.append(z['b.Drug_Name'])

disease_list = list(set(disease_list))

print("Competitor Drugs: -")
flag = 0
for dl in disease_list:
    flag = flag + 1
    print(flag,".",dl)

comp_in = input("Please enter name of Competitor Drug you wanna see trend with - ")

if comp_in not in disease_list:
    print("Entered Competitor Drug wasn't from the list. Hence ending program.")
    sys.exit(1)

trend_list.append(drug_in)
trend_list.append(comp_in)

df2 = df1[df1['Value'].isin(trend_list)]
df3 = df2.groupby(['Key','Value']).size().reset_index(name='counts')

final = pd.pivot_table(df3, index=['Key'],columns = ['Value'], fill_value=0)
final.columns = final.columns.droplevel(0)
final.sort_values(by = ['Key'])

final.plot(figsize = (20,10)).legend(title='Drugs')
plt.show()
