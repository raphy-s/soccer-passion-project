import requests
import pandas as pd
from supabase import create_client
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

# -----------------------
# SUPABASE
# -----------------------

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# -----------------------
# FOOTBALL DATA API
# -----------------------

headers = {
    "X-Auth-Token": API_KEY
}

url = "https://api.football-data.org/v4/competitions/WC/matches"

response = requests.get(
    url,
    headers=headers
)

matches = response.json()["matches"]

print(
    "Matches retrieved:",
    len(matches)
)

# -----------------------
# PROCESS RESULTS
# -----------------------

updated = 0

for match in matches:

    if match["status"] != "FINISHED":
        continue

    home_team = match["homeTeam"]["name"]
    away_team = match["awayTeam"]["name"]

    home_score = (
        match["score"]["fullTime"]["home"]
    )

    away_score = (
        match["score"]["fullTime"]["away"]
    )

    if home_score is None or away_score is None:
        continue

    # -----------------------
    # DETERMINE WINNER
    # -----------------------

    if home_score > away_score:

        winner = home_team

    elif away_score > home_score:

        winner = away_team

    else:

        winner = "Draw"

    # -----------------------
    # LOOKUP PREDICTION
    # -----------------------

    prediction = (
        supabase
        .table("world_cup_matches")
        .select("*")
        .eq("home_team", home_team)
        .eq("away_team", away_team)
        .execute()
    )

    if len(prediction.data) == 0:

        print(
            f"Prediction not found: {home_team} vs {away_team}"
        )

        continue

    prediction_row = prediction.data[0]

    pick = prediction_row["pick"]

    correct = (
        pick == winner
    )

    # -----------------------
    # UPDATE SUPABASE
    # -----------------------

    (
        supabase
        .table("world_cup_matches")
        .update(
            {
                "winner": winner,
                "correct": correct
            }
        )
        .eq("home_team", home_team)
        .eq("away_team", away_team)
        .execute()
    )

    updated += 1

    print(
        f"{home_team} {home_score}-{away_score} {away_team}"
    )

    print(
        f"Winner: {winner}"
    )

    print(
        f"Pick: {pick}"
    )

    print(
        f"Correct: {correct}"
    )

    print("-" * 40)

# -----------------------
# SUMMARY
# -----------------------

print(
    f"Updated {updated} completed matches."
)

print(
    "World Cup results sync complete 🚀"
)