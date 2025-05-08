# NFL Player Performance Dashboard

This Streamlit app provides an interactive dashboard for analyzing NFL player performance by position (QB, RB, WR, TE). Users can select a player to view weekly game logs, season totals, and dynamic visualizations with league-average comparisons and custom stat thresholds.

## Features

- Position-aware stat filters (QB, RB, WR, TE)
- Interactive weekly bar charts with:
  - Season and 3-game rolling averages
  - League-average overlays (top 32 QBs)
  - Custom threshold inputs
  - Breakdown of percentage of games over user-defined values
- Season totals that dynamically adjust by position
- Cleaned and sortable game log with relevant metadata
- Fast, responsive interface built with Streamlit

## Tech Stack

- Python
- Streamlit
- nfl_data_py
- pandas
- matplotlib

## Installation

Clone the repository and install the required packages:

```bash
git clone https://github.com/your-username/nfl-dashboard.git
cd nfl-dashboard
pip install -r requirements.txt
