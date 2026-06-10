import pandas as pd
import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

st_autorefresh(interval=60000, limit=None, key="refresh")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# -----------------------
# SUPABASE CONNECTION
# -----------------------
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
API_KEY = st.secrets["FOOTBALL_API_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

with st.spinner("Loading latest Premier League data..."):
    response = supabase.table("premier_league_standings").select("*").execute()
    df = pd.DataFrame(response.data)

# -----------------------
# POWER RANKING
# -----------------------
power_df = df.sort_values(
    "power_rating",
    ascending=False
).reset_index(drop=True)

power_df["power_rank"] = power_df.index + 1

# Merge power rank back into main table
df = df.merge(
    power_df[["team", "power_rank"]],
    on="team"
)

# Difference metric
df = df.merge(
    power_df[["team", "power_rank"]],
    on="team"
)

df["difference"] = df["position"] - df["power_rank"]

# -----------------------
# UI
# -----------------------
st.title("⚽ Premier League Power Rankings Dashboard")

st.markdown("""
### Power Rating Formula

Power Rating =
2 × Points Per Game
+ Goals For Per Game
− Goals Against Per Game
+ 0.5 × Goal Difference Per Game

This rewards winning, attacking strength,
defensive strength, and overall dominance.
""")

# -----------------------
# TEAM SELECTOR
# -----------------------
selected_team = st.selectbox(
    "Choose a Team",
    sorted(df["team"])
)

team_data = df[df["team"] == selected_team].iloc[0]

st.subheader(f"📊 {selected_team}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "League Position",
        int(team_data["position"])
    )

with col2:
    st.metric(
        "Power Rank",
        int(team_data["power_rank"])
    )

with col3:
    st.metric(
        "Power Rating",
        round(team_data["power_rating"], 2)
    )

# -----------------------
# TABLE COMPARISON
# -----------------------
st.subheader("League Table vs Power Rankings")

display_df = df[
    [
        "position",
        "power_rank",
        "team",
        "points",
        "power_rating",
        "difference"
    ]
].sort_values("position")

st.dataframe(
    display_df.style.map(
        lambda x:
            "color: green" if x > 0
            else "color: red" if x < 0
            else "",
        subset=["difference"]
    )
)

# -----------------------
# TOP 10 POWER RANKINGS
# -----------------------
st.subheader("Top 10 Power Rankings")

top10 = power_df[
    ["power_rank", "team", "power_rating"]
].head(10)

st.dataframe(top10)

# -----------------------
# CHART
# -----------------------
st.subheader("Power Rating Chart")

st.bar_chart(
    power_df.set_index("team")["power_rating"]
)
st.markdown("---")
st.markdown("**By Raphael Shehata**")
competition = st.sidebar.selectbox(
    "Competition",
    ["Premier League", "World Cup"]
)

st.write(f"Viewing: {competition}")

