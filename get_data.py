import requests
import pandas as pd

API_KEY = "531070fe203d4adaa853a65c382fb4b8"

headers = {
    "X-Auth-Token": API_KEY
}

url = "https://api.football-data.org/v4/competitions/PL/standings"

response = requests.get(url, headers=headers)

data = response.json()

table = data["standings"][0]["table"]

rows = []

for team in table:
    rows.append({
    "Position": team["position"],
    "Team": team["team"]["name"],
    "Played": team["playedGames"],
    "Won": team["won"],
    "Draw": team["draw"],
    "Lost": team["lost"],
    "Points": team["points"],
    "GoalsFor": team["goalsFor"],
    "GoalsAgainst": team["goalsAgainst"],
    "GoalDifference": team["goalDifference"],
    "AttackRating": round(
        team["goalsFor"] / team["playedGames"],
        2
    ),
    "DefenseRating": round(
        team["goalsAgainst"] / team["playedGames"],
        2
    ),
    "PointsPerGame": round(
        team["points"] / team["playedGames"], 2
    ),
    "AttackRating": round(
        team["goalsFor"] / team["playedGames"],
        2
),

"DefenseRating": round(
    team["goalsAgainst"] / team["playedGames"],
    2
),
"GoalDiffPerGame": round(
    team["goalDifference"] / team["playedGames"], 2
),
    "PowerRating": round(
    2 * (team["points"] / team["playedGames"])
    + (team["goalsFor"] / team["playedGames"])
    - (team["goalsAgainst"] / team["playedGames"])
    + 0.5 * (team["goalDifference"] / team["playedGames"]),
    2
)
})

df = pd.DataFrame(rows)

df = df.sort_values(
    "PowerRating",
    ascending=False
)

df.to_csv("standings.csv", index=False)

print("CSV created successfully!")
print(df[["Team", "PowerRating"]].head(10))