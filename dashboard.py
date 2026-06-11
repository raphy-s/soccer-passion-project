import pandas as pd
import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# -----------------------
# AUTO REFRESH
# -----------------------

st_autorefresh(interval=60000, limit=None, key="refresh")

# -----------------------
# PAGE HEADER
# -----------------------

st.title("⚽ Raphael Shehata Football Analytics")

st.caption(
    "Custom Power Rankings • Matchday Picks • Data Updated Daily"
)

st.caption(
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
# -----------------------
# SUPABASE
# -----------------------

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
# -----------------------
# SIDEBAR
# -----------------------


competition = st.sidebar.selectbox(
    "Competition",
    [
        "🎯 Matchday Picks",
        "🌎 World Cup",
        "🏴 Premier League",
        "📈 World Cup Analytics"
    ],
    index=0
)

# ==================================================
# MATCHDAY PICKS PAGE
# ==================================================

if competition == "🎯 Matchday Picks":

    st.title("🔥 AI Matchday Predictions")

    st.caption(
        "Predictions generated using Elo ratings, FIFA rankings, and tournament performance."
    )

    matches_response = (
        supabase
        .table("world_cup_matches")
        .select("*")
        .order("match_date")
        .execute()
    )

    matches_df = pd.DataFrame(
        matches_response.data
    )

    if len(matches_df) > 0:

        matches_df["match_date"] = pd.to_datetime(
            matches_df["match_date"],
            utc=True
        )

        now = pd.Timestamp.utcnow()

        upcoming_matches = (
            matches_df[
                matches_df["match_date"] >= now
            ]
            .sort_values("match_date")
            .head(12)
        )

        if len(upcoming_matches) > 0:

            for _, match in upcoming_matches.iterrows():

                confidence = match["confidence"]

                if confidence == "Very High":
                    emoji = "🔥"

                elif confidence == "High":
                    emoji = "✅"

                elif confidence == "Medium":
                    emoji = "📊"

                else:
                    emoji = "⚪"

                kickoff = (
                    match["match_date"]
                    .strftime("%b %d • %I:%M %p UTC")
                )

                probability = round(
                    float(match["win_probability"]),
                    1
                )

                st.markdown(
                    f"""
### {emoji} {match['home_team']} vs {match['away_team']}

**Prediction:** {match['pick']}

**Win Probability:** {probability}%

**Confidence:** {match['confidence']}

**Kickoff:** {kickoff}

---
"""
                )

        else:

            st.info(
                "No upcoming matches."
            )

    else:

        st.info(
            "No predictions available."
        )

# ==================================================
# WORLD CUP PAGE
# ==================================================

if competition == "🌎 World Cup":

    st.title("🌎 FIFA World Cup 2026 Analytics")

    with st.spinner("Loading World Cup data..."):

        standings_response = (
            supabase
            .table("world_cup_standings")
            .select("*")
            .execute()
        )

        world_df = pd.DataFrame(
            standings_response.data
        )

    if len(world_df) == 0:

        st.warning(
            "No World Cup data available."
        )

    else:

        world_df = world_df.sort_values(
            "power_rank"
        )

        # =====================================
        # HERO SECTION
        # =====================================

        st.markdown(
            "### Predictive Analytics • Elo Ratings • Power Rankings"
        )

        top_team = world_df.iloc[0]["team"]

        top_elo = int(
            world_df["elo_rating"].max()
        )

        avg_rating = round(
            world_df["power_rating"].mean(),
            2
        )

        total_teams = len(world_df)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "🏆 #1 Team",
                top_team
            )

        with c2:
            st.metric(
                "⚡ Top Elo",
                top_elo
            )

        with c3:
            st.metric(
                "🌍 Teams",
                total_teams
            )

        with c4:
            st.metric(
                "📊 Avg Rating",
                avg_rating
            )

        st.markdown("---")

        # =====================================
        # TEAM EXPLORER
        # =====================================

        st.subheader(
            "🔍 Team Explorer"
        )

        selected_team = st.selectbox(
            "Choose a Team",
            sorted(
                world_df["team"]
            )
        )

        team_data = world_df[
            world_df["team"]
            ==
            selected_team
        ].iloc[0]

        st.markdown(
            f"## {selected_team}"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "FIFA Rank",
                int(team_data["fifa_rank"])
            )

        with c2:
            st.metric(
                "Power Rank",
                int(team_data["power_rank"])
            )

        with c3:
            st.metric(
                "Elo Rating",
                int(team_data["elo_rating"])
            )

        with c4:
            st.metric(
                "Power Rating",
                round(
                    float(
                        team_data["power_rating"]
                    ),
                    2
                )
            )

        st.markdown("---")

        # =====================================
        # TOP 10
        # =====================================

        st.subheader(
            "🏆 Top 10 Teams"
        )

        st.dataframe(
            world_df[
                [
                    "power_rank",
                    "team",
                    "elo_rating",
                    "fifa_rank",
                    "power_rating"
                ]
            ].head(10),
            use_container_width=True
        )

        # =====================================
        # POWER CHART
        # =====================================

        st.subheader(
            "📈 Top 15 Power Ratings"
        )

        chart_df = (
            world_df
            .sort_values(
                "power_rating",
                ascending=False
            )
            .head(15)
        )

        st.bar_chart(
            chart_df.set_index(
                "team"
            )["power_rating"]
        )

        # =====================================
        # ELO CHART
        # =====================================

        st.subheader(
            "⚡ Top 15 Elo Ratings"
        )

        elo_df = (
            world_df
            .sort_values(
                "elo_rating",
                ascending=False
            )
            .head(15)
        )

        st.bar_chart(
            elo_df.set_index(
                "team"
            )["elo_rating"]
        )

        # =====================================
        # FULL TABLE
        # =====================================

        with st.expander(
            "📋 Full Rankings"
        ):

            st.dataframe(
                world_df[
                    [
                        "power_rank",
                        "team",
                        "elo_rating",
                        "fifa_rank",
                        "power_rating"
                    ]
                ],
                use_container_width=True
            )

        st.markdown("---")
        st.markdown(
            "**Built by Raphael Shehata**"
        )

# ==================================================
# PREMIER LEAGUE PAGE
# ==================================================

elif competition == "Premier League":

    # -----------------------
    # SUPABASE
    # -----------------------

    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    # -----------------------
    # LOAD DATA
    # -----------------------

    with st.spinner("Loading latest Premier League data..."):

        response = (
            supabase
            .table("premier_league_standings")
            .select("*")
            .execute()
        )

        df = pd.DataFrame(response.data)

    # -----------------------
    # POWER RANKINGS
    # -----------------------

    power_df = (
        df.sort_values(
            "power_rating",
            ascending=False
        )
        .reset_index(drop=True)
        .copy()
    )

    power_df["power_rank"] = power_df.index + 1

    rank_lookup = dict(
        zip(
            power_df["team"],
            power_df["power_rank"]
        )
    )

    df["power_rank"] = df["team"].map(rank_lookup)

    df["difference"] = (
        df["position"].astype(int)
        -
        df["power_rank"].astype(int)
    )
    # -----------------------
    # FORMULA
    # -----------------------

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

    team_data = df[
        df["team"] == selected_team
    ].iloc[0]

    st.subheader(
        f"📊 {selected_team}"
    )

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
            round(
                float(team_data["power_rating"]),
                2
            )
        )

    # -----------------------
    # TABLE
    # -----------------------

    st.subheader(
        "League Table vs Power Rankings"
    )

    display_df = df[
        [
            "position",
            "power_rank",
            "team",
            "points",
            "power_rating",
            "difference"
        ]
    ].sort_values(
        "position"
    )

    st.dataframe(
        display_df.style.map(
            lambda x:
                "color: green"
                if x > 0
                else "color: red"
                if x < 0
                else "",
            subset=["difference"]
        )
    )

    # -----------------------
    # TOP 10
    # -----------------------

    st.subheader(
        "Top 10 Power Rankings"
    )

    top10 = power_df[
        [
            "power_rank",
            "team",
            "power_rating"
        ]
    ].head(10)

    st.dataframe(top10)

    # -----------------------
    # CHART
    # -----------------------

    st.subheader(
        "Power Rating Chart"
    )

    st.bar_chart(
        power_df.set_index(
            "team"
        )["power_rating"]
    )

    st.markdown("---")
    st.markdown("**By Raphael Shehata**")

elif competition == "World Cup Analytics":

    st.title("📈 World Cup Analytics")

    response = (
        supabase
        .table("world_cup_matches")
        .select("*")
        .execute()
    )

    analytics_df = pd.DataFrame(response.data)

    if len(analytics_df) == 0:

        st.info(
            "No prediction data available."
        )

    else:

        completed = analytics_df[
            analytics_df["correct"].notna()
        ]

        if len(completed) == 0:

            st.info(
                "No completed World Cup matches yet."
            )

        else:

            accuracy = round(
                completed["correct"].mean() * 100,
                1
            )

            st.metric(
                "Overall Accuracy",
                f"{accuracy}%"
            )

            st.subheader(
                "Confidence Breakdown"
            )

            breakdown = (
                completed
                .groupby("confidence")["correct"]
                .mean()
                .reset_index()
            )

            breakdown["correct"] = (
                breakdown["correct"] * 100
            ).round(1)

            st.dataframe(
                breakdown,
                use_container_width=True
            )
