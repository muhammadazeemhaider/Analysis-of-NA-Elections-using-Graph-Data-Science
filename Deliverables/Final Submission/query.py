from neo4j import GraphDatabase
from graphdatascience import GraphDataScience
# import gds

uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456789"

gds = GraphDataScience(uri, auth=(user, password))
driver = GraphDatabase.driver(uri, auth=(user, password))

def fetch_data():
    with driver.session() as session:
        result = session.run(
            '''
            MATCH (c:Candidate) - [:AFFILIATED_WITH] -> (p:Political_Party)
            RETURN * LIMIT 10 
            ''')
        for record in result:
            C_node = record['c']  # Access the node from the record
            P_node = record['p']
            C_labels = list(C_node.labels)  # Convert labels set to list for easier manipulation
            C_properties = dict(C_node)  # Convert node properties to dictionary
            P_labels = list(P_node.labels)
            P_properties = dict(P_node)
            # print(record)
            # Print labels and properties
            print(f"{C_labels}, {C_properties}")
            print(f"{P_labels}, {P_properties}")
            # print(f"Labels: {labels}, Properties: {properties}")
    session.close()

def projection():
    # with driver.session() as session:
    G, res = gds.graph.project('sample-proj', ['Candidate'], 
    {'*'})
    a = gds.pageRank.stream(G, nodeLabels=['Candidate'], 
    relationshipTypes=['*'])
    print(a)
    print(G)
    print(res)
    # session.close()

def main():
    # fetch_data()
    projection()

if __name__ == '__main__':
    main()