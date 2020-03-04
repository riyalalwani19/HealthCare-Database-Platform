# Title - User Story 8

## Synopsis - This file will help a user to run user story 8 in his enviornment.

## User Story -   
Local pharmacists of a town are looking to stock their shop up with drugs according to each season. They want to know the monthly trends of drugs and occurrences of diseases to help them store better.

## Prerequisites -   
Following are the database and code related prequisites that need to be fullfilled before running the script.

#### 1. Database -   	
		a. MongoDB server should be up and running.  
		b. Neo4J server should be up and running.  
		c. Redis server should be up and running.  
		d. Neo4J Graph should already be created.  
		e. Data should have been inserted in all databases.  

#### 2. Code -  
		a. Install python (python 3.7 for matplotlib.pyplot) packages (matplotlib.pyplot,redis, pymongo, py2neo,collections, itertools)  
		b. Change graph password(line 22) to password of the graph created in your enviornment.  
		c.Change redis db number as per your setting (line 25)  
		d.Change connection for Mongodb Collection (line 63)  

#### Inputs - 
		The python program asks users for following input -  
		a. Season Number -   "Enter Season Number"-  
		("1" - Rainy, "2" - Summer, "3" - Winter, "4"-Spring)  

##### *Disclaimer*: If Incorrect Season Number is entered default output will be for Spring

#### Default Output:  
Season Number: "1"  
