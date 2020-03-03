# HealthCare-Database-Platform
Database application combining information from different data sources of the healthcare sector like drugs, diseases, insurance companies, hospitals, doctors, user comments, symptoms and relationships between them. It stores all of the data in three different database i.e. MongoDb, Neo4j and Redis. It contains solutions to the popular use cases in Health care sector by querying the resprective databases and combinining them using python as language and Pycharm as IDE. Some of the use cases are also solved using R langauge. 


## Getting Started
### Download the entire content on your machine and create the seperate folders as available in Git.
- Get all the files from files folder in one folder,some files are in zip format. Unzip it and keep in one folder with all other files.
- Run the code from Insertion code in Python IDE, that will help to insert all the data in your machine. For that, you have to first provide the location where you have downloaded all the files.
- Run the merged all data code which contains all the user stories except R. But, Firstly, Provide Neo Graph password for it.
- Run all the user stories by R in R studio. But, Firstly, Provide Neo Graph password for it.
- Seperate User Stories folder contains all the User Stories and thier description.

Prerequisites
- Need to install MongoDb server, Redis server and Neo4j Graph database, PyCharm IDE(any Python IDE), R studio.
- For some packages in python like matplotlib python was required to be of version 3.7 or less. So, In IDE add Python 3.7 or less as porject interpreter.
- Download all the packages required for entire project mentioned in the below list:-

#### For insertion of data:-
  import pandas as pd
  import json
  from py2neo import Graph, Node, Relationship
  from collections import OrderedDict
  from pymongo import MongoClient
  import xlrd
  import redis
  import csv
  
 #### for Merged User Stories
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
  import nltk.corpus 
  nltk.download("stopwords")
  from nltk import stopwords
  from textblob import TextBlob
  from pymongo import MongoClient
  from datetime import datetime
  
  

