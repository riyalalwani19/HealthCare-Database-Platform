## For insertion of data


###Prerequisites -   
Following are the database and code related prequisites that need to be fullfilled before running the script.  

1. Database -  
a. MongoDB server should be up and running.  
b. Neo4J server should be up and running.  
c. Neo4J Graph should already be created.  
d. Redis server should be up and running.  
e. change configuration of neo4j to import file from any local location and not just import location.   
				  1. Remove ***dbms.directories.import=import***  
				  2. Add ***dbms.security.allow_csv_import_from_file_urls=true***  


2. Code:-  
Download below packages
- import pandas as pd
- import json
- from py2neo import Graph, Node, Relationship
- from collections import OrderedDict
- from pymongo import MongoClient
- import xlrd
- import redis
- import csv

Inputs - 
The python program asks users for following input -  
a. Location of the downloaded files  
b. Password for Neo4j graph.  


