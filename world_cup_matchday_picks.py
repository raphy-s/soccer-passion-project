import pandas as pd
from supabase import create_client
import streamlit as st
import os
import requests

# -----------------------
# SUPABASE
# -----------------------

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    API_KEY = st.secrets["FOOTBALL_API_KEY"]

except Exception:
    SUPABASE_URL = os.environ["SUPABASE_URL"]
    SUPABASE_KEY = os.environ["SUPABASE_KEY"]
    API_KEY = os.environ["FOOTBALL_API_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# -----------------------
# LOAD WORLD CUP RATINGS
# -----------------------

response = (
    supabase
    .table("world_cup_standings")
    .select("*")
    .execute()
)

df = pd.DataFrame(response.data)

ratings = dict(
    zip(
        df["team"],
        df["elo_rating"]
    )
)


# -----------------------
# GET WORLD CUP FIXTURES
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

# Sort chronologically

matches = sorted(
    matches,
    key=lambda x: x["utcDate"]
)

print("Matches found:", len(matches))

# -----------------------
# GENERATE PICKS
# -----------------------

for match in matches:

    if match["status"] not in ["SCHEDULED", "TIMED"]:
        continue

    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]

    # Skip knockout placeholders

    if not home or not away:
        continue

    home_rating = ratings.get(home)
    away_rating = ratings.get(away)

    if home_rating is None:
        print("Missing home team:", home)
        continue

    if away_rating is None:
        print("Missing away team:", away)
        continue

    # Elo win probability

    home_probability = (
        1 /
        (
            1 +
            10 ** (
                (away_rating - home_rating)
                / 400
            )
        )
    )

    away_probability = (
        1 - home_probability
    )

    if home_probability > away_probability:

        pick = home

        win_probability = round(
            home_probability * 100,
            1
        )

    else:

        pick = away

        win_probability = round(
            away_probability * 100,
            1
        )

    diff = abs(
        home_probability
        -
        away_probability
    ) * 100

    if diff >= 40:
        confidence = "Very High"

    elif diff >= 25:
        confidence = "High"

    elif diff >= 10:
        confidence = "Medium"

    else:
        confidence = "Low"
    print(
        {
        "home_team": home,
        "away_team": away,
        "pick": pick,
        "confidence": confidence,
        "rating_difference": diff,
        "win_probability": win_probability,
        "match_date": match["utcDate"]
        }
    )

    payload = {
    "home_team": home,
    "away_team": away,
    "pick": pick,
    "confidence": confidence,
    "rating_difference": float(diff),
    "win_probability": float(win_probability),
    "match_date": match["utcDate"]
}

    result = (
        supabase
        .table("world_cup_matches")
        .insert(payload)
        .execute()
    )

    print(result.data)

print("Matchday picks uploaded 🚀")
