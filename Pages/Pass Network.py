import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import streamlit as st
from mplsoccer import Pitch, FontManager, Sbopen
import streamlit as st
from statsbombpy import sb

events = sb.competitions()

matches = [267569,9924]


st.header('Pass Network for Real Madrid')
st.subheader('Available match data for Real Madrid')
st.dataframe(events.head())
# st.dataframe(events['competition_id'].unique())
evnts = events[['competition_id','competition_name']]
st.dataframe(evnts['competition_name'].unique())
# comps = list(events['competition_id'].unique())
comp = st.selectbox(
    'Select a Competition',
    evnts['competition_name'].unique())

season = st.selectbox(
    'Select a Season',
    events['season_name'].unique())
st.write(comp,season)

select_match = st.selectbox(
    'Select Match',
    matches)
    
if st.button("Generate pass network"):

    parser = Sbopen()
    events, related, freeze, players = parser.event(select_match)
    TEAM = 'Real Madrid'
    OPPONENT = 'versus FC Barcelona, 2016/17 La Liga'

    events.loc[events.tactics_formation.notnull(), 'tactics_id'] = events.loc[
        events.tactics_formation.notnull(), 'id']
    events[['tactics_id', 'tactics_formation']] = events.groupby('team_name')[[
        'tactics_id', 'tactics_formation']].ffill()

    formation_dict = {1: 'Navas', 2: 'Carvajal', 3: 'Nacho', 4: 'CB', 5: 'Ramos', 6: 'Marcelo', 7: 'RWB',
                    8: 'LWB', 9: 'RDM', 10: 'Casemiro', 11: 'LDM', 12: 'RM', 13: 'Modric',
                    14: 'CM', 15: 'Kroos', 16: 'LM', 17: 'Bale', 18: 'RAM', 19: 'CAM',
                    20: 'LAM', 21: 'Ronaldo', 22: 'RCF', 23: 'Benzema', 24: 'LCF', 25: 'SS'}
    players['position_abbreviation'] = players.position_id.map(formation_dict)

    sub = events.loc[events.type_name == 'Substitution',
                    ['tactics_id', 'player_id', 'substitution_replacement_id',
                    'substitution_replacement_name']]
    players_sub = players.merge(sub.rename({'tactics_id': 'id'}, axis='columns'),
                                on=['id', 'player_id'], how='inner', validate='1:1')
    players_sub = (players_sub[['id', 'substitution_replacement_id', 'position_abbreviation']]
                .rename({'substitution_replacement_id': 'player_id'}, axis='columns'))
    players = pd.concat([players, players_sub])
    players.rename({'id': 'tactics_id'}, axis='columns', inplace=True)
    players = players[['tactics_id', 'player_id', 'position_abbreviation']]

    # add on the position the player was playing in the formation to the events dataframe
    events = events.merge(players, on=['tactics_id', 'player_id'], how='left', validate='m:1')
    # add on the position the receipient was playing in the formation to the events dataframe
    events = events.merge(players.rename({'player_id': 'pass_recipient_id'},
                                        axis='columns'), on=['tactics_id', 'pass_recipient_id'],
                        how='left', validate='m:1', suffixes=['', '_receipt'])

    FORMATION = 433
    pass_cols = ['id', 'position_abbreviation', 'position_abbreviation_receipt']
    passes_formation = events.loc[(events.team_name == TEAM) & (events.type_name == 'Pass') &
                                (events.tactics_formation == FORMATION) &
                                (events.position_abbreviation_receipt.notnull()), pass_cols].copy()
    location_cols = ['position_abbreviation', 'x', 'y']
    location_formation = events.loc[(events.team_name == TEAM) &
                                    (events.type_name.isin(['Pass', 'Ball Receipt'])) &
                                    (events.tactics_formation == FORMATION), location_cols].copy()

    # average locations
    average_locs_and_count = (location_formation.groupby('position_abbreviation')
                            .agg({'x': ['mean'], 'y': ['mean', 'count']}))
    average_locs_and_count.columns = ['x', 'y', 'count']

    # calculate the number of passes between each position (using min/ max so we get passes both ways)
    passes_formation['pos_max'] = (passes_formation[['position_abbreviation',
                                                    'position_abbreviation_receipt']]
                                .max(axis='columns'))
    passes_formation['pos_min'] = (passes_formation[['position_abbreviation',
                                                    'position_abbreviation_receipt']]
                                .min(axis='columns'))
    passes_between = passes_formation.groupby(['pos_min', 'pos_max']).id.count().reset_index()
    passes_between.rename({'id': 'pass_count'}, axis='columns', inplace=True)

    # add on the location of each player so we have the start and end positions of the lines
    passes_between = passes_between.merge(average_locs_and_count, left_on='pos_min', right_index=True)
    passes_between = passes_between.merge(average_locs_and_count, left_on='pos_max', right_index=True,
                                        suffixes=['', '_end'])


    MAX_LINE_WIDTH = 18
    MAX_MARKER_SIZE = 3000
    passes_between['width'] = (passes_between.pass_count / passes_between.pass_count.max() *
                            MAX_LINE_WIDTH)
    average_locs_and_count['marker_size'] = (average_locs_and_count['count']
                                            / average_locs_and_count['count'].max() * MAX_MARKER_SIZE)


    MIN_TRANSPARENCY = 0.3
    color = np.array(to_rgba('white'))
    color = np.tile(color, (len(passes_between), 1))
    c_transparency = passes_between.pass_count / passes_between.pass_count.max()
    c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency


    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor("#22312b")
    pass_lines = pitch.lines(passes_between.x, passes_between.y,
                            passes_between.x_end, passes_between.y_end, lw=passes_between.width,
                            color=color, zorder=1, ax=ax)
    pass_nodes = pitch.scatter(average_locs_and_count.x, average_locs_and_count.y,
                            s=average_locs_and_count.marker_size,
                            color='red', edgecolors='black', linewidth=1, alpha=1, ax=ax)
    for index, row in average_locs_and_count.iterrows():
        pitch.annotate(row.name, xy=(row.x, row.y), c='white', va='center',
                    ha='center', size=16, weight='bold', ax=ax)

    st.write(fig)

    # fig, axs = pitch.grid(figheight=10, title_height=0.08, endnote_space=0,
    #                       # Turn off the endnote/title axis. I usually do this after
    #                       # I am happy with the chart layout and text placement
    #                       axis=False,
    #                       title_space=0, grid_height=0.82, endnote_height=0.05)
    # fig.set_facecolor("black")
    # pass_lines = pitch.lines(passes_between.x, passes_between.y,
    #                          passes_between.x_end, passes_between.y_end, lw=passes_between.width,
    #                          color=color, zorder=1, ax=axs['pitch'])
    # pass_nodes = pitch.scatter(average_locs_and_count.x, average_locs_and_count.y,
    #                            s=average_locs_and_count.marker_size,
    #                            color='red', edgecolors='black', linewidth=1, alpha=1, ax=axs['pitch'])
    # for index, row in average_locs_and_count.iterrows():
    #     pitch.annotate(row.name, xy=(row.x, row.y), c='white', va='center',
    #                    ha='center', size=16, weight='bold', ax=axs['pitch'])

    # # Load a custom font.
    # URL = 'https://github.com/google/fonts/blob/main/apache/roboto/Roboto%5Bwdth,wght%5D.ttf?raw=true'
    # robotto_regular = FontManager(URL)

    # # endnote /title
    # axs['endnote'].text(1, 0.5, '', color='#c7d5cc',
    #                     va='center', ha='right', fontsize=15,
    #                     fontproperties=robotto_regular.prop)
    # TITLE_TEXT = f'{TEAM}, {FORMATION} formation'
    # axs['title'].text(0.5, 0.7, TITLE_TEXT, color='#c7d5cc',
    #                   va='center', ha='center', fontproperties=robotto_regular.prop, fontsize=30)
    # axs['title'].text(0.5, 0.25, OPPONENT, color='#c7d5cc',
    #                   va='center', ha='center', fontproperties=robotto_regular.prop, fontsize=18)

    # # sphinx_gallery_thumbnail_path = 'gallery/pitch_plots/images/sphx_glr_plot_pass_network_002.png'

    # plt.show()  # If you are using a Jupyter notebook you do not need this line
    # fig.savefig('pass_network_rma.jpg',dpi=1200)

