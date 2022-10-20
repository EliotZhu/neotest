from neo4j import GraphDatabase



def data_import(driver):
    '''Function for data import'''
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        try:
            # Import Education Data
            session.run(
                """
                USING PERIODIC COMMIT
                LOAD CSV WITH HEADERS
                FROM 'https://gist.githubusercontent.com/maruthiprithivi/10b456c74ba99a35a52caaffafb9d3dc/raw/a46af9c6c4bf875ded877140c112e9ff36f8f2e8/sng_education.csv'
                AS row
                //process rows
                WITH row
                MERGE (p:Person {passport_number:row.passportnumber, name:row.name})
                MERGE (e:Education {passport_number:row.passportnumber, nameofinstitution:row.nameofinstitution})
                MERGE (c:Country {name:row.country})
                MERGE (d1:Year {year: toInteger(row.startyear)})
                MERGE (d2:Year {year: toInteger(row.endyear)})
                MERGE (p)-[:HAS_ACTIVITY {type:'education'}]->(e)
                MERGE (p)-[:PERSON_ACTION_LOCATION {type:'education'}]->(c)
                MERGE (p)-[:PERSON_ACTION_YEAR_START {type:'education'}]->(d1)
                MERGE (p)-[:PERSON_ACTION_YEAR_END {type:'education'}]->(d2)
                MERGE (e)-[:EVENT_ACTION_YEAR_START {type:'education'}]->(d1)
                MERGE (e)-[:EVENT_ACTION_YEAR_END {type:'education'}]->(d2)
                MERGE (e)-[:EVENT_LOCATION_AT {type:'education'}]->(c)
                RETURN p
                """
            )
            # Import Transaction Data
            print('Education Data Imported', end='\r')
            session.run(
                """
                USING PERIODIC COMMIT
                LOAD CSV WITH HEADERS
                FROM 'https://gist.githubusercontent.com/maruthiprithivi/10b456c74ba99a35a52caaffafb9d3dc/raw/a46af9c6c4bf875ded877140c112e9ff36f8f2e8/sng_transaction.csv'
                AS row
                WITH row, apoc.date.parse(row.transactiondate, "ms", "EEEEE, dd MMMMM yyyy") as ms
                MERGE (p:Person {passport_number:row.passportnumber, name:row.name})
                MERGE (t:Transaction {passport_number:row.passportnumber, cardNumber:row.cardnumber,merchant:row.merchant,amount: apoc.number.parseFloat(row.amount, '$#.;(#.)', 'it'),date:date(datetime({epochmillis: ms})) })
                MERGE (p)-[:HAS_ACTIVITY {type:'shopping'}]-(t)
                MERGE (c:Country {name:row.country})
                MERGE (d:Year {year: t.date.year})
                MERGE (p)-[:PERSON_ACTION_LOCATION {type:'shopping'}]->(c)
                MERGE (p)-[:PERSON_ACTION_YEAR_START {type:'shopping'}]->(d)
                MERGE (t)-[:EVENT_LOCATION_AT {type:'shopping'}]->(c)
                MERGE (t)-[:EVENT_ACTION_YEAR_START {type:'shopping'}]->(d)
                RETURN p,t
                """
            )
            print('Transaction Data Imported', end='\r')

            # Import Trip Data
            session.run(
                """
                USING PERIODIC COMMIT
                LOAD CSV WITH HEADERS
                FROM 'https://gist.githubusercontent.com/maruthiprithivi/10b456c74ba99a35a52caaffafb9d3dc/raw/a46af9c6c4bf875ded877140c112e9ff36f8f2e8/sng_trips.csv'
                AS row
                //process rows
                WITH row, apoc.date.parse(row.departuredate, "ms", "EEEEE, dd MMMMM yyyy") as ms,
                     apoc.date.parse(row.arrivaldate, "ms", "EEEEE, dd MMMMM yyyy") as ms2
                MERGE (p:Person {passport_number:row.passportnumber, name:row.name})
                MERGE (t:Trip  {passport_number:row.passportnumber, departuredate:date(datetime({epochmillis: ms}))})
                SET t.arrivaldate=date(datetime({epochmillis: ms2}))
                MERGE (p)-[:HAS_ACTIVITY {type:'travel'}]->(t)
                MERGE (d1:Year {year: t.departuredate.year})
                MERGE (d2:Year {year: t.arrivaldate.year})
                MERGE (c:Country {name:row.departurecountry})
                MERGE (c1:Country {name:row.citizenship})
                MERGE (c2:Country {name:row.arrivalcountry})
                MERGE (p)-[:PERSON_ACTION_LOCATION {type:'travel'}]->(c2)
                MERGE (p)-[:PERSON_ACTION_ORIGINAL_LOCATION {type:'travel'}]->(c)
                MERGE (p)-[:IS_CITIZEN_OF]->(c1)
                MERGE (p)-[:PERSON_ACTION_YEAR_START {type:'travel'}]->(d1)
                MERGE (p)-[:PERSON_ACTION_YEAR_END {type:'travel'}]->(d2)
                MERGE (t)-[:EVENT_LOCATION_AT {type:'travel'}]->(c2)
                MERGE (t)-[:EVENT_ORIGINAL_LOCATION {type:'travel'}]->(c)
                MERGE (t)-[:EVENT_ACTION_YEAR_START {type:'travel'}]->(c2)
                MERGE (t)-[:EVENT_ACTION_YEAR_END {type:'travel'}]->(c)
                RETURN p
                """
            )
            print('Education Trip Imported', end='\r')

            # Import Work Data
            session.run(
                """
                USING PERIODIC COMMIT
                LOAD CSV WITH HEADERS
                FROM 'https://gist.githubusercontent.com/maruthiprithivi/10b456c74ba99a35a52caaffafb9d3dc/raw/a46af9c6c4bf875ded877140c112e9ff36f8f2e8/sng_work.csv'
                AS row
                //process rows
                WITH row
                MERGE (p:Person {passport_number:row.passportnumber, name:row.name})
                MERGE (e:Work {passport_number:row.passportnumber, nameoforganization:row.nameoforganization})
                MERGE (c:Country {name:row.country})
                MERGE (d1:Year {year: toInteger(row.startyear)})
                MERGE (d2:Year {year: coalesce(toInteger(row.endyear),2100)})
                MERGE (p)-[:HAS_ACTIVITY {type:'work'}]->(e)
                MERGE (p)-[:PERSON_ACTION_LOCATION {type:'work'}]->(c)
                MERGE (p)-[:PERSON_ACTION_YEAR_START {type:'work'}]->(d1)
                MERGE (p)-[:PERSON_ACTION_YEAR_END {type:'work'}]->(d2)
                MERGE (e)-[:EVENT_LOCATION_AT {type:'work'}]->(c)
                MERGE (e)-[:EVENT_ACTION_YEAR_START {type:'work'}]->(d1)
                MERGE (e)-[:PERSON_ACTION_YEAR_END {type:'work'}]->(d2)
                RETURN p
                """
            )
            print('Education Work Imported', end='\r')
            print('Data Successfully Imported')
        except:
            print('Data Import Failed')


if __name__ == "__main__":
    # Create a new Driver instance
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "s3cr3t"))
    driver.verify_connectivity()
    data_import(driver)


    with driver.session() as session:
        result = session.run(
            '''
            MATCH (p:Country)
            CALL {
              WITH p
             MATCH (p:Country)-[r:EVENT_LOCATION_AT]-(e:Transaction)
              RETURN count(r) AS count_shopping
            }
            CALL {
              WITH p
              MATCH (p:Country)-[r:EVENT_LOCATION_AT]-(e:Education)
              RETURN count(r) AS count_education
            }
            CALL {
              WITH p
              MATCH (p:Country)-[r:EVENT_LOCATION_AT]-(e:Work)
              RETURN count(r) AS count_work
            }
            CALL {
              WITH p
              MATCH (p:Country)-[r:EVENT_LOCATION_AT]-(e:Trip)
              RETURN count(r) AS count_trip
            }
            RETURN p.name, count_shopping,count_education,count_work,count_trip
            '''
        )
