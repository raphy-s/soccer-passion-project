import requests
import pandas as pd
from supabase import create_client, Client

import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
API_KEY = st.secrets["FOOTBALL_API_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------
# FOOTBALL API
# -----------------------
API_KEY = "531070fe203d4adaa853a65c382fb4b8"

headers = {
    "X-Auth-Token": API_KEY
}

url = "https://api.football-data.org/v4/competitions/PL/standings"

response = requests.get(url, headers=headers)
data = response.json()

table = data["standings"][0]["table"]

# -----------------------
# TRANSFORM DATA
# -----------------------
rows = []

for team in table:
    rows.append({
        "position": team["position"],
        "team": team["team"]["name"],
        "played": team["playedGames"],
        "won": team["won"],
        "draw": team["draw"],
        "lost": team["lost"],
        "points": team["points"],
        "goals_for": team["goalsFor"],
        "goals_against": team["goalsAgainst"],
        "goal_difference": team["goalDifference"],

        "power_rating": round(
            2 * (team["points"] / team["playedGames"])
            + 1.5 * (team["goalDifference"] / team["playedGames"]),
            2
        )
    })

df = pd.DataFrame(rows)

# -----------------------
# POWER RANK
# -----------------------
df = df.sort_values("power_rating", ascending=False).reset_index(drop=True)
df["power_rank"] = df.index + 1

# -----------------------
# UPLOAD TO SUPABASE
# -----------------------
for _, row in df.iterrows():
    supabase.table("premier_league_standings").insert({
        "position": int(row["position"]),
        "team": row["team"],
        "played": int(row["played"]),
        "won": int(row["won"]),
        "draw": int(row["draw"]),
        "lost": int(row["lost"]),
        "points": int(row["points"]),
        "goals_for": int(row["goals_for"]),
        "goals_against": int(row["goals_against"]),
        "goal_difference": int(row["goal_difference"]),
        "power_rating": float(row["power_rating"]),
        "power_rank": int(row["power_rank"])
    }).execute()

print("Upload complete 🚀")