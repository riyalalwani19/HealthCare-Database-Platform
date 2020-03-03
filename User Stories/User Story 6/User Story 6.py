from pymongo import MongoClient
import matplotlib.pyplot as plt
client = MongoClient()

list1= []
disease_list = []
speciality_list = []
disease_spc_list = []

pipeline1 = [{"$group": {"_id" : {"Specialization":"$Doctor_Specialization"}}},
{"$project": {"Specialization" : {"$toLower": "$_id.Specialization"},"_id":0}}]


result1 = client.Information_System.Doctor.aggregate(pipeline1)
for x in result1:
    list1.append(x['Specialization'])

pipeline2 = [{"$match": {"Specialization" : {"$ne":None}}},{"$unwind": "$Specialization"},{"$unwind": "$Specialization.Name"},{"$project": {"_id":0,
"Disease":1,"Speciality":{"$toLower": "$Specialization.Name"}}},{"$match": {"Speciality" : {"$in" : list1}}}]


result2 = client.Information_System.disease.aggregate(pipeline2)

for y in result2:
    disease_list.append(y['Disease'])
    speciality_list.append(y['Speciality'])

pipeline3 = [{"$unwind": "$Specialization"},{"$unwind": "$Specialization.Name"},
            {"$project" : {"_id":0,"Speciality":"$Specialization.Name"}},{"$group" : {"_id":"$Speciality"}}]
result3 = client.Information_System.disease.aggregate(pipeline3)

for z in result3:
    disease_spc_list.append(z['_id'])

total = client.Information_System.disease.find().count()
remainder = total - len(list(set(disease_list)))

values1 = [len(list(set(disease_list))),remainder]
Labels1 = ['No. Of Diseases with Doctors','Disease with no Doctors']
values2 = [len(list(set(speciality_list))),len(list(set(disease_spc_list))) - len(list(set(speciality_list)))]
Labels2 = ['No. of Speciality with Doc','No. of Speciality without Doc']
explode = [0.05,0]
plt.figure(figsize=(10,5))

plt.subplot2grid((1,2),(0,0))
plt.pie(values1, labels=Labels1, autopct="%.1f%%",explode=explode)
plt.title("Disease to Doctor Share",fontweight = "bold")

plt.subplot2grid((1,2),(0,1))
plt.pie(values2, labels=Labels2, autopct="%.1f%%",explode=explode)
plt.title("Speciality of Diseases Covered",fontweight = "bold")
plt.show()
