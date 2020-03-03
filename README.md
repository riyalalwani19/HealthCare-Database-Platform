# HealthCare-Database-Platform
Database application combining information from different data sources of the healthcare sector like drugs, diseases, insurance companies, hospitals, doctors, user comments, symptoms and relationships between them. It stores all the data in three different databases i.e. Mongo DB, Neo4j and Redis. It contains solutions to the popular use cases in Health care sector by querying the respective databases and combining them using python as language and PyCharm as IDE. Some of the use cases are also solved using R language. 


## Getting Started
### Download the entire content on your machine and create the separate folders as available in Git.
- Get all the files from files folder in one folder, some files are in zip format. Unzip it and keep in one folder with all other files.
- Run the code from Insertion code in Python IDE, that will help to insert all the data in your machine. For that, you must first provide the location where you have downloaded all the files.
- Run the merged all data code which contains all the user stories except R. But, Firstly, Provide Neo Graph password for it.
- Run all the user stories by R in R studio. But, Firstly, Provide Neo Graph password for it.
- Separate User Stories folder contains all the User Stories and their description.

### Prerequisites
- Need to install Mongo DB server, Redis server and Neo4j Graph database, PyCharm IDE(any Python IDE), R studio.
- For some packages in python like matplotlib python was required to be of version 3.7 or less. So, In IDE add Python 3.7 or less as project interpreter.
- Before running any code
    1) create a Graph in Neo4J and enter password to it, which will be further asked by code if required. Install Plugin called Graph       Algorithms.
       Change configuration of neo4j to import file from any local location and not just import location.   
        a. Remove ***dbms.directories.import=import*** ( Comment line 25)  
        b. Add ***dbms.security.allow_csv_import_from_file_urls=true*** ( Uncomment line 693)

    2) Databases:- 

        a. MongoDB server should be up and running.  
        b. Neo4J server should be up and running.  
        c. Neo4J Graph should already be created.  
        d. Redis server should be up and running.  
        e. All the data should be inserted using Insertion code.  
    
### Download all the packages required for entire project mentioned in the below list:-

#### For insertion of data:-
•	import pandas as pd
•	import json
•	from py2neo import Graph, Node, Relationship
•	from collections import OrderedDict
•	from pymongo import MongoClient
•	import xlrd
•	import redis
•	import csv

#### For Merged User Stories:-
•	from random_username.generate import generate_username
•	import re
•	from bson.objectid import ObjectId
•	from tabulate import tabulate
•	import numpy as np
•	from matplotlib import pyplot, axes
•	from py2neo import Graph
•	from collections import Counter
•	from itertools import repeat, chain
•	import redis
•	from datetime import datetime, timedelta
•	import warnings
•	import matplotlib.pyplot as plt
•	import pandas as pd
•	import statsmodels.api as sm
•	import matplotlib
•	import nltk.corpus 
•	nltk.download("stopwords")
•	from nltk import stopwords
•	from textblob import TextBlob
•	from pymongo import MongoClient
•	from datetime import datetime

#### For R based User Stories:-  
•	RNeo4j
•	Httr
•	ggplot2

  ## Authors
  - Riya Lalwani
  - Varun John
  - Sangireddy Siva 
  - Abhinav Parashar
  - Prashant sonar
 
