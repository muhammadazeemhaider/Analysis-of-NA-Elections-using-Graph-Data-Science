import pandas as pd

# constituency_df = pd.read_csv("Data\\CONTESTED_BY.csv")
# filtered_df = constituency_df[constituency_df["constituency_number"].str.startswith("NA")]
# filtered_df.to_csv("filtered_CONTESTED_BY.csv", index=False)\

# election_data = pd.read_csv("Data\\CONTESTED_BY.csv")
# election_data["election_date"] = election_data["election_date"].astype(int)
# filtered_data = election_data[election_data["election_date"] < 2014]
# filtered_data.to_csv("filtered_CONTESTED_BY.csv", index=False)

# election_data = pd.read_csv("Data\\CONTESTED_BY.csv")

# election_data["election_date"] = election_data["election_date"].astype(int)
# election_data = election_data[election_data["election_date"] != 2003]
# filtered_data = election_data[election_data["election_date"] < 2014]
# filtered_data.to_csv("CONTESTED_BY.csv", index=False)

data = pd.read_csv("Data\\CONTESTED_BY.csv")

unique_data = data.drop_duplicates(subset=["election_date", "constituency_number", "candidateID"])
unique_data.to_csv("CONTESTED_BY.csv", index=False)
