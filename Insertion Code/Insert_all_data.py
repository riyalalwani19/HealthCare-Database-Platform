import pandas as pd
import json
from py2neo import Graph, Node, Relationship
from collections import OrderedDict
from pymongo import MongoClient
import xlrd
import redis
import csv

#Mongo Db Connection
try:
    client = MongoClient()
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")

# database
db = client.Information_System

#file location
fl = input("Enter Location for all dowloaded files: ")
fl = fl.replace("\\","/")

#Graph password
print("Please enter password for the Neo4j Graph")
inp = input()

if inp == '':
    print("Please enter password and try again")
    exit()

graph = Graph(password=inp)


#--------------------------------------------------------------------------------------------------------
#Location Data insertion

graph.run("""LOAD CSV WITH HEADERS FROM 'file:///""" + fl + """/pincodes_6.csv' as a
create (:Location {name:a.Location})""")
print("created nodes")

graph.run("""UNWIND range(0,5) as inner
LOAD CSV WITH HEADERS FROM 'file:///""" + fl + """/pincodes_'+ toString(inner)+ '.csv' AS x
match(a:Location),(b:Location)
where a.name=x.Location and b.name=x.Location1
merge (a)-[dist:Distance{distance:toInt(x.Distance)}]->(b);""")
print("created relationships")


#--------------------------------------------------------------------------------------------------------
#Disease data insertion

df = pd.read_csv(fl+"/Disease_Details.csv")
dfl = df[['Disease', 'Diagnosis_treatment']]
dfl = dfl.drop_duplicates()
dfl.sort_values(['Disease'],ascending=True)
records_ = dfl.to_dict(orient = 'records')

results = db.Disease.insert_many(records_)

df2 = pd.DataFrame(list(results.inserted_ids))
df2.columns= ['Object_id']
df = df.join(df2)

for index, row in df.iterrows():
    #print(row['Disease'], row['Object_id'])
    a = Node("Disease", name=row['Disease'], id=str(row['Object_id']))
    graph.merge(a,"Disease","name")

df_symptoms = pd.read_csv(fl+"/Disease_Symptoms.csv")
df_symptoms = df_symptoms[['Disease','Symptoms']]
df_symptoms = df_symptoms.drop_duplicates()
df_symptoms = df_symptoms.dropna()

df_symptoms = df_symptoms.groupby('Disease')['Symptoms'].apply(list).reset_index(name='Symptoms_arr')

for index, row in df_symptoms.iterrows():
    query = {'Disease':{'$eq':row['Disease']}}
    update = {'$set':{'Symptoms.Name':row['Symptoms_arr']}}
    results_symptoms = db.Disease.update_one(query,update, upsert=True)
    print(f"Symptoms data inserted into MongoDB {results_symptoms}")
    for i in range(len(row['Symptoms_arr'])):
        graph.run('''MERGE (a:Disease {name: $d1})
        MERGE (b:Symptom {name: $d2})
        MERGE (b)-[:CAUSES]->(a)''',parameters={'d1': row['Disease'],'d2': row['Symptoms_arr'][i]})
        print(f"{row['Disease']} and {row['Symptoms_arr'][i]} relationship has been created in neo4j ")

df_specialty = pd.read_csv(fl+"/Disease_Specialization.csv")
df_specialty = df_specialty[['Disease','Specialization']]
df_specialty = df_specialty.drop_duplicates()
df_specialty = df_specialty.dropna()
df_specialty = df_specialty.groupby('Disease')['Specialization'].apply(list).reset_index(name='Specialty_arr')

for index, row in df_specialty.iterrows():
    query = {'Disease':{'$eq':row['Disease']}}
    update = {'$set':{'Specialization.Name':row['Specialty_arr']}}
    results_specialty = db.Disease.update_one(query,update, upsert=True)
    print(f"Specialization data inserted into MongoDB {results_specialty}")
    for i in range(len(row['Specialty_arr'])):
        graph.run('''MERGE (a:Disease {name: $d1})
        MERGE (b:Specialization {name: $d2})
        MERGE (a)-[:TREATS_UNDER]->(b)''',parameters={'d1': str(row['Disease']),'d2': row['Specialty_arr'][i]})
        print(f"{row['Disease']} and {row['Specialty_arr'][i]} relationship has been created in neo4j ")




#--------------------------------------------------------------------------------------------------------
#Hospital,Doctor,User Comments data insertion

df = pd.read_csv(fl + "/Hospital_Information_System.csv", header=0)
df = df.drop_duplicates()
client = MongoClient()
hospital_records = df.to_dict(orient='records')
db.Hospital.insert_many(hospital_records)
print("inserted in Mongodb")


df= pd.read_csv(fl + "/Doctor_Information_System.csv", header=0)
df = df.drop_duplicates()
client = MongoClient()
doctor_records = df.to_dict(orient='records')
db.Doctor.insert_many(doctor_records)
print("inserted in Mongodb")


export = db.Hospital.find()
dfl = pd.DataFrame(list(export))
dfl = dfl[['_id', 'Hospital_Name','Location','Hospital_Timings']]
dfl = dfl.drop_duplicates()
dfl.to_csv(fl + "/Hospital_Information_System_exported.csv")
print("exported from Mongodb")

export = db.Doctor.find()
dfl = pd.DataFrame(list(export))
dfl = dfl[['_id', 'Doctor_Name','Location','Doctor_Specialization','Hospital_Name']]
dfl = dfl.drop_duplicates()
dfl.to_csv(fl + "/Doctor_Information_System_exported.csv")
print("exported from Mongodb")


df = pd.read_csv(fl + "/Specialization_Information_System.csv", header=0)
df = df.drop_duplicates()
client = MongoClient()
specialization_records = df.to_dict(orient='records')
db.Specialization.insert_many(specialization_records)
print("inserted in Mongodb")

export = db.Specialization.find()
dfl = pd.DataFrame(list(export))
dfl = dfl[['_id', 'specialization']]
dfl = dfl.drop_duplicates()
dfl.to_csv(fl + "/Specialization_Information_System_exported.csv")
print("exported from Mongodb")


graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Doctor_Information_System_exported.csv' AS line
CREATE (:Doctors { Doctor_Name: line.Doctor_Name, Doctor_ID: line._id})""")
print("Inserted in Neo4j")


graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Hospital_Information_System_exported.csv' AS line
CREATE (:Hospitals { Hospital_Name: line.Hospital_Name, Hospital_ID: line._id})""")
print("Inserted in Neo4j")

graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Doctor_Information_System_exported.csv' AS line
match(a:Doctors),(b:Hospitals)
where a.Doctor_Name=line.Doctor_Name and b.Hospital_Name=line.Hospital_Name
create (a)-[:Practices_At]->(b)""")
print("created relationships")

graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Specialization_Information_System_exported.csv' AS line with line
where line.specialization is not null
MERGE (:Specialization { Doctor_Specialization: line.specialization})""")
print("Inserted in Neo4j")


graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Doctor_Information_System_exported.csv' AS line
match(a:Doctors),(b:Specialization)
where a.Doctor_Name=line.Doctor_Name and b.Doctor_Specialization=line.Doctor_Specialization
create (a)-[:Specialist_In]->(b)""")
print("created relationships")


df = pd.read_csv(fl + "/UserComments_Information_System.csv", header=0)
df = df.drop_duplicates()
client = MongoClient()
usercomments_records = df.to_dict(orient='records')
db.UserComments.insert_many(usercomments_records)
print("inserted in Mongodb")

graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Hospital_Location.csv' AS line
match(a:Hospitals),(b:Location)
where a.Hospital_Name=line.Hospital_Name and b.name=line.Hospital_Location
create (a)-[:Hospital_Location]->(b)""")
print("created relationships")

graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Doctor_Information_System_exported.csv' AS line
match(a:Doctors),(b:Location)
where a.Doctor_Name=line.Doctor_Name and b.name=line.Location
create (a)-[:Doctor_Location]->(b)""")
print("created relationships")


#--------------------------------------------------------------------------------------------------------
#Drug data insertion



#### Mongo Insert ####
df = pd.read_csv(fl + "/Drug_Information_System.csv", header=0)
df = df.drop('Disease_Name', axis=1)
df = df.drop_duplicates()

df= df.where(pd.notnull(df), None)

client = MongoClient()
drug_records = df.to_dict(orient='records')
db.Drugs.insert_many(drug_records)
print("inserted Drugs into Mongodb")


### Mongo export for Neo4j ###
export = db.Drugs.find()
dfl = pd.DataFrame(list(export))
dfl = dfl[['_id', 'Drug_Name']]
dfl = dfl.drop_duplicates()
dfl.to_csv(fl + "/Drug_Information_System_exported.csv")


#### Insert into Neo4j ####
graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Drug_Information_System_exported.csv' AS line
CREATE (:Drug { Drug_Name: line.Drug_Name, Drug_ID: line._id})""")
print("Inserted Drugs into Neo4j")

### Creating Relationships ###
graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Drug_Information_System.csv' AS line
match(a:Drug),(b:Disease)
where a.Drug_Name=line.Drug_Name and b.name=line.Disease_Name
create (a)-[:Medicine_For]->(b)""")
print("created relationships between Drugs and Diseases")


#--------------------------------------------------------------------------------------------------------
#Insurance data insertion

df = pd.read_csv(fl+"/insurance_corrected.csv", header=0)
df['Policy_Id'] = df.PolicyName.map(hash)
records = []
for (CompanyName), policies in df.groupby(["CompanyName"]):
    contents_df = policies.drop(["CompanyName"], axis=1)
    subset = [OrderedDict(row) for i,row in contents_df.iterrows()]
    records.append(OrderedDict([("CompanyName", CompanyName),
                                ("Policies", subset)]))
result = db.Insurance.insert_many( records )
print("inserted")


#Logic for Premium File
file_name=fl + "/PremiumRange.xlsx"
df = pd.read_excel(file_name)

def f(row):
    if row['Premium'] > 1000 and row['Premium'] < 50000 :
        val = "1000-50000"
    elif row['Premium'] > 50000 and row['Premium'] < 100000:
        val = "50000-100000"
    elif row['Premium'] > 100000 and row['Premium'] < 150000:
        val = "100000-150000"
    else :
        val = "150000-200000"
    return val

df['SumInsured'] = df.apply(f, axis=1)
df.to_csv(fl + "/PremiumRange.csv")



#### Insert into Neo4j ####

graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/CName.csv' AS CName
CREATE (:CompanyName { CompanyName: CName.CompanyName, Company_ID: CName._id})""")
print("Inserted Comp Details in Neo4j")

graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/PName.csv' AS PName
CREATE (:PolicyName { PolicyName: PName.PolicyName, Policy_ID: PName.Policy_Id})""")
print("Inserted Policy Details in Neo4j")

graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Premium.csv' AS Premium
CREATE (:PremiumRanges { name:Premium.Premium, PremiumRange: Premium.Premium})""")
print("Inserted Premium Details in Neo4j")



### Creating Relationships ###
graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/RelationCompandPolicy.csv' AS CompandPol
match(a:CompanyName),(b:PolicyName)
where a.CompanyName=CompandPol.CompanyName and b.PolicyName=CompandPol.PolicyName
create (a)-[:Has_Policy]->(b)""")
print("created relationships between comp and policy")


graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/PremiumRange.csv' AS PremiumRange
match(a:PremiumRanges),(b:PolicyName)
    where  PremiumRange.SumInsured = a.PremiumRange AND b.PolicyName=PremiumRange.PolicyName
    MERGE (b)-[r:PremiumRange_Of]->(a)""")
print("created relationships between policy and premiumrange")

graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/Policy_Disease.csv' AS PD
match(a:PolicyName),(b:Disease)
    where  PD.PolicyName = a.PolicyName AND PD.DiseasesCovered=toUpper(b.name)
    MERGE (a)-[r:Diseases_Covered]->(b)""")
print("created relationships between policy and disease")


graph.run("""LOAD CSV with headers FROM 'file:///""" + fl + """/PolicyHosp.csv' AS PolicyHosp
match(a:PolicyName),(b:Hospitals)
    where  PolicyHosp.Plans = a.PolicyName AND PolicyHosp.CashlessHospitals=b.Hospital_Name
    MERGE (a)-[r:Hospital_Covered]->(b)""")
print("created relationships between policy and hospitals")

#Insertion Script
#Redis Insertion
r = redis.Redis(db=0)
#Generating  two files from search history file
file1 = open(fl + "/Redis_Search_Hist_commands.csv","w",newline='')
field_names=['Key','Value']
writer = csv.DictWriter(file1, fieldnames=field_names)
writer.writeheader()
with open(fl + "/Redis_Search_Hist.csv", encoding='utf-8',newline='') as csvfile:
    reader= csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        key1 = row['Location']+ ":"+ row['Date']+ ":" + row['Time'] +":SEARCH"
        value1 = row["Topic"]
        writer.writerow({'Key': key1, 'Value': value1})

file1.close()


file2 = open(fl + "/Redis_Search_Hist_commands2.csv","w",newline='')
writer2 = csv.DictWriter(file2, fieldnames=field_names)
writer2.writeheader()

with open(fl + "/Redis_Search_Hist.csv", encoding='utf-8',newline='') as csvfile:
    reader= csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        key2 = row['Location']+ ":"+ row['Date']+ ":" + row['Time'] + ":USER"
        value2 = row['\ufeffUser']
        writer2.writerow({'Key': key2, 'Value': value2})
        # print(string_command)

file2.close()

#inserting search history into redis
pipeline1 = r.pipeline()
pipeline2 = r.pipeline()
with open(fl + "/Redis_Search_Hist_commands.csv",newline='') as csvfile:
    reader= csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        # print(row['Key'])
        pipeline1.lpush(row['Key'], row['Value'])

pipeline1.execute()

with open(fl + "/Redis_Search_Hist_commands2.csv",newline='') as csvfile:
    reader= csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        # print(row['Key'])
        pipeline2.sadd(row['Key'], row['Value'])

pipeline2.execute()
print("Done")

#---------------------------------------------------------------------------------------------------
#Historical Disease Insertion
df = pd.read_excel(fl+"/Disease_measles.xlsx")

df = df.drop(columns = ['Total', 'incidence','lab.conf'])
print(df.head())
for index, row in df.iterrows():
    country = {}
    for col in df.columns:
        if col == 'CountryName':
            country = row[col].upper()
            print(country)
        else:
            param = "DISEASE:H:"+country+":"+col
            key = "MEASLES"
            value = row[col]
            r.hset(param, key, value)
            print(f"Data {row[col]} has been inserted into redis with {param} and {key}")

df = pd.read_excel(fl+"/Disease_rubella.xlsx")

df = df.drop(columns = ['Total', 'incidence','lab.conf'])
print(df.head())
for index, row in df.iterrows():
    country = {}
    for col in df.columns:
        if col == 'CountryName':
            country = row[col].upper()
            print(country)
        else:
            param = "DISEASE:H:"+country+":"+col
            key = "RUBELLA"
            value = row[col]
            r.hset(param, key, value)
            print(f"Data {row[col]} has been inserted into redis with {param} and {key}")


#----------------------------------------------------------------------------------------------------
#Anagram Data Insertion

letterpoints = { "E":(1),
                 "A":(2),
                 "R":(3),
                 "I":(4),
                 "O":(5),
                 "T":(6),
                 "N":(7),
                 "S":(8),
                 "L":(9),
                 "C":(10),
                 "U":(11),
                 "D":(12),
                 "P":(13),
                 "M":(14),
                 "H":(15),
                 "G":(16),
                 "B":(17),
                 "F":(18),
                 "Y":(19),
                 "W":(20),
                 "K":(21),
                 "V":(22),
                 "X":(23),
                 "Z":(24),
                 "J":(25),
                 "Q":(26)
}

result1 = graph.run("match(n:PolicyName) return n.PolicyName").data()
result2 = graph.run("match(n:Hospitals) return n.Hospital_Name").data()
result3 = graph.run("match(n:CompanyName) return n.CompanyName").data()
result4 = graph.run("match(n:Disease) return n.name").data()
result5 = graph.run("match(n:Drug) return n.Drug_Name").data()
result6 = graph.run("match(n:Doctors) return n.Doctor_Name").data()
result7 = graph.run("match(n:Symptom) return n.name").data()


PolicyNames = (x['n.PolicyName'] for x in result1)
HospitalNames = (x['n.Hospital_Name'] for x in result2)
CompanyNames = (x['n.CompanyName'] for x in result3)
Diseases = (x['n.name'] for x in result4)
Drug_Names = (x['n.Drug_Name'] for x in result5)
Doctor_Names = (x['n.Doctor_Name'] for x in result6)
Symptom = (x['n.name'] for x in result7)


def insertintoredis(list,var):

    for y in list:
        score = 0
        z = y.split('(')[0]
    #
        z = z.split('-')[0]
        z = z.split('–')[0]
        z = ''.join(e for e in z if e.isalnum())
        z = ''.join([i for i in z if not i.isdigit()])

        for j in z:
            j = j.upper()
            try:
                score = score + letterpoints[j]
            except KeyError:
                score = score + 0

        key = "ANAGRAM:"+str(score)
        value = "{}:".format(var) + y.encode().decode('utf-8')

        print(key,value)

        r.sadd(key,value)


insertintoredis(PolicyNames,"PolicyName")
insertintoredis(HospitalNames,"Hospital")
insertintoredis(CompanyNames,"Company")
insertintoredis(Diseases,"disease")
insertintoredis(Drug_Names,"Drugs")
insertintoredis(Doctor_Names,"Doctor")
insertintoredis(Symptom,"Symptom")

print("Inserted Data into Redis")