Title - User Story 1

Synopsis - This document is the guide to run User Story 1 in their environment

User Story - After consulting a doctor Suresh came to know that Hay Fever is the reason for his cough, sneezing and  fatigue sensation. He wants to have a second opinion before going for the medication, but he doesn’t want to spend any money in consultations

Prerequisites - Following are the database and code related prequisites that need to be fullfilled before running the script.

1. Database - 	a. Neo4J server should be up and running
		b. MongoDB server should be up and running
		c. Redis server should be up and running.
		b. Data should have been inserted in Neo4J and Mongo databases.

2. Code - 	a. Install python packages (py2neo, pymongo, json, redis, datetime, time, random_username, pandas, re)


Inputs - The python program asks users for following input -
		a. User will be asked for the Neo4j graph password - "Please enter password for the Neo4j Graph"
		b. Symptoms - "Enter the symptoms with space" (Enter the Symptoms e.g. cough sneezing)
		c. User will be notified with the available diseases for the input symptoms
		d. More about disease - "You want to know more about Diseases and their treatments (y/n)" (Enter y if you wish to know more about diseases and their treatment o.w enter n to exit)
		e. Disease name - if above input is y then asks for "Please enter Disease you want to know from above list, enter all if you want to know about all Diseases:" (Enter disease name from the list of diseases for the input symptoms, if you wish to know about all disease, then just type 'all')
