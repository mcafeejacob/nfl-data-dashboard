import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import nfl_data_py as nfl
import numpy as np

# --- CONFIG ---
st.set_page_config(page_title="NFL Dashboard", layout="wide")
orange = '#ffb100'
mpl.rcParams['axes.edgecolor'] = 'white'
mpl.rcParams['xtick.color'] = 'black'
mpl.rcParams['ytick.color'] = 'black'
mpl.rcParams['axes.labelcolor'] = 'black'
mpl.rcParams['text.color'] = 'black'

# --- THRESHOLDS (rounded with .5 endings) ---
def half_steps(lst):
    return [x - 0.5 for x in lst]

common_receiving_thresholds = half_steps([10, 30, 50, 70, 100])
threshold_breakdowns = {
    "completions": half_steps([15, 20, 25, 30, 35]),
    "attempts": half_steps([20, 25, 30, 35, 40]),
    "passing_yards": half_steps([150, 200, 250, 300, 350]),
    "passing_tds": half_steps([1, 2, 3, 4, 5]),
    "interceptions": half_steps([1, 2, 3, 4, 5]),
    "carries": half_steps([1, 2, 5, 8, 10]),
    "rushing_yards": common_receiving_thresholds,
    "rushing_tds": half_steps([1, 2, 3, 4, 5]),
    "receptions": half_steps([1, 3, 5, 7, 10]),
    "targets": half_steps([1, 3, 5, 7, 10]),
    "receiving_yards": common_receiving_thresholds,
    "receiving_tds": half_steps([1, 2, 3, 4, 5]),
    "receiving_fumbles": half_steps([1, 2, 3]),
    "fantasy_points": half_steps([10, 15, 20, 25, 30]),
    "fantasy_points_ppr": half_steps([10, 15, 20, 25, 30]),
}

@st.cache_data
def load_data():
    return nfl.import_weekly_data(years=[2024])

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔍 Filters")
allowed_positions = ["QB", "RB", "WR", "TE"]
selected_position = st.sidebar.selectbox("Select Position", allowed_positions)

position_df = df[df["position"] == selected_position]
player_names = sorted(position_df["player_display_name"].dropna().unique())
selected_player = st.sidebar.selectbox("Select Player", player_names)

# --- PLAYER DATA FILTERING ---
player_df = position_df[position_df["player_display_name"] == selected_player].copy()
player_df["week_opponent"] = player_df["week"].astype(str) + " vs " + player_df["opponent_team"]
player_df.sort_values(by="week", inplace=True)
player_info = player_df.iloc[0]

# --- LEAGUE AVERAGE ---
if selected_position == "QB":
    top_qbs = df[df["position"] == "QB"].groupby("player_display_name")["passing_yards"].sum().nlargest(32).index
    league_df = df[df["player_display_name"].isin(top_qbs)]
    league_avg = league_df.groupby("week")[list(threshold_breakdowns.keys())].mean()
else:
    league_avg = df[df["position"] == selected_position].groupby("week")[list(threshold_breakdowns.keys())].mean()

# --- POSITION-BASED STATS ---
if selected_position == "QB":
    stats = {
        "Completions": "completions",
        "Attempts": "attempts",
        "Passing Yards": "passing_yards",
        "Passing TDs": "passing_tds",
        "Interceptions": "interceptions",
        "Carries": "carries",
        "Rushing Yards": "rushing_yards",
        "Rushing TDs": "rushing_tds",
        "Fantasy Points": "fantasy_points",
        "Fantasy Points (PPR)": "fantasy_points_ppr"
    }
elif selected_position == "RB":
    stats = {
        "Carries": "carries",
        "Rushing Yards": "rushing_yards",
        "Rushing TDs": "rushing_tds",
        "Receptions": "receptions",
        "Targets": "targets",
        "Receiving Yards": "receiving_yards",
        "Receiving TDs": "receiving_tds",
        "Fantasy Points": "fantasy_points",
        "Fantasy Points (PPR)": "fantasy_points_ppr"
    }
else:  # WR or TE
    stats = {
        "Receptions": "receptions",
        "Targets": "targets",
        "Receiving Yards": "receiving_yards",
        "Receiving TDs": "receiving_tds",
        "Receiving Fumbles": "receiving_fumbles",
        "Fantasy Points": "fantasy_points",
        "Fantasy Points (PPR)": "fantasy_points_ppr"
    }

# --- PLAYER HEADER ---
st.title(f"{selected_player} - {player_info['recent_team']} ({selected_position})")
col1, col2 = st.columns([1, 3])
with col1:
    st.image(player_info["headshot_url"], width=150)
with col2:
    st.markdown("### Season Totals")
    total_cols = [v for v in stats.values() if v in player_df.columns]
    totals = player_df[total_cols].sum(numeric_only=True).astype(int)
    st.dataframe(totals.to_frame("Total").T.style.format("{:,}"), use_container_width=True)

# --- CHARTS ---
st.markdown("## Weekly Performance Charts")
for label, col in stats.items():
    if col not in player_df.columns:
        continue

    st.markdown(f"### {label}")
    row = st.columns([2, 1, 1])

    with row[0]:
        y = player_df[col].fillna(0)
        x = player_df["week_opponent"]

        avg_all = y.mean()
        avg_last3 = y.tail(3).mean()

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x, y, color=orange)
        ax.axhline(avg_all, color='gray', linestyle='--', linewidth=1, label='Season Avg')
        ax.axhline(avg_last3, color='red', linestyle='--', linewidth=1, label='Last 3 Avg')

        if col in league_avg.columns:
            league_y = league_avg[col].reindex(player_df['week']).values
            ax.plot(x, league_y, linestyle='dashed', color='blue', label='League Avg')

        ax.set_title(f"{label} per Game", fontsize=14)
        ax.set_ylabel(label)
        ax.set_xlabel("Week vs Opponent")
        ax.tick_params(axis='x', rotation=45)
        ax.legend()
        st.pyplot(fig)

    with row[1]:
        stat_series = y
        st.markdown("#### Stat Summary")
        st.write(f"**High:** {stat_series.max():.1f}")
        st.write(f"**Low:** {stat_series.min():.1f}")
        st.write(f"**Average:** {stat_series.mean():.1f}")
        st.write(f"**Avg (Last 3):** {stat_series.tail(3).mean():.1f}")
        st.write(f"**Avg (Last 5):** {stat_series.tail(5).mean():.1f}")
        st.write(f"**Std Dev:** {stat_series.std():.2f}")

        threshold = st.number_input(f"Custom Threshold for {label}", min_value=0.0, step=1.0, key=col)
        if threshold > 0:
            pct = (stat_series > threshold).mean() * 100
            st.success(f"{pct:.1f}% of games over {threshold}")

    with row[2]:
        st.markdown("#### Breakdown")
        for t in threshold_breakdowns.get(col, []):
            pct = (y > t).mean() * 100
            st.write(f"Over {t}: {pct:.1f}%")

# --- GAME LOG CLEANING ---
remove_cols = ['player_id', 'player_name', 'player_display_name', 'position_group', 'headshot_url', 'week_opponent']
cols = [c for c in player_df.columns if c not in remove_cols]
reorder = ['season_type', 'season', 'week', 'opponent_team'] + [c for c in cols if c not in ['season_type', 'season', 'week', 'opponent_team']]
st.markdown("## Game Log")
st.dataframe(player_df[reorder], use_container_width=True)