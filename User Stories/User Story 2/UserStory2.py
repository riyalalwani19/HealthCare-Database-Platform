import pandas as pd
from py2neo import Graph
from pymongo import MongoClient
from tabulate import tabulate

#Connectiong with Neo Graph

#Neo4J password
print("Please enter password for the Neo4j Graph")
Neo4JPwd = input()
graph = Graph(password=Neo4JPwd)

#initializations and Validations
input1_PremiumRange =str(input ("Please enter the premium range you want from following options:\n"
       "1000-50000 \n" 
       "50000-100000 \n"
       "100000-150000 \n"
       "150000-200000 \n"))

if input1_PremiumRange != "1000-50000" and input1_PremiumRange != "50000-100000" and  input1_PremiumRange != "100000-150000" and input1_PremiumRange != "150000-200000":
    print("Entered Premium Range is not from mentioned list.Please try again by entering the range from options given")
    exit()
if input1_PremiumRange == []:
    print("Entered Premium Range is not valid.Please try again by entering the range from options given")
    exit()

input3_CoverFor = str(input("Please enter the disease you require in coverage:")).lower()

if input3_CoverFor == []:
    print("Entered Covered disease is not valid.Please try again")
    exit()


input2_CompanyName = str(input("Please enter the company name of  the insurance:")).lower()

if input2_CompanyName == []:
    print("Entered Company Name is not valid.Please try again")
    exit()

#NEO4J Query for retreiving Policy Names based on above matching criteria

results = graph.run("""MATCH (a:CompanyName)-[r:Has_Policy]->(b:PolicyName)
WHERE toLower(a.CompanyName) = $CName
WITH {PolicyName:b.PolicyName} AS Policies
MATCH (t:PolicyName)- [r:PremiumRange_Of]->(u:PremiumRanges)
WITH {PolicyName:t.PolicyName} AS PoliciesRange
WHERE Policies.PolicyName = t.PolicyName AND u.PremiumRange = \"""" + \
                input1_PremiumRange + """\"
MATCH (a:PolicyName)-[r:Diseases_Covered]->(b:Disease)
WHERE PoliciesRange.PolicyName = a.PolicyName AND toLower(b.name) = \"""" + \
                input3_CoverFor + """\"
return PoliciesRange.PolicyName AS PolicyNames""", parameters={'CName' : input2_CompanyName}).data()

if results != []:
    Policy_Name = [record['PolicyNames'] for record in results]
#Mongodb Query to retrieve Min and Max Policies
    conn = MongoClient()
    db = conn.Information_Systems
    collection = db.Insurance

    Pol_PremiumDetails = collection.aggregate([

    {"$match": {"CompanyName":{"$ne":None}}},
    {"$unwind": "$Policies"},
    {"$match": {"Policies.PolicyName": {"$in": Policy_Name}}},
    {"$project" : {"_id":0,"CompanyName":{"$toLower":"$CompanyName"},"PolicyName":"$Policies.PolicyName","Premium":"$Policies.Premium"}},
    {"$match": {"CompanyName":input2_CompanyName}},
    { "$out" : "Policy_Premium"}
    ])

    query =  db.Policy_Premium.aggregate(
    [
        {
        "$group":
            {
            "_id": "$CompanyName",
            "minPremium": { "$min": "$Premium" },
            "maxPremium": { "$max": "$Premium" }
        }
    }

    ])

    df = pd.DataFrame(query)
    for index, row in df.iterrows():
        minPremium = row['minPremium']
        maxPremium = row['maxPremium']

# print(df)
    Minimum_Policy = db.Policy_Premium.find({"Premium" :minPremium},{"PolicyName":1,"_id":0})
    Maximum_Policy = db.Policy_Premium.find({"Premium" :maxPremium},{"PolicyName":1,"_id":0})

    Minimum_Policy1 = [record['PolicyName'] for record in Minimum_Policy]
    Maximum_Policy1= [record['PolicyName'] for record in Maximum_Policy]
    Minimum_Premium_PolicyName=[]
    for x in Minimum_Policy1:
        Minimum_Premium_PolicyName.append(x)
    Maximum_Premium_PolicyName = []
    for x in Maximum_Policy1:
        Maximum_Premium_PolicyName.append(x)
    df['Minimum_PolicyName'] = Minimum_Premium_PolicyName
    df['Maximum_PolicyName'] = Maximum_Premium_PolicyName

#Final Output
    print(tabulate(df, headers='keys', tablefmt='psql'))
else:
    print("There is no Policy for this combination")