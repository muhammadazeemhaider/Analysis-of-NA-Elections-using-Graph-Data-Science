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

def get_pageRank():
    with driver.session() as session:
        # Create the graph projection
        # session.run(
        #     '''
        #     CALL gds.graph.project(
        #         'elections_graph',
        #         {
        #             Candidate: {label: 'Candidate', properties: []},
        #             Political_Party: {label: 'Political_Party', properties: []},
        #             Constituency: {label: 'Constituency', properties: []}
        #         },
        #         {
        #             CONTESTED_BY: {
        #                 orientation: 'NATURAL',
        #                 aggregation: 'NONE',
        #                 type: 'CONTESTED_BY',
        #                 properties: ['candidate_votes', 'candidate_share', 'outcome']
        #             },
        #             AFFILIATED_WITH: {
        #                 orientation: 'UNDIRECTED',
        #                 aggregation: 'NONE',
        #                 type: 'AFFILIATED_WITH',
        #                 properties: []
        #             }
        #         }
        #     )
        #     '''
        # )
        session.run(
            '''
                    CALL gds.graph.project(
            'elections_graph',   // Name of the graph projection
            {   // Node projections
                Candidate: {label: 'Candidate', properties: []}
            },
            {   // Relationship projections
                CONTESTED_BY: {
                    type: 'CONTESTED_BY',  // Specify the type of relationship
                    orientation: 'NATURAL',  // Directed from one node type to another
                    properties: ['candidate_votes', 'candidate_share', 'outcome'],
                    aggregation: 'NONE'  // How to handle multiple relationships between the same nodes
                }
            }
        )
            '''
        )

        # Query using PageRank algorithm
        result = session.run(
            '''
            CALL gds.pageRank.stream('elections_graph')
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).candidate_name AS Candidate, score AS pagerank
            ORDER BY pagerank DESC LIMIT 10
            '''
        )
        # Print results
        for record in result:
            print(record)
        
        # Drop the graph projection
        session.run('CALL gds.graph.drop("elections_graph")')
    # Close the session
    session.close()

    

def projection():
    # with driver.session() as session:
    gds.graph.drop("elections_graph")
    G, project_info = gds.graph.project(
        "elections_graph",
        {
            "Candidate": {"label": "Candidate", "properties": []},
            # "Political_Party": {"label": "Political_Party", "properties": []},
            # "Constituency": {"label": "Constituency", "properties": []}
        },
        {
            "CONTESTED_BY": {
                "orientation": "NATURAL",  # Directed as per the relationship in Neo4j
                "aggregation": "NONE",
                "type": "CONTESTED_BY",
                "properties": ["candidate_votes", "candidate_share", "outcome"]  # Assuming these are the field names in Neo4j
            }
            # "AFFILIATED_WITH": {
            #     "orientation": "UNDIRECTED",
            #     "aggregation": "NONE",
            #     "type": "AFFILIATED_WITH",
            #     "properties": []
            # }
        }
    )
    pagerank_result = gds.pageRank.stream(G)
    print(pagerank_result[:10])
    # pagerank_result = sorted(pagerank_result, key=lambda x: x['score'], reverse=True)
    # for node in pagerank_result[:10]:  # Adjust the slice for more or fewer results
    #     print(node)
    gds.graph.drop("elections_graph")


def main():
    # fetch_data()
    # projection()
    get_pageRank()

if __name__ == '__main__':
    main()