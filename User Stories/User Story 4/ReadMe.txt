Title - User Story 4

Synopsis - This file will help a user to run user story 4 in his enviornment.

User Story - As MAX a traveller travelling to Mumbai, I want to know the top 10 disease which are common in Mumbai during a particular month and also I want to know one drug for each disease that has least side effects.

Prerequisites - Following are the database and code related prequisites that need to be fullfilled before running the script.

1. Database - 	a. MongoDB server should be up and running.
		b. Neo4J server should be up and running.
		c. Redis server should be up and running.
		d. Neo4J Graph should already be created.
		e. Data should have been inserted in all databases.

2. Code - 	a. Install python packages (redis, pymongo, py2neo, pandas, collections, itertools)
		b. Change graph password(line 21) to password of the graph created in your enviornment.

Inputs - The python program asks users for following input -
		a. Month number - "Enter month number" - (Enter 03 for March or 11 for November)

Default input - "03"