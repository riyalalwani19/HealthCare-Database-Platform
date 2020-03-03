Title - User Story 9

Synopsis - This file will help a user to run user story 9 in his enviornment.

User Story - As a Drug Company's marketing head I want to know trend in popularity of drug oy company in camprison with drug of my competitors.

Prerequisites - Following are the database and code related prequisites that need to be fullfilled before running the script.

1. Database - 	b. Neo4J server should be up and running.
				c. Redis server should be up and running.
				d. Neo4J Graph should already be created.
				e. Data should have been inserted in all databases.

2. Code - 	a. Install python packages (redis, sys, py2neo, pandas, matplotlib)
			b. Change graph password(line 11) to password of the graph created in your enviornment.

Inputs - The python program asks users for following input -
		a. Drug name  - "Enter Drug Name" - (Enter any drug name of the company like - Bextra, Supartz)

Default input - "Supartz"
