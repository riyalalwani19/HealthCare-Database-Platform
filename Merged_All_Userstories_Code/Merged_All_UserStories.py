from random_username.generate import generate_username
import re
from bson.objectid import ObjectId
from tabulate import tabulate
import numpy as np
from matplotlib import pyplot, axes
from py2neo import Graph
from collections import Counter
from itertools import repeat, chain
import redis
from datetime import datetime, timedelta
import warnings
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import matplotlib
from nltk.corpus import stopwords
from textblob import TextBlob
from pymongo import MongoClient
from datetime import datetime

# Warnings
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')
warnings.filterwarnings("ignore", category=DeprecationWarning)

#Neo4J password
print("Please enter password for the Neo4j Graph")
Neo4JPwd = input()

if Neo4JPwd == '':
    print("Please enter password and try again")
    exit()

#Mongodb Database name
Dbname = "Information_System"

#Mongodb Database no
redisdb= 0



def UserStory1(Neo4JPwd, Dbname, redisdb):
    graph = Graph(password=Neo4JPwd)
    print("Enter the symptoms with space")
    inp = [str(i).lower() for i in input().split()]
    if inp == []:
        print("Entered input is not valid.Please try again by entering symptoms with space")
        return

    results = graph.run('''with $in as symptoms
    match (s:Symptom)
    Where toLower(s.name) in symptoms
    with collect(s) as symptoms
    match (d:Disease)
    where all(s in symptoms Where (s)-[:CAUSES]->(d))
    return DISTINCT d.name as Disease, d.id as Disease_id''', parameters={'in': inp}).data()

    now = datetime.now()
    current_time = now.strftime("%d-%m-%Y:%H:%M:%S")
    username = ''.join(map(str, generate_username(1)))

    r = redis.Redis(db=redisdb)

    client = MongoClient()
    db = client[Dbname]
    collection = db.Disease
    if results == []:
        print(
            f"Tring.. Tring..... Tring............  database does not have any disease associated with mentioned symptoms {inp}")
        print("--------------------------------------------------------------------------------")
        for i in range(len(inp)):
            key = 'NODISEASE' + ':' + current_time + ':' + username.upper()
            r.lpush(key, inp[i].upper())
            print(f"Search data {inp[i].upper()} inserted into Redis with key {key} for further validation")
        print("--------------------------------------------------------------------------------")
        return
    record_ids = [record['Disease'].lower() for record in results]
    record_ids2 = [ObjectId(record['Disease_id']) for record in results]
    print(f"{inp} symptoms causes disease(s) {record_ids}")
    print("--------------------------------------------------------------------------------")
    for i in range(len(inp)):
        key = 'SYMPTOMS' + ':' + current_time + ':' + username.upper()
        r.lpush(key, inp[i].upper())
        print(f"Search data {inp[i].upper()} inserted into Redis with key {key}")
    print("--------------------------------------------------------------------------------")
    inp1 = input("You want to know more about Diseases and their treatments (y/n):").lower()
    if inp1 != 'y':
        return
    print("Please enter Disease you want to know from above list, enter all if you want to know about all Diseases:")
    disease = input().lower()
    print(disease)
    if disease != 'all' and disease in record_ids:
        query = collection.find({'Disease': re.compile(disease, re.IGNORECASE)})
        df = pd.DataFrame(query)
        for index, row in df.iterrows():
            print("--------------------------------------------------------------------------------")
            print(f"{inp} causes '{row['Disease']}'")
            print(f"please find some treatements for '{row['Disease']}''")
            print(row['Diagnosis_treatment'])
            if 'Specialization' in row:
                print(
                    f"This '{row['Disease']}' can be treated by doctors having specialization of {row['Specialization']['Name']}")
            key = 'DISEASE' + ':' + current_time + ':' + username.upper()
            r.lpush(key, row['Disease'].upper())
            print("--------------------------------------------------------------------------------")
            print(f"Search data {row['Disease'].upper()} inserted into Redis with key {key}")
    else:
        if disease == 'all':
            print(record_ids2)
            query = collection.find({'_id': {'$in': record_ids2}})
            df = pd.DataFrame(query)
            print(df)
            for index, row in df.iterrows():
                print("---------------------------------------------------------------------------------------------")
                print(f"{inp} causes '{row['Disease']}'")
                print(f"please find some treatements for '{row['Disease']}''")
                print(row['Diagnosis_treatment'])
                if 'Specialization' in row:
                    if not pd.isna(row['Specialization']):
                        print(
                            f"This '{row['Disease']}' can be treated by doctors with specialization of {row['Specialization']['Name']}")
                key = 'DISEASE' + ':' + current_time + ':' + username.upper()
                r.lpush(key, row['Disease'].upper())
                print("--------------------------------------------------------------------------------")
                print(f"Search data {row['Disease'].upper()} inserted into Redis with key {key}")
                print("--------------------------------------------------------------------------------")
        else:
            print(f"Entered {disease} does not exist in our database. Thank you for choosing healthcare engine")


def UserStory2(Neo4JPwd, Dbname):
    graph = Graph(password=Neo4JPwd)

    # initializations and Validations
    input1_PremiumRange = str(input("Please enter the premium range you want from following options:\n"
                                    "1000-50000 \n"
                                    "50000-100000 \n"
                                    "100000-150000 \n"
                                    "150000-200000 \n"))

    if input1_PremiumRange != "1000-50000" and input1_PremiumRange != "50000-100000" and input1_PremiumRange != "100000-150000" and input1_PremiumRange != "150000-200000":
        print(
            "Entered Premium Range is not from mentioned list.Please try again by entering the range from options given")
        return
    if input1_PremiumRange == []:
        print("Entered Premium Range is not valid.Please try again by entering the range from options given")
        return

    input3_CoverFor = str(input("Please enter the disease you require in coverage:")).lower()

    if input3_CoverFor == []:
        print("Entered Covered disease is not valid.Please try again")
        return

    input2_CompanyName = str(input("Please enter the company name of  the insurance:")).lower()

    if input2_CompanyName == []:
        print("Entered Company Name is not valid.Please try again")
        return

    # NEO4J Query for retreiving Policy Names based on above matching criteria

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
    return PoliciesRange.PolicyName AS PolicyNames""", parameters={'CName': input2_CompanyName}).data()

    if results != []:
        Policy_Name = [record['PolicyNames'] for record in results]
        # Mongodb Query to retrieve Min and Max Policies
        client = MongoClient()
        db = client[Dbname]
        collection = db.Insurance

        Pol_PremiumDetails = collection.aggregate([

            {"$match": {"CompanyName": {"$ne": None}}},
            {"$unwind": "$Policies"},
            {"$match": {"Policies.PolicyName": {"$in": Policy_Name}}},
            {"$project": {"_id": 0, "CompanyName": {"$toLower": "$CompanyName"}, "PolicyName": "$Policies.PolicyName",
                          "Premium": "$Policies.Premium"}},
            {"$match": {"CompanyName": input2_CompanyName}},
            {"$out": "Policy_Premium"}
        ])

        query = db.Policy_Premium.aggregate(
            [
                {
                    "$group":
                        {
                            "_id": "$CompanyName",
                            "minPremium": {"$min": "$Premium"},
                            "maxPremium": {"$max": "$Premium"}
                        }
                }

            ])

        df = pd.DataFrame(query)
        for index, row in df.iterrows():
            minPremium = row['minPremium']
            maxPremium = row['maxPremium']

        # print(df)
        Minimum_Policy = db.Policy_Premium.find({"Premium": minPremium}, {"PolicyName": 1, "_id": 0})
        Maximum_Policy = db.Policy_Premium.find({"Premium": maxPremium}, {"PolicyName": 1, "_id": 0})

        Minimum_Policy1 = [record['PolicyName'] for record in Minimum_Policy]
        Maximum_Policy1 = [record['PolicyName'] for record in Maximum_Policy]
        Minimum_Premium_PolicyName = []
        for x in Minimum_Policy1:
            Minimum_Premium_PolicyName.append(x)
        Maximum_Premium_PolicyName = []
        for x in Maximum_Policy1:
            Maximum_Premium_PolicyName.append(x)
        df['Minimum_PolicyName'] = Minimum_Premium_PolicyName
        df['Maximum_PolicyName'] = Maximum_Premium_PolicyName

        # Final Output
        print(tabulate(df, headers='keys', tablefmt='psql'))
    else:
        print("There is no Policy for this combination in our database.")


def UserStory4(Neo4JPwd, Dbname, redisdb):
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

    graph = Graph(password=Neo4JPwd)
    r = redis.Redis(db=redisdb)
    pipeline = r.pipeline()

    ### Redis Search - for all seacrhed topics####
    val = input("Please enter Month(in 2 digit format) of your choice: ")

    if len(val) != 2:
        print("You didn't enter a 2 digit month code hence terminating program")
        return

    if int(val) <= 0 or int(val) > 12:
        print("You didnt enter a valid month digit hence terminating program")
        return

    print("Please wait for few seconds...")
    pattern = "*-" + val + "-*SEARCH"
    x = r.keys(pattern=pattern)
    for y in x:
        pipeline.lrange(y, 0, 100)

    result = pipeline.execute()

    for y in result:
        result2.append(y[0].decode('utf-8'))

    result2 = list(chain.from_iterable(repeat(i, c) for i, c in Counter(result2).most_common()))
    result3 = list(dict.fromkeys(result2))

    ### Mongo Search - for filter out diseases from search topics####
    client = MongoClient()
    db = client[Dbname]
    for temp in result3:
        x = db.Disease.find({"Disease": temp}, {"Disease": 1, "_id": 0})
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
            pipeline = [{"$match": {"Drug_Name": drug}}, {"$project": {"Drug_Name": 1, "_id": 0, "Side_Effects": {
                "$switch": {"branches": [{"case": {"$eq": ["$Side_Effects", None]}, "then": "Blank"}],
                            "default": "$Side_Effects"}}}}]
            result4 = db.Drugs.aggregate(pipeline)
            for irr3 in result4:
                irr3['Disease'] = disease5
                disease_drug3.append(irr3)

    ### Grouping and filtering for final result ###
    for curr in disease_drug3:
        temp_se = {}
        side_effects = curr.get('Side_Effects')
        if side_effects == 'Blank':
            count_se = 0
        else:

            if "following:" in side_effects:
                side_effects2 = side_effects.split("following:")
                count_se = side_effects2[1].count('\n') - 1
            else:
                count_se = 1

        temp_se['Disease'] = curr.get('Disease')
        temp_se['Drug'] = curr.get('Drug_Name')
        temp_se['No_Of_SE'] = count_se
        disease_drug4.append(temp_se)

    df_se = pd.DataFrame(disease_drug4)

    df_se_2 = df_se.groupby(['Disease']).agg({'No_Of_SE': ['min']}).reset_index()
    df_se_2.columns = df_se_2.columns.droplevel(1)
    df_se_3 = []
    df_se_4 = pd.DataFrame([], columns=list(['Disease', 'Drug', 'No_Of_SE']))

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
    pd.set_option('display.max_colwidth', -1)
    result_df = result_df.drop_duplicates()
    final = result_df.groupby('Disease').agg({'Drug': ['min']}).reset_index()
    final.columns = final.columns.droplevel(1)

    for kor in disease_drug3:
        disease_final.append(kor['Disease'])

    seen = set()
    seen_add = seen.add
    gog = [x for x in disease_final if not (x in seen or seen_add(x))]
    gog2 = gog[:10]

    final2 = final[final['Disease'].isin(gog2)]

    print(final2.to_string(index=False, justify='left'))


def UserStory5(Dbname):
    client = MongoClient()
    db = client[Dbname]
    result = db.UserComments.distinct("Doctor_Name")

    lim = input("Please enter the number of recent comments you want to search rating from: ")
    if lim.isdigit() == False:
        print("You didn't enter a valid number for number of recent comments input")
        return
    rat = input(
        f"Please enter what should be the average doctor rating based on recent {lim} comments(enter a number between 1 and 10): ")
    if rat.isdigit() == False:
        print("You didn't enter a valid number for lowest limit of rating")
        return

    if 10 < int(rat) or int(rat) < 0:
        print("You didn't enter a valid number for lowest limit of rating")
        return

    for x in result:
        pipeline = [{"$match": {"Doctor_Name": x}}, {"$sort": {
            "Posted_On": -1}}, {"$limit": int(lim)},
                    {"$group": {"_id": "$Doctor_Name", "avg_rating": {"$avg": "$Comment_Rating"}}},
                    {"$project": {
                        "Doctor": "$_id", "Avg_Rating": "$avg_rating", "_id": 0}}]
        result2 = db.UserComments.aggregate(pipeline)
        for y in result2:
            if y['Avg_Rating'] >= int(rat):
                result3 = db.Doctor.find({"Doctor_Name": y['Doctor']},
                                                                {"_id": 0, "Doctor_Rating": 0})
                for z in result3:
                    z['Doctor_Rating'] = y['Avg_Rating']
                    df = pd.DataFrame.from_dict(z, orient='index')
                    print(df)

def UserStory6(Dbname):
    client = MongoClient()
    db = client[Dbname]
    list1 = []
    disease_list = []
    speciality_list = []
    disease_spc_list = []

    pipeline1 = [{"$group": {"_id": {"Specialization": "$Doctor_Specialization"}}},
                 {"$project": {"Specialization": {"$toLower": "$_id.Specialization"}, "_id": 0}}]

    result1 = db.Doctor.aggregate(pipeline1)
    for x in result1:
        list1.append(x['Specialization'])

    pipeline2 = [{"$match": {"Specialization": {"$ne": None}}}, {"$unwind": "$Specialization"}, {"$unwind": "$Specialization.Name"},
                 {"$project": {"_id": 0,
                               "Disease": 1, "Speciality": {"$toLower": "$Specialization.Name"}}},
                 {"$match": {"Speciality": {"$in": list1}}}]

    result2 = db.Disease.aggregate(pipeline2)

    for y in result2:
        disease_list.append(y['Disease'])
        speciality_list.append(y['Speciality'])

    pipeline3 = [{"$unwind": "$Specialization"}, {"$unwind": "$Specialization.Name"},
                 {"$project": {"_id": 0, "Speciality": "$Specialization.Name"}}, {"$group": {"_id": "$Speciality"}}]
    result3 = db.Disease.aggregate(pipeline3)

    for z in result3:
        disease_spc_list.append(z['_id'])

    total = db.Disease.find().count()
    remainder = total - len(list(set(disease_list)))

    values1 = [len(list(set(disease_list))), remainder]
    Labels1 = ['No. Of Diseases with Doctors', 'Disease with no Doctors']
    values2 = [len(list(set(speciality_list))), len(list(set(disease_spc_list))) - len(list(set(speciality_list)))]
    Labels2 = ['No. of Speciality with Doc', 'No. of Speciality without Doc']
    explode = [0.05, 0]
    plt.figure(figsize=(10, 5))

    plt.subplot2grid((1, 2), (0, 0))
    plt.pie(values1, labels=Labels1, autopct="%.1f%%", explode=explode)
    plt.title("Disease to Doctor Share", fontweight="bold")

    plt.subplot2grid((1, 2), (0, 1))
    plt.pie(values2, labels=Labels2, autopct="%.1f%%", explode=explode)
    plt.title("Speciality of Diseases Covered", fontweight="bold")
    plt.show()


def UserStory8(Neo4JPwd, Dbname, redisdb):
    ## Intializations ###
    result = []
    result2 = []
    result3 = []
    drug = []
    disease = []
    disease_drug = []
    disease_drug2 = []
    Drugsofdiseaseslist = []
    Sortedlistelements = []
    Top5Drugs = []

    # Neo Graph
    graph = Graph(password=Neo4JPwd)

    # Redis connection
    r = redis.Redis(db=redisdb)
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
        result2.append(y[0].decode('utf-8'))  ###decoding the elements(removing eccoding)

    # sorted(result2, key=result2.count, reverse=True)
    result2 = list(chain.from_iterable(
        repeat(i, c) for i, c in Counter(result2).most_common()))  ###sorting the elemts on basis of count
    result3 = list(dict.fromkeys(result2))  ###removing duplicates

    ### Mongo Search - for filter out drugs from search topics####
    client = MongoClient()
    db = client[Dbname]

    drug = [y['Drug_Name'] for temp in result3 for y in db.Drugs.find({"Drug_Name": temp}, {"Drug_Name": 1, "_id": 0})]

    ## Mongo Search - for filter out diseases from search topics####
    disease = [y['Disease'] for temp in result3 for y in db.Disease.find({"Disease": temp}, {"Disease": 1, "_id": 0})]

    ### Neo Search - to find drug of the diseases####

    disease_drug = [graph.run("""match(n:Disease)<-[:Medicine_For]-(b) where n.name=\"""" + \
                              temp2 + """\" return b.Drug_Name as Drug""").data() for temp2 in disease]

    disease_drug2 = list2 = [x for x in disease_drug if x != []]  ###remove null elements list

    for irr1 in disease_drug2:
        for irr2 in irr1:
            drugs = irr2.get('Drug')
            Drugsofdiseaseslist.append(drugs)

    def Sort_Tuple(tup):
        return (sorted(tup, key=lambda x: x[1], reverse=True))

    counts = Counter(drug)
    counts.update(Drugsofdiseaseslist)
    Sortedlistelements = Sort_Tuple(counts.items())
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

def UserStory9(Neo4JPwd, redisdb):
    graph = Graph(password=Neo4JPwd)
    drug_in = input("Please enter your Drug Name: ")
    result3 = graph.run(
        "match (a:Drug)-[:Medicine_For]->()<-[:Medicine_For]-(b:Drug) where a.Drug_Name='" + drug_in + "' return b.Drug_Name").data()

    if not result3:
        print("Drug Name entered didn't match any drug names in the database. Hence ending script.")
        return

    print("This will take around 30 seconds...")

    plt.style.use("ggplot")

    r = redis.Redis(db=redisdb)
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

    for var, car in zip(result, pip):
        temp = {}
        temp['Key'] = var['Key']
        temp['Value'] = car[0].decode("utf-8")
        result2.append(temp)

    df1 = pd.DataFrame(result2)
    df1['Key'] = pd.to_datetime(df1['Key'], format='%m-%Y')

    for z in result3:
        disease_list.append(z['b.Drug_Name'])

    disease_list = list(set(disease_list))

    print("Competitor Drugs: -")
    flag = 0
    for dl in disease_list:
        flag = flag + 1
        print(flag, ".", dl)

    comp_in = input("Please enter name of Competitor Drug you wanna see trend with - ")

    if comp_in not in disease_list:
        print("Entered Competitor Drug wasn't from the list. Hence ending program.")
        return

    trend_list.append(drug_in)
    trend_list.append(comp_in)

    df2 = df1[df1['Value'].isin(trend_list)]
    df3 = df2.groupby(['Key', 'Value']).size().reset_index(name='counts')

    final = pd.pivot_table(df3, index=['Key'], columns=['Value'], fill_value=0)
    final.columns = final.columns.droplevel(0)
    final.sort_values(by=['Key'])

    final.plot(figsize=(20, 10)).legend(title='Drugs')
    plt.show()


def UserStory10(redisdb):
    r = redis.Redis(db=redisdb, decode_responses=True)
    dates = []
    keys = []
    values = []
    locations = []
    frequency = []
    print("This will take around 30 seconds...")
    for key in r.scan_iter("*08-12-2019*:USER"):
        if key.split(":")[2] != 'USER':
            pattern = ":(.*?):USER"
            key_date = datetime.strptime(re.search(pattern, key).group(1), "%d-%m-%Y:%H:%M:%S")
            dates.append(key_date)
            frequency.append(int(1))
            keys.append(key)
            return_value = r.smembers(key)
            value = [str(data) for data in return_value]
            values.append(value)
            locations.append(key.split(':')[0])

    if keys == []:
        print("Keys does not exist in redis for the given pattern. please change the pattern and try again")
        return

    df = pd.DataFrame(zip(keys, dates, values, locations), columns=('keys', 'dates', 'values', 'locations'))

    rows = []
    _ = df.apply(lambda row: [rows.append([row['keys'], row['dates'], nn, row['locations']]) for nn in row['values']],
                 axis=1)

    df_new = pd.DataFrame(rows, columns=df.columns).set_index('dates')

    df_date = df_new.groupby([pd.Grouper(freq='1H')], axis=1)['values'].apply(list).reset_index(name='users')
    df_date['dates'] = df_date['dates'].dt.time

    df_date = df_date.groupby('dates')['users'].apply(list).reset_index(name='users')
    df_date = df_date.set_index('dates')

    values_f = []
    values_c = []
    dates_f = []
    i = 0
    max_lim = 8

    while i < len(df_date) and max_lim <= len(df_date):
        if i < max_lim:
            data = df_date['users'][i:max_lim][0:8].explode()
            values_f.append([q for q in data])
            date = str(df_date.index[i]) + '-' + str(df_date.index[max_lim - 1]).replace('00:00', '59:59')
            dates_f.append(date)
        i = i + 1
        max_lim = max_lim + 1

    df_f = pd.DataFrame(zip(dates_f, values_f), columns=('time', 'users'))

    vals = df_f['users'].values.tolist()
    rs = [len(r) for r in vals]
    a = np.repeat(df_f['time'], rs)

    df = pd.DataFrame(np.column_stack((a, np.concatenate(vals))), columns=df_f.columns)

    rows = []
    _ = df.apply(lambda row: [rows.append([row['time'], nn]) for nn in row['users']], axis=1)

    df_fc = pd.DataFrame(rows, columns=df_f.columns)
    df_fc = df_fc.groupby('time')['users'].nunique().reset_index(name='count').nlargest(5, 'count')

    print(df_fc)

    df_date = df_new.groupby([pd.Grouper(freq='8H')])['values'].apply(list).reset_index(name='users')
    df_date['dates'] = df_date['dates'].dt.time
    rows = []
    _ = df_date.apply(lambda row: [rows.append([row['dates'], nn]) for nn in row['users']], axis=1)
    df_8h = pd.DataFrame(rows, columns=df_date.columns)
    df_8h = df_8h.groupby('dates')['users'].nunique().reset_index(name='count')
    df_8h['time'] = ['00:00:00-07:59:59', '08:00:00-15:59:59', '16:00:00-23:59:59']

    fig, axes = pyplot.subplots(nrows=1, ncols=2)

    ax = df_fc.plot(kind='bar', x='time', y='count', color='Turquoise', ax=axes[0])
    axes[0].set_xlabel('Best 8 hours bucket (continuous next)')
    axes[0].set_ylabel('Number of unique users')
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
    fig.autofmt_xdate()

    ax = df_8h.plot(kind='bar', x='time', y='count', color='Gold', ax=axes[1])
    axes[1].set_xlabel('Best 8 hours bucket')
    axes[1].set_ylabel('Number of unique users')
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
    fig.autofmt_xdate()

    df_loc = df_new.groupby(['locations'])['values'].nunique().sort_values(ascending=False).reset_index(
        name='count').nlargest(10, 'count')

    df_datloc = df_new.groupby([pd.Grouper(freq='1H'), 'locations'])['values'].nunique().reset_index(name='count')
    df_datloc['dates'] = df_datloc['dates'].dt.time
    ax = df_datloc.groupby(['dates', 'locations']).mean().unstack().plot(kind='line', stacked=True)
    pyplot.xlabel('Hourly trend')
    pyplot.ylabel('Locations')
    pyplot.legend(df_datloc['locations'].unique())
    pyplot.xticks(rotation=0)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))

    print(df_loc.head())

    ax = df_loc.plot(kind='bar', x='locations', y='count')
    pyplot.xlabel('Locations')
    pyplot.ylabel('Number of unique users')
    pyplot.xticks(rotation=0)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))

    pyplot.show()


def UserStory11(redisdb):
    r = redis.Redis(db=redisdb, decode_responses=True)

    diseases = []
    print("Please wait for few seconds ...")
    for key in r.scan_iter("DISEASE:H:*"):
        return_value = r.hkeys(key)
        for i in range(len(return_value)):
            if return_value[i] not in diseases:
                diseases.append(return_value[i])

    print(f"We have historical data for the diseases {diseases} \nPlease enter the Disease to forecast")
    inp = input()

    if inp == '' or inp.upper() not in diseases:
        print(f"We do not have {inp} disease history in out database. Please try again.")
        return

    matplotlib.rcParams['axes.labelsize'] = 14
    matplotlib.rcParams['xtick.labelsize'] = 12
    matplotlib.rcParams['ytick.labelsize'] = 12
    matplotlib.rcParams['text.color'] = 'k'

    dates = []
    keys = []
    values = []
    country = []

    for key in r.scan_iter("DISEASE:H:*"):
        return_keys = r.hkeys(key)
        for i in range(len(return_keys)):
            if return_keys[i] == inp.upper():
                hash_date = datetime.strptime(key.split(':')[3], "%Y-%m").date()
                country.append(key.split(':')[2])
                dates.append(hash_date)
                keys.append(return_keys[i])
                return_values = r.hget(key, return_keys[i])
                values.append(return_values)

    if dates == [] or values == []:
        print("Sorry right now we are facing issue with retreiving values from Redis. Please contact responsible.")
        return

    df = pd.DataFrame(zip(dates, values), columns=('dates', 'values'))

    df['values'] = df['values'].astype(float)

    max_date = df['dates'].max()

    print(f"We have historical data for Disease {inp.upper()} until {max_date}")
    print("Please enter the number of weeks to forecast e.g. 10")
    inp_fc = input()

    try:
        float(inp_fc)
    except ValueError:
        print(f"{inp_fc} is not a number. Please try again by giving number")
        return

    if float(inp_fc) > 100:
        print(f"Input {inp_fc} weeks has crossed maximum limit. Please try again by giving number within 100")
        return

    forecast_date = max_date + timedelta(weeks=float(inp_fc))

    df = df.sort_values('dates')
    df = df.groupby('dates')['values'].sum().reset_index()
    df = df.set_index('dates')
    df.index = pd.to_datetime(df.index)

    y = df['values'].resample('MS').mean()

    mod = sm.tsa.statespace.SARIMAX(y,
                                    order=(1, 1, 1),
                                    seasonal_order=(0, 1, 1, 12),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

    results = mod.fit()

    pred_uc = results.get_prediction(start=max_date, end=forecast_date, dynamic=False)
    pred_ci = pred_uc.conf_int()
    ax = y.plot(label='observed', figsize=(14, 6))
    pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.25)
    ax.set_xlabel('Years')
    ax.set_ylabel(f'Disease "{inp.upper()}" registered cases')
    plt.legend()
    plt.show()


def UserStory12(Neo4JPwd):
    # asthma,arthritis
    val = input("Enter Diseases with comma between them :")
    val2 = []
    temp = val.split(",")
    drug = []
    disease = []

    for x in temp:
        x = x.lower()
        val2.append(x)
    val3 = set(val2)

    graph = Graph(password=Neo4JPwd)

    for rorr in val2:
        query3 = "match (a:Disease) where toLower(a.name)='" + rorr + "' return a.name as Disease"
        result = graph.run(query3).data()
        if not result:
            print(rorr, "named disease doesnt exist in our database. Please enter a name that exists in our database.")
            return

    query = """with """ + str(val2) + """ as diseases match (a:Disease) where
    toLower(a.name) in diseases with collect(a) as disease_node match (x:Drug) where All
    (a in disease_node where (a)<-[:Medicine_For]-(x)) return DISTINCT x.Drug_Name as Drug_Name"""

    neo_result = graph.run(query).data()
    for x in neo_result:
        drug.append(x['Drug_Name'])

    neo_result2 = graph.run(
        "match (a:Drug)-[:Medicine_For]-(b)  where a.Drug_Name in " + str(drug) + " return b.name as Disease").data()

    for y in neo_result2:
        disease.append(y['Disease'])

    disease = set(disease)

    disease2 = [x.lower() for x in disease]

    if val3.issubset(disease2):
        for x in neo_result:
            print("Drug_Name:", end=" ")
            print(x['Drug_Name'])
            drug.append(x['Drug_Name'])

    else:
        print("No drug exist for this combination of diseases")


def UserStory14(redisdb):
    r = redis.Redis(db=redisdb)
    letterpoints = {"E": (1),
                    "A": (2),
                    "R": (3),
                    "I": (4),
                    "O": (5),
                    "T": (6),
                    "N": (7),
                    "S": (8),
                    "L": (9),
                    "C": (10),
                    "U": (11),
                    "D": (12),
                    "P": (13),
                    "M": (14),
                    "H": (15),
                    "G": (16),
                    "B": (17),
                    "F": (18),
                    "Y": (19),
                    "W": (20),
                    "K": (21),
                    "V": (22),
                    "X": (23),
                    "Z": (24),
                    "J": (25),
                    "Q": (26)
                    }
    new = []
    word = input("Enter your word:")
    if word != []:
        z = word.split('(')[0]
        z = word.split('-')[0]
        z = word.split('–')[0]
        z = ''.join(e for e in z if e.isalnum())
        z = ''.join([i for i in z if not i.isdigit()])
        WordCount = str(len(z))
        org = z
        score = 0
        for j in z:
            j = j.upper()
            try:
                score = score + letterpoints[j]
            except KeyError:
                score = score + 0

        set = r.smembers("ANAGRAM:{}".format(score))

        listing = []
        for x in set:
            listing.append(x.decode("utf-8"))

        keys, values = zip(*(s.split(":") for s in listing))
        df = pd.DataFrame()
        df['Description'] = keys
        df['value'] = values
        # print(df)
        key = []
        for x in df['value']:
            z = x.split('(')[0]
            z = z.split('-')[0]
            z = z.split('–')[0]
            z = ''.join(e for e in z if e.isalnum())
            z = ''.join([i for i in z if not i.isdigit()])

            if WordCount == str(len(z)):
                key.append(x + ":" + str(len(z)) + ":" + z)
                new_doc = {}
                new_doc['original'] = x
                new_doc['not_original'] = z.lower()
                new_doc['match'] = x + ":" + str(len(z)) + ":" + z
                new.append(new_doc)

        org = ''.join(sorted(org.lower()))
        result = []
        for kill in new:
            jugs = ''.join(sorted(kill['not_original']))
            if jugs == org:
                result.append(kill)

        # print(result)
        # Activ Health Enhance

        key = [sub['match'] for sub in result]
        # print(str(key))
        Redisreturnedlist = []
        for x in key:
            Redisreturnedlist.append(x.split(":"))

        flat_list = [item for sublist in Redisreturnedlist for item in sublist]

        requiredvalues = []
        requiredvalues = flat_list[::3]

        # print(requiredvalues)

        # Function to convert
        def listToString(s):
            # initialize an empty string
            str1 = ""

            # traverse in the string
            for ele in s:
                str1 += ele

            # return string
            return str1

        listtostringval = (listToString(requiredvalues))

        if (requiredvalues == [] and listtostringval == ""):
            print("Entered word not available in our database")
            return
        else:
            if (len(requiredvalues) > 1):
                print("Correct options available based on your search")
                print(df[df.value.isin(requiredvalues)].to_string(index=False))
            else:
                print("Correct options available based on your search")
                print(df[df.value == listtostringval].to_string(index=False))

    else:
        print("Please enter non blank value ")


def UserStory15(Neo4JPwd, Dbname):
    client = MongoClient()
    db = client[Dbname]
    rating = 0
    new_rating = 0
    Doctor_name = input("Please enter Doctors Full Name who you wanna comment on: ")
    exp = Doctor_name.title()

    first = db.Doctor.count_documents({"Doctor_Name": {"$regex": exp}})

    if first == 0:
        print("Doctor with this name does not exist in our database. Hence ending program.")
        return
    User = input("Please enter your user name: ")
    comment_user = input("Please enter your comment: ")

    insert_dict = {}

    ## replacing special characters ##
    comment = re.sub('[!.,@#$%^*()~;:/<>\|+_\-[\]\?]', '', comment_user)

    ### replacing stop words ###
    stop = stopwords.words('english')
    for words in stop:
        comment = comment.replace(" " + words + " ", " ")

    ## determining polarity of the comment##
    result = TextBlob(comment).sentiment

    polarity_score = result[0]

    ## determining rating based on the polarity##
    if polarity_score > 0.7:
        rating = 10
    elif 0.7 >= polarity_score > 0.5:
        rating = 9
    elif 0.5 >= polarity_score > 0.30:
        rating = 8
    elif 0.30 >= polarity_score > 0.20:
        rating = 7
    elif 0.20 >= polarity_score > 0:
        rating = 6
    elif 0 >= polarity_score > -0.20:
        rating = 5
    elif -0.20 >= polarity_score > -0.30:
        rating = 4
    elif -0.30 >= polarity_score > -0.5:
        rating = 3
    elif -0.5 >= polarity_score > -0.7:
        rating = 2
    else:
        rating = 1

    ## Inserting into Mongo ##
    insert_dict['Doctor_Name'] = Doctor_name
    insert_dict['Comment'] = comment_user
    insert_dict['User_Name'] = User
    insert_dict['Posted_On'] = datetime.today().isoformat()
    insert_dict['Comment_Rating'] = rating

    db.UserComments.insert_one(insert_dict)
    print("Inserted in Mongo")

    result2 = db.Doctor.find({"Doctor_Name": {"$regex": exp}})

    for var in result2:
        new_rating = (float(rating) + float(var['Doctor_Rating'])) / 2.0
        db.Doctor.update_one({"Doctor_Name": Doctor_name}, {"$set": {"Doctor_Rating": new_rating}})
        print("Doctor Commented on:", var['Doctor_Name'])
        print("User Commented By:", User)
        print("Comment: ", comment_user)
        print("Posted On:", insert_dict['Posted_On'])
        print("Comment Rating:", rating)
        print("Old Doctor Rating:", var['Doctor_Rating'])
        print("New Doctor Rating:", new_rating)

# Main program
loop = 1
while (loop == 1):
    print("\n")
    print("Welcome to Healthcare Engine")
    print("Please enter the User Story Number to display the output")
    print()
    print("User Story 1")
    print("User Story 2")
    print("User Story 4")
    print("User Story 5")
    print("User Story 6")
    print("User Story 8")
    print("User Story 9")
    print("User Story 10")
    print("User Story 11")
    print("User Story 12")
    print("User Story 14")
    print("User Story 15")
    print("Enter 16 to Exit")
    choice = input("Choose your option: ")
    if choice != []:
        if choice == "1" or choice == "01":
            UserStory1(Neo4JPwd, Dbname, redisdb)
        elif choice == "2" or choice == "02":
            UserStory2(Neo4JPwd, Dbname)
        elif choice == "4" or choice == "04":
            UserStory4(Neo4JPwd, Dbname, redisdb)
        elif choice == "5"or choice == "05":
            UserStory5(Dbname)
        elif choice == "6"or choice == "06":
            UserStory6(Dbname)
        elif choice == "8" or choice == "08":
            UserStory8(Neo4JPwd, Dbname, redisdb)
        elif choice == "9" or choice == "09":
            UserStory9(Neo4JPwd, redisdb)
        elif choice == "10":
            UserStory10(redisdb)
        elif choice == "11":
            UserStory11(redisdb)
        elif choice == "12":
            UserStory12(Neo4JPwd)
        elif choice == "14":
            UserStory14(redisdb)
        elif choice == "15":
            UserStory15(Neo4JPwd, Dbname)
        elif choice == "16":
            print("Happy to help. Visit again :-)")
            loop = 0
        else:
            print("Please enter a valid value from menu. ")
    else:
        print("Please enter Non blank value ")
