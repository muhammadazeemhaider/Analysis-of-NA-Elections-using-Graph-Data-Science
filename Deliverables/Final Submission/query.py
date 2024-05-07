from neo4j import GraphDatabase
from graphdatascience import GraphDataScience
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay

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
            MATCH (a:Candidate {name: "Dr. M. Farooq Sattar"}), (b:Candidate {name: "Asad Umar"})
            WITH a, b
            MATCH q = shortestPath((a)-[*..5]-(b))
            RETURN q
            '''
        )
        for record in result:
            path = record['q']  
            print(f'Path: {path}')

            # Access nodes in the path
            for node in path.nodes:
                node_labels = list(node.labels)
                node_properties = dict(node)

                # Print node labels and properties
                print(f"Node Labels: {node_labels}, Properties: {node_properties}")

            # Access relationships in the path (optional)
            for relationship in path.relationships:
                relationship_type = relationship.type
                relationship_properties = dict(relationship)

                print(f"Relationship Type: {relationship_type}, Properties: {relationship_properties}")

    session.close()

def find_dominant_party():
    query = """
        MATCH (co:Constituency)-[:CONTESTED_BY {outcome: "Win"}]->(c:Candidate)
        MATCH (c)-[:AFFILIATED_WITH]->(pp:Political_Party)
        WITH co.election_date AS Election_Year, pp.Name AS Political_Party, COUNT(co) AS Won_Constituencies
        ORDER BY Election_Year, Won_Constituencies DESC
        WITH Election_Year, COLLECT({Party: Political_Party, Wins: Won_Constituencies}) AS PartyWins
        RETURN Election_Year, HEAD(PartyWins) AS Dominant_Party
    """
    
    with driver.session() as session:
        result = session.run(query)
        
        # Process the results
        for record in result:
            election_year = record["Election_Year"]
            dominant_party = record["Dominant_Party"]
            
            print(f"Election Year: {election_year}, Dominant Party: {dominant_party['Party']} with {dominant_party['Wins']} Wins")
    
    session.close()

def find_multiyear_winners():
    query = """
        MATCH (co:Constituency)-[r:CONTESTED_BY {outcome: "Win"}]->(c:Candidate)
        WITH co.constituency_number AS Constituency, c.name AS Candidate, co.election_date AS Election_Year
        ORDER BY Constituency, Candidate, Election_Year
        
        WITH Constituency, Candidate, COLLECT(DISTINCT Election_Year) AS Unique_Election_Years
        WHERE SIZE(Unique_Election_Years) > 1  // At least two unique wins in the same constituency
        
        RETURN Constituency, Candidate, Unique_Election_Years, SIZE(Unique_Election_Years) AS Win_Count
        ORDER BY Win_Count DESC, Constituency, Candidate
    """
    
    with driver.session() as session:
        result = session.run(query)

        # Process the results
        for record in result:
            constituency = record["Constituency"]
            candidate = record["Candidate"]
            unique_election_years = record["Unique_Election_Years"]
            win_count = record["Win_Count"]
            
            # Display candidate information
            print(f"Constituency: {constituency}, Candidate: {candidate}, "
                  f"Unique Election Years: {unique_election_years}, Win Count: {win_count}")
    
    session.close()

def find_avg_voter_registration():
    query = """
        MATCH (co:Constituency)-[:BELONGS_TO]->(p:Province)
        RETURN p.Name AS Province, AVG(co.voter_reg) AS Avg_Voter_Registration
        ORDER BY Avg_Voter_Registration DESC
    """
    
    with driver.session() as session:
        result = session.run(query)

        for record in result:
            province = record["Province"]
            avg_voter_registration = record["Avg_Voter_Registration"]
            
            print(f"Province: {province}, Average Voter Registration: {avg_voter_registration}")
    
    session.close()

def find_top_candidate_by_vote_share():
    query = """
        MATCH (co:Constituency)-[r:CONTESTED_BY {outcome: "Win"}]->(c:Candidate)
        MATCH (co)-[:BELONGS_TO]->(p:Province)
        MATCH (c)-[:AFFILIATED_WITH]->(pp:Political_Party)
        WITH co.election_date AS Election_Year, co.constituency_number AS Constituency,
             co.constituency_name AS Constituency_Name, p.Name AS Province,
             c.name AS Candidate, pp.Name AS Political_Party,
             r.candidate_share AS Vote_Share
        ORDER BY Election_Year, Vote_Share DESC
        
        WITH Election_Year, COLLECT({
            Vote_Share: Vote_Share,
            Candidate: Candidate,
            Constituency: Constituency,
            Constituency_Name: Constituency_Name,
            Province: Province,
            Political_Party: Political_Party
        }) AS Candidates
        
        RETURN Election_Year, HEAD(Candidates) AS Candidate_With_Highest_Vote_Share
    """
    
    with driver.session() as session:
        result = session.run(query)

        for record in result:
            election_year = record["Election_Year"]
            candidate_info = record["Candidate_With_Highest_Vote_Share"]
            
            vote_share = candidate_info["Vote_Share"]
            candidate = candidate_info["Candidate"]
            constituency = candidate_info["Constituency"]
            constituency_name = candidate_info["Constituency_Name"]
            province = candidate_info["Province"]
            political_party = candidate_info["Political_Party"]
            
            print(f"Election Year: {election_year}, Candidate: {candidate}, "
                  f"Vote Share: {vote_share}, Constituency: {constituency}, "
                  f"Constituency Name: {constituency_name}, Province: {province}, "
                  f"Political Party: {political_party}")
    
    session.close()

# def get_pageRank():
#     with driver.session() as session:
#         # session.run('CALL gds.graph.drop("elections_graph")')
#         # Create the graph projection
#         # session.run(
#         #     '''
#         #     CALL gds.graph.project(
#         #         'elections_graph',
#         #         {
#         #             Candidate: {label: 'Candidate', properties: []},
#         #             Political_Party: {label: 'Political_Party', properties: []},
#         #             Constituency: {label: 'Constituency', properties: []}
#         #         },
#         #         {
#         #             CONTESTED_BY: {
#         #                 orientation: 'NATURAL',
#         #                 aggregation: 'NONE',
#                         #  type: 'CONTESTED_BY',
#         #                 properties: ['candidate_votes', 'candidate_share', 'outcome']
#         #             },
#         #             AFFILIATED_WITH: {
#         #                 orientation: 'UNDIRECTED',
#         #                 aggregation: 'NONE',
#         #                 type: 'AFFILIATED_WITH',
#         #                 properties: []
#         #             }
#         #         }
#         #     )
#         #     '''
#         # )
#         session.run(
#             '''
#                     CALL gds.graph.project(
#             'elections_graph',   // Name of the graph projection
#             {   // Node projections
#                 Candidate: {label: 'Candidate', properties: []},
#                 Constituency: {label: 'Constituency', properties: []}
#             },
#             {   // Relationship projections
#                 CONTESTED_BY: {
#                     type: 'CONTESTED_BY',  // Specify the type of relationship
#                     orientation: 'NATURAL',  // Directed from one node type to another
#                     properties: ['candidate_votes', 'candidate_share', 'outcome'],
#                     aggregation: 'NONE'  // How to handle multiple relationships between the same nodes
#                 }
#             }
#         )
#             '''
#         )

#         # Query using PageRank algorithm
#         result = session.run(
#             '''
#             CALL gds.betweenness.stream('elections_graph')
#             YIELD nodeId, score
#             RETURN gds.util.asNode(nodeId).name AS name, score
#             ORDER BY score desc limit 10
#             '''
#         )
#         # Print results
#         for record in result:
#             print(record)
        
#         # Drop the graph projection
#         session.run('CALL gds.graph.drop("elections_graph")')
#     # Close the session
#     session.close()

    

def machine_learning():
    # with driver.session() as session:
    query = """
        MATCH (c:Constituency)-[:BELONGS_TO]->(p:Province),
            (c)-[cb:CONTESTED_BY]->(can:Candidate)-[:AFFILIATED_WITH]->(party:Political_Party)
        RETURN c.constituency_number AS constituency,
            party.Name AS affiliated_party, 
            p.Name AS province_of_constituency, 
            cb.outcome AS outcome
    """
    with driver.session() as session:
        df = pd.DataFrame(session.run(query))

        df = df.rename(columns={0: 'constituency', 1: 'affiliated_party', 
                                2: 'province', 3: 'outcome'})

        df['constituency'] = df['constituency'].str.extract(r'(\d+)')
        df['outcome'] = df['outcome'].apply(lambda x: 1 if x == 'Win' else 0)
        df = pd.get_dummies(df, columns=['affiliated_party', 'province'])
        # print(df)

        df_X = df.drop('outcome', axis=1)
        df_y = df[['outcome']]

        X = df_X.values
        y = df_y.values

        y = LabelBinarizer().fit_transform(y)
        
        # Test/train data split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=42, stratify=y)
        
        # Oversample only the training data
        oversample = SMOTE(random_state=42)
        X_train, y_train = oversample.fit_resample(X_train, y_train)

        # Random forrest classification
        model = RandomForestClassifier(n_estimators=500, random_state=42, max_depth=5, bootstrap=True, class_weight='balanced')
        model = model.fit(X_train, y_train)
        # Evaluate the model
        cm_display = ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, normalize= 'true')
        roc_display = RocCurveDisplay.from_estimator(model, X_test, y_test, name="RF Model")

        plt.figure(figsize=(10, 5))
        cm_display.plot()
        plt.title('Confusion Matrix')

        # Plot ROC curve
        plt.figure(figsize=(10, 5))
        roc_display.plot()
        plt.title('ROC Curve')

        plt.show()

def machine_learning_pagerank():
    # driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("user", "password"))
    with driver.session() as session:
        # Create the in-memory graph projection
        session.run('CALL gds.graph.drop("electionGraph")')
        session.run("""
        CALL gds.graph.project(
                'electionGraph',
                {
                    Candidate: {label: 'Candidate', properties: []},
                    Political_Party: {label: 'Political_Party', properties: []},
                    Constituency: {label: 'Constituency', properties: []}
                },
                {
                    CONTESTED_BY: {
                        orientation: 'NATURAL',
                        aggregation: 'NONE',
                         type: 'CONTESTED_BY',
                        properties: ['candidate_votes', 'candidate_share']
                    },
                    AFFILIATED_WITH: {
                        orientation: 'UNDIRECTED',
                        aggregation: 'NONE',
                        type: 'AFFILIATED_WITH',
                        properties: []
                    }
                }
            )
        """)

        # Run PageRank on the in-memory graph
        session.run("""
        CALL gds.pageRank.write('electionGraph', {
            maxIterations: 20,
            dampingFactor: 0.85,
            writeProperty: 'pageRank'
        })
        """)

        # Run Jaccard similarity
        # jaccard_result = session.run("""
        # CALL gds.nodeSimilarity.stream('electionGraph')
        # RETURN node1, node2, similarity
        # """)

        # Fetching the result with added PageRank
        result = session.run("""
        MATCH (c:Constituency)-[:BELONGS_TO]->(p:Province),
              (c)-[cb:CONTESTED_BY]->(can:Candidate)-[:AFFILIATED_WITH]->(party:Political_Party)
        RETURN c.constituency_number AS constituency,
               party.name AS affiliated_party,
               p.name AS province,
               cb.outcome AS outcome,
               can.pageRank AS candidatePageRank,
               c.pageRank AS constituencyPageRank
        """)

        df = pd.DataFrame([dict(record) for record in result])

        df['constituency'] = df['constituency'].str.extract(r'(\d+)')
        df['outcome'] = df['outcome'].apply(lambda x: 1 if x == 'Win' else 0)
        df = pd.get_dummies(df, columns=['affiliated_party', 'province'])
        # print(df)

        df_X = df.drop('outcome', axis=1)
        df_y = df[['outcome']]

        X = df_X.values
        y = df_y.values

        y = LabelBinarizer().fit_transform(y)
        
        # Test/train data split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=42, stratify=y)
        
        # Oversample only the training data
        oversample = SMOTE(random_state=42)
        X_train, y_train = oversample.fit_resample(X_train, y_train)

        # Random forrest classification
        model = RandomForestClassifier(n_estimators=500, random_state=42, max_depth=5, bootstrap=True, class_weight='balanced')
        model = model.fit(X_train, y_train)
        # Evaluate the model
        cm_display = ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, normalize= 'true')
        roc_display = RocCurveDisplay.from_estimator(model, X_test, y_test, name="RF Model")

        plt.figure(figsize=(10, 5))
        cm_display.plot()
        plt.title('Confusion Matrix')

        # Plot ROC curve
        plt.figure(figsize=(10, 5))
        roc_display.plot()
        plt.title('ROC Curve')

        plt.show()
        session.run('CALL gds.graph.drop("electionGraph")')



    # gds.graph.drop("elections_graph")
    # G, project_info = gds.graph.project(
    #     "elections_graph",
    #     {
    #         "Candidate": {"label": "Candidate", "properties": []},
    #         # "Political_Party": {"label": "Political_Party", "properties": []},
    #         # "Constituency": {"label": "Constituency", "properties": []}
    #     },
    #     {
    #         "CONTESTED_BY": {
    #             "orientation": "NATURAL",  # Directed as per the relationship in Neo4j
    #             "aggregation": "NONE",
    #             "type": "CONTESTED_BY",
    #             "properties": ["candidate_votes", "candidate_share", "outcome"]  # Assuming these are the field names in Neo4j
    #         }
    #         # "AFFILIATED_WITH": {
    #         #     "orientation": "UNDIRECTED",
    #         #     "aggregation": "NONE",
    #         #     "type": "AFFILIATED_WITH",
    #         #     "properties": []
    #         # }
    #     }
    # )
    # pagerank_result = gds.pageRank.stream(G)
    # print(pagerank_result[:10])
    # # pagerank_result = sorted(pagerank_result, key=lambda x: x['score'], reverse=True)
    # # for node in pagerank_result[:10]:  # Adjust the slice for more or fewer results
    # #     print(node)
    # gds.graph.drop("elections_graph")

def main():
    # fetch_data()
    # find_dominant_party()
    # find_multiyear_winners()
    # find_avg_voter_registration()
    # find_top_candidate_by_vote_share()
    # projection()
    # get_pageRank()
    machine_learning_pagerank()

if __name__ == '__main__':
    main()