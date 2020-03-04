# Title - User Story 2

## Synopsis - This file will help a user to run user story 2 in his environment.

## User Story -  
Alex is an insurance agent and he wants to know the two insurance policies which have the highest and lowest Premium in the Premium range of 1000-50000rs, which come comes under Aditya Birla (Insurance company) and provides cover for Anal cancer to suggest to his client.

## Prerequisites - Following are the database and code related prequisites that need to be fullfilled before running the script.

#### 1. Database - 	a. MongoDB server should be up and running.
		b. Neo4J server should be up and running.
		c. Neo4J Graph should already be created.
		d. Data should have been inserted in all databases.

#### 2. Code - 	a. Install python packages (pandas, pymongo, py2neo,tabulate)
		b. Change graph password(line 6) to password of the graph created in your environment.

## Inputs - The python program asks users for following input -  
		a. Premium Range -   "Enter range from options available" -   (Options Available:"1000-50000","50000-100000","100000-150000",
																	"150000-200000")



## Default input:   
Premium Range :1000-50000,  
Covered Disease:Anal Cancer,  
Company Name:Aditya Birla  
