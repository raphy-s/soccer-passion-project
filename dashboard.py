import pandas as pd
import streamlit as st

# Load data
df = pd.read_csv("standings.csv")

# Create power ranking order
power_df = df.sort_values(
    "PowerRating",
    ascending=False
).reset_index(drop=True)

power_df["PowerRank"] = power_df.index + 1

# Merge power rank back into main table
df = df.merge(
    power_df[["Team", "PowerRank"]],
    on="Team"
)

# Difference metric
df["Difference"] = df["Position"] - df["PowerRank"]

# Display
st.title("⚽ Premier League Analytics Dashboard")

st.markdown("""
### Power Rating Formula

Power Rating =
2 × Points Per Game
+ Goals For Per Game
− Goals Against Per Game
+ 0.5 × Goal Difference Per Game

This rating rewards winning, attacking strength,
defensive strength, and overall dominance.
""")
selected_team = st.selectbox(
    "Choose a Team",
    sorted(df["Team"])
)
team_data = df[df["Team"] == selected_team].iloc[0]
st.subheader(f"📊 {selected_team}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "League Position",
        int(team_data["Position"])
    )

with col2:
    st.metric(
        "Power Rank",
        int(team_data["PowerRank"])
    )

with col3:
    st.metric(
        "Power Rating",
        round(team_data["PowerRating"], 2)
    )

st.subheader("League Table vs Power Rankings")

display_df = df[
    [
        "Position",
        "PowerRank",
        "Team",
        "Points",
        "PowerRating",
        "Difference"
    ]
].sort_values("Position")

st.dataframe(
    display_df.style.map(
        lambda x:
            "color: green" if x > 0
            else "color: red" if x < 0
            else "",
        subset=["Difference"]
    )
)

st.subheader("Top 10 Power Rankings")

top10 = power_df[
    ["PowerRank", "Team", "PowerRating"]
].head(10)

st.dataframe(top10)

st.subheader("Power Rating Chart")

st.bar_chart(
    power_df.set_index("Team")["PowerRating"]
)