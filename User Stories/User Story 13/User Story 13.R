############################ Query 13 ############################
install.packages("RNeo4j")
library(RNeo4j)

graph = startGraph("http://localhost:7474/db/data/", 
                   username="neo4j", password="graph_data")
con$ping()

# Data upload from REDIS #
df_13a <- read.csv("~/Downloads/Redis_D.csv", stringsAsFactors=TRUE)
colnames(df_13a)[3] <- "c.name"

# Running User Story #
query13 = "match (c:Disease)-[r:TREATS_UNDER]->(a:Specializations)<-[:Specialist_In]-(b:Doctors)-[:Practices_At]->(u:Hospitals)-[:Hospital_Location]->(d:Location)
return d.name,c.name,count(u.Hospital_Name)"
df_13b <- cypher(graph,query13)

# Merging and Grouping #
colnames(df_13a)[2] <- "d.name"
dff <-merge(x=df_13b,y=df_13a,by=c("d.name","c.name"))
dff$X <- NULL

colnames(dff)[2] <- "c.name"
colnames(dff)[1] <- "Location"
colnames(dff)[3] <- "Hospitals"

ggplot(dff, 
       aes(x=dff$c.name, y=dff$Location, label = Hospitals))  + geom_label() + ggtitle("Diseases with Locations") + labs(x = "Disease Name", y="Location Name") + theme(plot.title = element_text(size=30, face="bold", margin = margin(10, 0, 10, 0)),axis.text.x=element_text(angle=90, size=8, vjust=0.5))


