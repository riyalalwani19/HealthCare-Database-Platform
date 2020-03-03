# For Running the scripts

### Prerequisites -
Following are the database and code related prequisites that need to be fullfilled before running the script.  
1.	Database -  
  a. MongoDB server should be up and running.  
  b. Neo4J server should be up and running.  
  c. Neo4J Graph should already be created.  
  d. Redis server should be up and running.  
  e. change configuration of neo4j to import file from any local location and not just import location.  
    1. Remove dbms.directories.import=import  
    2. Add dbms.security.allow_csv_import_from_file_urls=true  
    
2.	Code:-  
  Download below packages  
  For Merged User Stories:-  
  • from random_username.generate import generate_username • import re • from bson.objectid import ObjectId • from tabulate import         tabulate • import numpy as np • from matplotlib import pyplot, axes • from py2neo import Graph • from collections import Counter •       from itertools import repeat, chain • import redis • from datetime import datetime, timedelta • import warnings • import                 matplotlib.pyplot as plt • import pandas as pd • import statsmodels.api as sm • import matplotlib • import nltk.corpus •                 nltk.download("stopwords") • from nltk import stopwords • from textblob import TextBlob • from pymongo import MongoClient • from         datetime import datetime
  For R based User Stories:-  
  • RNeo4j • Httr • ggplot2  

3. Inputs -   
The python program asks users for following input -   
a. Password for Neo4j graph.  
b. Enter User Story Number which you want to run
