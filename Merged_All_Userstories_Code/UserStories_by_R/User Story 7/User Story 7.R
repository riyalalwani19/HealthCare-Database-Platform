############################ Query 7 ############################
install.packages("RNeo4j")
library(RNeo4j)
library(ggpubr)

if(!require(devtools)) install.packages("devtools")
devtools::install_github("kassambara/ggpubr")

graph = startGraph("http://localhost:7474/db/data/", 
                   username="neo4j", password="graph_data")
con$ping()

# Data from Neo4J for combined #
query3 = "match (u:CompanyName)-[:Has_Policy]->(b:PolicyName)-[:Diseases_Covered]->(a:Disease)
return a.name, u.CompanyName, count(*) as line
order by line DESC"

d <- cypher(graph,query3)
colnames(d)[3] <- "Diseases"

jpeg("rplot.jpg", width = 350, height = "350")
ggplot(d, 
       aes(x=d$a.name, y=d$u.CompanyName, 
           color = Diseases)) + geom_point() + ggtitle("Insurace Company Vs Disease Covered") + labs(x = "Disease Name", y="Company Name") + theme(plot.title = element_text(size=20, face="bold", 
       
                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                                                                   margin = margin(10, 0, 10, 0)),axis.text.x=element_text(angle=90, size=8, vjust=0.5))
## All Diseases ##
query1 = "match (a:Disease) return a.name as a"
a <- cypher(graph,query1)
colnames(a)[1] <- "a.name"

df<-merge(x=d,y=a,by="a.name",all=TRUE)
df[is.na(df)] <- 0
colnames(df)[3] <- "Diseases"

jpeg("rplot.jpg", width = 1500, height = 2000)
ggplot(df, 
       aes(x=df$a.name, y=df$u.CompanyName, 
           color = Diseases)) + geom_point() + ggtitle("Insurace Company Vs Disease Covered") + labs(x = "Disease Name", y="Company Name") + theme(plot.title = element_text(size=20, face="bold", margin = margin(10, 0, 10, 0)),axis.text.x=element_text(angle=90, size=8, vjust=0.5))

readJPEG(source = "rplot.jpg")


func1 <- function(){
Graph <- readline(prompt="Enter which Graph (Combined_Diseases/All_Diseases: ")


ifelse(Graph == "All_Diseases", ggplot_add(test1),ifelse(Graph == "Combined_Diseases",ggplot_add(test2), "Enter Valid Input"))
}


func1()
