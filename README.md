# Neo4j Sample Project
##Set up Neo4j Enterprise (Docker / VM). 
```
docker run \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/s3cr3t\
    -v $PWD/data:/data -v $PWD/plugins:/plugins \
    --name neo4j-apoc \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_import_file_use__neo4j__config=true \
    -e NEO4JLABS_PLUGINS=\[\"apoc\"\] \
    neo4j
```


## Key Use Cases 
Link to the graph:  
https://arrows.app/#/local/id=CGvPhHgNFdKpruz0pgS1
![img.png](img.png)


There are four activities can be identified given the supplied dataset, that is Person node can have 
any of the following four activity nodes:
- Work
- Education
- Trip
- Transaction

In this exercise, I created four nodes for different activities, an alternative way, given the small
amount of data, could be creating an activity node, with a type property set as work, education etc.


To reduce the amount of duplicated data, I further introduced the country and year nodes, as these data are 
presented in all tables. 
Based on the assumed graph, I intend to answer the following use cases:

Fact questions: 
- Has an individual worked/educated/traveled/shopped ? 
- If any activity happened, what is the location?
- Given a particular year, what a person has done? 
- How many times a person has shopped? 

Inference question: 
- Does more educated person shopped more? 

After code execution 103 nodes will be created:
- 30 Transaction nodes
- 3 Person nodes
- 15 Trip nodes
- 18 Country nodes
- 12 Education nodes
- 6 Work nodes
- 19 Year nodes

Please refer to neo4j_test.py for the import application. 

## Test of the database based on use cases

-----
**Case one:** Has Anil Kumar received any education?
```
MATCH (n:Person)-[:HAS_ACTIVITY {type:'education'}]-(e) WHERE n.name = 'Anil Kumar' RETURN e
```
Answer: Anil has received five qualifications 

-----
**Case two:** When and where did Anil Kumar receive her university education?
```
MATCH (n:Person)-[:HAS_ACTIVITY {type:'education'}]-(e:Education)-[:EVENT_LOCATION_AT]-(c:Country)
MATCH (n:Person)-[:HAS_ACTIVITY {type:'education'}]-(e:Education)-[:EVENT_ACTION_YEAR_START]-(y:Year)
WHERE n.name = 'Anil Kumar'
AND e.nameofinstitution CONTAINS 'University' 
RETURN c.name, y.year
```
Answer: 1992 in Vietnam. 


-----
**Case three:** What has Anil Kumar did during 1990-2000 (inclusive)?
```
MATCH (n:Person)-[r:HAS_ACTIVITY]-(e)-[:EVENT_ACTION_YEAR_START]-(y:Year)
WHERE n.name = 'Anil Kumar'
AND 1990<= y.year <=2000
RETURN labels(e)[0], y.year
```
Answer: Anil Kumar started education in 1992 and started work in 1996.

-----
**Case four:** How often does Anil Kumar shop?
```
MATCH (n:Person)-[r:HAS_ACTIVITY {type:'shopping'}]-(e)-[:EVENT_ACTION_YEAR_START]-(y:Year)
WHERE n.name = 'Anil Kumar'
RETURN y.year,count(r)
```
Answer: 10 times in year 2021. 

-----
**Case four:** What's the relationship between shopping and education?
```
MATCH (p:Person)
CALL {
  WITH p
 MATCH (p:Person)-[r:HAS_ACTIVITY {type:'shopping'}]-()
  RETURN count(r) AS count_shopping
}
CALL {
  WITH p
  MATCH (p:Person)-[r:HAS_ACTIVITY {type:'education'}]-()
  RETURN count(r) AS count_education
}
RETURN p.name, count_shopping,count_education

```

Answer:
There is no correlation. 
```
p.name	count_shopping	count_education
"Anil Kumar"	10	5
"Alice Gan"	10	3
"Ariff Johan"	10	4
```
