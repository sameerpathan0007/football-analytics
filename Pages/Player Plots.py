# import streamlit as st

# st.set_page_config(
#     page_title = "Player Plots",
#     page_icon = "📊"
# )

import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt

stats_df = pd.read_csv('D:/University of Leeds/MSc Project/Player Recommendation System/data/player_stats.csv')
npxg = stats_df['Player']

# st.table(npxg.head())


# def read_data():
#     stats_df = pd.read_csv('D:/University of Leeds/MSc Project/Player Recommendation System/data/player_stats.csv')
#     npxg = stats_df['Player']

#     return npxg.head()

# stats_df = read_data()

# st.markdown("<h1 style='text-align: center'>Player Performances</h1>", unsafe_allow_html=True)
# st.markdown('Player suggestion method for the top five European Leagues that produces the most comparable players for a specific player based on numerous characteristics from the 17–18 to the 21–22 season.')


def get_list(df,col):
    items = df[col].unique()
    items = np.insert(items,0,'All')
    return items


seasons = get_list(stats_df,'Season')
leagues = get_list(stats_df,'Season')
positions = get_list(stats_df,'Season')
players = stats_df['Player']


# @st.cache(show_spinner=False)
def create_dict(df, items):
    return [dict(zip(df['Player'], df[item])) for item in items]

cols = ['Season', 'Pos', 'Squad', 'Comp', 'Age', 'Foot']
player_mappings = create_dict(stats_df, cols)
select_player = st.sidebar.selectbox(
    'Select Player',
    players)

player_team = player_mappings[2][select_player]
print(player_team)

player_tt = list(player_team)

# st.table(player_tt)
# select_season = st.sidebar.selectbox(
#     'Select Season',
#     seasons
# )

# select_pos = st.sidebar.selectbox(
#     'Compare With Position: ',
#     positions
# )