from py2neo import Graph, Node, Relationship
import pandas as pd
from pymongo import MongoClient
import json
import redis
from datetime import datetime
import time
from random_username.generate import generate_username
import re
from bson.objectid import ObjectId

print("Please enter password for the Neo4j Graph")
inp = input()

if inp == '':
    print("Please enter password and try again")
    exit()

# graph = Graph(password="graph_data")
graph = Graph(password=inp)

print("Enter the symptoms with space")
inp = [str(i).lower() for i in input().split()]

if inp == []:
    print("Entered input is not valid.Please try again by entering symptoms with space")
    exit()

for i in range(len(inp)):
    try:
        results = graph.run('''match (s:Symptom)
        Where toLower(s.name) = $symptom
        return DISTINCT s.name as Symptoms''', parameters={'symptom' : inp[i]}).data()
    except:
        print("Entered Neo4j graph password is wrong. Please try again")
        exit()
    if results == []:
        print(f"Symptom '{inp[i]}' does not exists in our database. Please try again")
        exit()
    
results = graph.run('''with $in as symptoms
match (s:Symptom)
Where toLower(s.name) in symptoms
with collect(s) as symptoms
match (d:Disease)
where all(s in symptoms Where (s)-[:CAUSES]->(d))
return DISTINCT d.name as Disease, d.id as Disease_id''', parameters={'in' : inp}).data()

now = datetime.now()
current_time = now.strftime("%d-%m-%Y:%H:%M:%S")
username = ''.join(map(str, generate_username(1)))

r = redis.Redis()

if results == []:
    print(f"Tring.. Tring..... Tring............  database does not have any disease associated with mentioned symptoms {inp}")
    print("--------------------------------------------------------------------------------")
    for i in range(len(inp)):
        key = 'NODISEASE' + ':' + current_time + ':' + username.upper()
        r.lpush(key, inp[i].upper())
        print(f"Search data {inp[i].upper()} inserted into Redis with key {key} for further validation")
    print("--------------------------------------------------------------------------------")
    exit()

record_ids = [record['Disease'].lower() for record in results]
record_ids2 = [ObjectId(record['Disease_id']) for record in results]
print(f"{inp} symptoms causes disease(s) {record_ids}")

client = MongoClient()
db = client['Information_System']
collection = db.Disease

print("--------------------------------------------------------------------------------")
for i in range(len(inp)):
    key = 'SYMPTOMS' + ':' + current_time + ':' + username.upper()
    r.lpush(key, inp[i].upper())
    print(f"Search data {inp[i].upper()} inserted into Redis with key {key}")
print("--------------------------------------------------------------------------------")

inp1 = input("You want to know more about Diseases and their treatments (y/n):").lower()
if inp1 != 'y':
    exit()

print("Please enter Disease you want to know from above list, enter all if you want to know about all Diseases:")
disease = input().lower()

if disease != 'all' and disease in record_ids:
    query = collection.find({'Disease':re.compile(disease, re.IGNORECASE)})
    df = pd.DataFrame(query)
    for index, row in df.iterrows():
        print("--------------------------------------------------------------------------------")
        print(f"{inp} causes '{row['Disease']}'")
        print(f"please find some treatements for '{row['Disease']}''")
        print(row['Diagnosis_treatment'])
        if 'Specialization' in row:
            print(f"This '{row['Disease']}' can be treated by doctors having specialization of {row['Specialization']['Name']}")
        key = 'DISEASE' + ':' + current_time + ':' + username.upper()
        r.lpush(key, row['Disease'].upper())
        print("--------------------------------------------------------------------------------")
        print(f"Search data {row['Disease'].upper()} inserted into Redis with key {key}")
else:
    if disease == 'all':
        print(record_ids2)
        query = collection.find({'_id':{'$in': record_ids2}})
        df = pd.DataFrame(query)
        for index, row in df.iterrows():
            print("---------------------------------------------------------------------------------------------")
            print(f"{inp} causes '{row['Disease']}'")
            print(f"please find some treatements for '{row['Disease']}''")
            print(row['Diagnosis_treatment'])
            if 'Specialization' in row:
                  if not pd.isna(row['Specialization']):
                    print(f"This '{row['Disease']}' can be treated by doctors with specialization of {row['Specialization']['Name']}")
            key = 'DISEASE' + ':' + current_time + ':' + username.upper()
            r.lpush(key, row['Disease'].upper())
            print("--------------------------------------------------------------------------------")
            print(f"Search data {row['Disease'].upper()} inserted into Redis with key {key}")
            print("--------------------------------------------------------------------------------")
    else:
        print(f"Entered {disease} doesnot exist in our database. Thank you for choosing healthcare engine")
