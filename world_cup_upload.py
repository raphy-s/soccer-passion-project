import requests
import pandas as pd
from supabase import create_client, Client
import streamlit as st
import os

# -----------------------
# SECRETS
# -----------------------

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    API_KEY = st.secrets["FOOTBALL_API_KEY"]

except Exception:
    SUPABASE_URL = os.environ["SUPABASE_URL"]
    SUPABASE_KEY = os.environ["SUPABASE_KEY"]
    API_KEY = os.environ["FOOTBALL_API_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# -----------------------
# LOAD FIFA RANKINGS
# -----------------------

fifa_response = (
    supabase
    .table("world_cup_teams")
    .select("*")
    .execute()
)

fifa_df = pd.DataFrame(fifa_response.data)


fifa_lookup = dict(
    zip(
        fifa_df["team"],
        fifa_df["fifa_rank"]
    )
)

# -----------------------
# FOOTBALL DATA API
# -----------------------

headers = {
    "X-Auth-Token": API_KEY
}

url = "https://api.football-data.org/v4/competitions/WC/standings"

response = requests.get(
    url,
    headers=headers
)

data = response.json()

print(
    "Number of standings groups:",
    len(data["standings"])
)

rows = []

for group in data["standings"]:

    table = group["table"]

    for team in table:

        team_name = team["team"]["name"]

        fifa_rank = fifa_lookup.get(
            team_name,
            50
        )

        played = team["playedGames"]

        # Initial Elo

        elo_rating = 2000 - (
            fifa_rank * 10
        )

        # Power Rating

        if played == 0:

            power_rating = round(
                5 / fifa_rank,
                2
            )

        else:

            power_rating = round(
                (
                    2 * (
                        team["points"] / played
                    )
                    +
                    1.5 * (
                        team["goalDifference"] / played
                    )
                )
                +
                (
                    5 / fifa_rank
                ),
                2
            )

        rows.append({
            "position": team["position"],
            "team": team_name,
            "played": team["playedGames"],
            "won": team["won"],
            "draw": team["draw"],
            "lost": team["lost"],
            "points": team["points"],
            "goals_for": team["goalsFor"],
            "goals_against": team["goalsAgainst"],
            "goal_difference": team["goalDifference"],
            "fifa_rank": fifa_rank,
            "elo_rating": elo_rating,
            "power_rating": power_rating
        })
# -----------------------
# DATAFRAME
# -----------------------

df = pd.DataFrame(rows)

print("Teams found:", len(df))

print("Rows:", len(rows))
print(df.columns)
print(df.head())

# -----------------------
# POWER RANK
# -----------------------

df = df.sort_values(
    "power_rating",
    ascending=False
).reset_index(drop=True)

df["power_rank"] = df.index + 1

print(
    df[
        [
            "power_rank",
            "team",
            "fifa_rank",
            "power_rating"
        ]
    ].head(10)
)

# -----------------------
# UPLOAD TO SUPABASE
# -----------------------

for _, row in df.iterrows():

    (
        supabase
        .table("world_cup_standings")
        .upsert({
            "team": row["team"],
            "position": int(row["position"]),
            "played": int(row["played"]),
            "won": int(row["won"]),
            "draw": int(row["draw"]),
            "lost": int(row["lost"]),
            "points": int(row["points"]),
            "goals_for": int(row["goals_for"]),
            "goals_against": int(row["goals_against"]),
            "goal_difference": int(row["goal_difference"]),
            "fifa_rank": int(row["fifa_rank"]),
            "elo_rating": float(row["elo_rating"]),
            "power_rating": float(row["power_rating"]),
            "power_rank": int(row["power_rank"])
        })
        .execute()
    )

print(
    df[
        [
            "power_rank",
            "team",
            "fifa_rank",
            "elo_rating",
            "power_rating"
        ]
    ].head(10)
)

print("Upload complete 🚀")
