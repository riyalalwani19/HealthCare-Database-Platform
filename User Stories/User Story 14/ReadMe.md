# Title - User Story 14

## Synopsis - 
This file will help a user to run user story 14 in his enviornment.

## User Story - 
Rachel is a frequent user of Healthcare Database platform, but she rarely remembers names of drugs and diseases correctly. As a user she wants the platform to suggest her names from the system if she enters misspelled names and tell her whether the misspelled name can be a drug, disease etc.

## Prerequisites - 
Following are the database and code related prequisites that need to be fullfilled before running the script.

#### 1. Database - 	
		a. Redis server should be up and running.
		b. Data should have been inserted in all databases.

#### 2. Code - 	
		a. Install python packages (redis,pandas)
		b.Change redis db number as per your setting (line 4)
		

## Inputs - 
		The python program asks users for following input -
		a. Word thats need to be searched - "Enter your word"

## Default Output:
Word Entered: "Activ hEALTH eNHECAN"
