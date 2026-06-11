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
        "World Cup",
        "Premier League"
    ],
    index=0
)

# ==================================================
# WORLD CUP PAGE
# ==================================================

# ==================================================
# WORLD CUP PAGE
# ==================================================

if competition == "World Cup":

    st.title("🌎 FIFA World Cup Analytics")

    # -----------------------
    # LOAD STANDINGS
    # -----------------------

    with st.spinner("Loading World Cup data..."):

        response = (
            supabase
            .table("world_cup_standings")
            .select("*")
            .execute()
        )

        world_df = pd.DataFrame(response.data)

    # -----------------------
    # LOAD MATCHDAY PICKS
    # -----------------------

    matches_response = (
        supabase
        .table("world_cup_matches")
        .select("*")
        .order("match_date")
        .execute()
    )

    matches_df = pd.DataFrame(matches_response.data)

    if len(world_df) == 0:

        st.warning(
            "No World Cup data available."
        )

    else:

        world_df = world_df.sort_values(
            "power_rank"
        )

        # -----------------------
        # TEAM SELECTOR
        # -----------------------

        selected_team = st.selectbox(
            "Choose a World Cup Team",
            sorted(world_df["team"])
        )

        team_data = world_df[
            world_df["team"] == selected_team
        ].iloc[0]

        st.subheader(
            f"📊 {selected_team}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "FIFA Rank",
                int(team_data["fifa_rank"])
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
        # POWER RANKINGS TABLE
        # -----------------------

        st.subheader(
            "World Cup Power Rankings"
        )

        display_df = world_df[
            [
                "power_rank",
                "team",
                "fifa_rank",
                "power_rating"
            ]
        ].sort_values(
            "power_rank"
        )

        st.dataframe(
            display_df,
            use_container_width=True
        )

        # -----------------------
        # TOP 10
        # -----------------------

        st.subheader(
            "Top 10 World Cup Teams"
        )

        st.dataframe(
            display_df.head(10),
            use_container_width=True
        )

        # -----------------------
        # CHART
        # -----------------------

        st.subheader(
            "World Cup Power Rating Chart"
        )

        st.bar_chart(
            world_df.set_index(
                "team"
            )["power_rating"]
        )

        # -----------------------
        # MATCHDAY PICKS
        # -----------------------

        st.subheader(
            "🎯 World Cup Matchday Picks"
        )
        
        if len(picks_df) > 0:

        from datetime import datetime

        today = datetime.utcnow().date()

        matches_df["match_date"] = pd.to_datetime(
            matches_df["match_date"]
        )

        picks_df = matches_df[
            matches_df["match_date"].dt.date == today
        ][
            [
                "home_team",
                "away_team",
                "pick",
                "confidence"
            ]
        ]

            st.dataframe(
                picks_df,
                use_container_width=True
            )

        else:

            st.info(
                "No matchday picks available."
            )

        st.markdown("---")
        st.markdown("**By Raphael Shehata**")

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
