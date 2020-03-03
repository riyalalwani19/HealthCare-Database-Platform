############################ Query 3 ############################

install.packages("RNeo4j")
library(RNeo4j)

graph = startGraph("http://localhost:7474/db/data/", 
                   username="neo4j", password="graph_data")
con$ping()



## Shortest Path Algo for all nodes ##

query10 = "CALL algo.allShortestPaths.stream('distance',{nodeQuery:'Location',defaultValue:1.0})
YIELD sourceNodeId, targetNodeId, distance
WITH sourceNodeId, targetNodeId, distance
WHERE algo.isFinite(distance) = true
MATCH (source:Location) WHERE id(source) = sourceNodeId
MATCH (target:Location) WHERE id(target) = targetNodeId
WITH source, target, distance WHERE source <> target
RETURN source.name AS source, target.name AS target, distance
ORDER BY distance DESC"

e <- cypher(graph,query10)
colnames(e)[2] <- "a.name"

## Policy Name, Hospital Name and Location ##
query4 = "match (u:PolicyName)-[:Hospital_Covered]->(b:Hospitals)-[:Hospital_Location]->(a:Location)
return u.PolicyName, b.Hospital_Name,a.name"

d3 <- cypher(graph,query4)

## Merging and Cleaning ##
d3 <- merge(e,d3,"a.name")
d3 <- unique(d3)

## Output ##
func2 <- function(){
loc <- readline(prompt="Enter Location:")
if(tolower(loc) %in% tolower(d3$source)){
  loc <- loc
} else {
  stop("Not a Valid Location")

}
d3 <- d3[which(tolower(d3$source) == tolower(loc)),]

Ins_pol <- readline(prompt="Enter Insurance Policy:")
ifelse(tolower(Ins_pol) %in% tolower(d3$u.PolicyName),Ins_pol,stop("Not a Valid Policy Name"))
d3 <- d3[which(tolower(d3$u.PolicyName) == tolower(Ins_pol)),]

dist <- readline(prompt="Enter max Distance:")
ifelse(dist >= min(as.integer(d3$distance)),dist,dist <- readline(prompt="Enter Valid Distance:"))
d3 <- d3[which(d3$distance <= as.integer(dist)),]

rownames(d3) <- NULL
print(d3[,c(2,1,3,4)])

}

func2()
