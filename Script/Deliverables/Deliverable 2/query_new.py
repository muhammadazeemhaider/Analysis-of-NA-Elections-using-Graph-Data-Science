from neo4j import GraphDatabase
import json

uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

driver = GraphDatabase.driver(uri, auth=(user, password))

def fetch_data():
    query = """
        MATCH (a:Candidate {name: "Dr. M. Farooq Sattar"}), (b:Candidate {name: "Asad Umar"})
        WITH a, b
        MATCH q = shortestPath((a)-[*..5]-(b))
        RETURN q
    """
    results = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            path = record['q']
            nodes = [{"labels": list(node.labels), "properties": dict(node)} for node in path.nodes]
            relationships = [{"type": rel.type, "properties": dict(rel)} for rel in path.relationships]
            results.append({"nodes": nodes, "relationships": relationships})
    
    session.close()
    return json.dumps(results, indent=4)

def find_dominant_party():
    query = """
        MATCH (co:Constituency)-[:CONTESTED_BY {outcome: "Win"}]->(c:Candidate)
        MATCH (c)-[:AFFILIATED_WITH]->(pp:Political_Party)
        WITH co.election_date AS Election_Year, pp.Name AS Political_Party, COUNT(co) AS Won_Constituencies
        ORDER BY Election_Year, Won_Constituencies DESC
        WITH Election_Year, COLLECT({Party: Political_Party, Wins: Won_Constituencies}) AS PartyWins
        RETURN Election_Year, HEAD(PartyWins) AS Dominant_Party
    """
    results = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            results.append({
                "Election Year": record["Election_Year"],
                "Dominant Party": record["Dominant_Party"]
            })
    
    session.close()
    return json.dumps(results, indent=4)

def find_multiyear_winners():
    query = """
        MATCH (co:Constituency)-[r:CONTESTED_BY {outcome: "Win"}]->(c:Candidate)
        WITH co.constituency_number AS Constituency, c.name AS Candidate, co.election_date AS Election_Year
        ORDER BY Constituency, Candidate, Election_Year
        WITH Constituency, Candidate, COLLECT(DISTINCT Election_Year) AS Unique_Election_Years
        WHERE SIZE(Unique_Election_Years) > 1
        RETURN Constituency, Candidate, Unique_Election_Years, SIZE(Unique_Election_Years) AS Win_Count
        ORDER BY Win_Count DESC, Constituency, Candidate
    """
    results = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            results.append({
                "Constituency": record["Constituency"],
                "Candidate": record["Candidate"],
                "Unique Election Years": record["Unique_Election_Years"],
                "Win Count": record["Win_Count"]
            })
    
    session.close()
    return json.dumps(results, indent=4)

def find_avg_voter_registration():
    query = """
        MATCH (co:Constituency)-[:BELONGS_TO]->(p:Province)
        RETURN p.Name AS Province, AVG(co.voter_reg) AS Avg_Voter_Registration
        ORDER BY Avg_Voter_Registration DESC
    """
    results = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            results.append({
                "Province": record["Province"],
                "Average Voter Registration": record["Avg_Voter_Registration"]
            })
    
    session.close()
    return json.dumps(results, indent=4)

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
    results = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            results.append({
                "Election Year": record["Election_Year"],
                "Candidate Info": record["Candidate_With_Highest_Vote_Share"]
            })
    
    session.close()
    return json.dumps(results, indent=4)

def main():
    # Example usage
    # data = fetch_data()
    # dominant_parties = find_dominant_party()
    multiyear_winners = find_multiyear_winners()
    # voter_registrations = find_avg_voter_registration()
    # top_candidates = find_top_candidate_by_vote_share()

    # print(data)
    # print(dominant_parties)
    print(multiyear_winners)
    # print(voter_registrations)
    # print(top_candidates)

if __name__ == '__main__':
    main()
