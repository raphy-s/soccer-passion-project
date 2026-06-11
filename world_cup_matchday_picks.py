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
        df["power_rating"]
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

    home_rating = ratings.get(home, 0)
    away_rating = ratings.get(away, 0)


    if home_rating is None:
        print("Missing home team:", home)
        continue

    if away_rating is None:
        print("Missing away team:", away)
        continue

    diff = abs(home_rating - away_rating)

    if home_rating > away_rating:
        pick = home
    else:
        pick = away

    confidence_score = round(diff * 10, 1)

    if diff >= 3:
        confidence = "Very High"
    elif diff >= 2:
        confidence = "High"
    elif diff >= 1:
        confidence = "Medium"
    else:
        confidence = "Low"

    print(
        f"{home} vs {away} | "
        f"Pick: {pick} | "
        f"Confidence: {confidence} | "
        f"Score: {confidence_score}/10"
    )
    print("INSERTING:", home, "vs", away)
    supabase.table(
        "world_cup_matches"
    ).insert(
        {
            "home_team": home,
            "away_team": away,
            "pick": pick,
            "confidence": confidence,
            "rating_difference": diff,
            "match_date": match["utcDate"]
        }
    ).execute()

print("Matchday picks uploaded 🚀")
print(sorted(df["team"].tolist()))