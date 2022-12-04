# Animate shots as it happened one by one.


# Data Handling & Analysis
import datetime

import numpy as np
import pandas as pd

# Data Visualisation
import matplotlib.pyplot as plt
import matplotlib.image as image

# Web Scraping
import json
import requests

from bs4 import BeautifulSoup

import streamlit as st
from highlight_text import fig_text

st.header('Match Summary')

def scrape_script_data(match_id):
    """Web scrape the match info and return the Beautiful object and a dictionary for the home and away team's data."""
    url = 'https://understat.com/match/{}'.format(match_id)

    response = requests.get(url)
    soup_object = BeautifulSoup(response.content, 'lxml')

    # Retrieve all data with a <script> tag - Field data are in the second <script> group
    script_data = soup_object.find_all('script')
    field_stats = script_data[1].string

    # Strip unnecessary symbols and get only JSON data
    ind_start = field_stats.index("('") + 2
    ind_end = field_stats.index("')")

    json_data = field_stats[ind_start:ind_end]
    json_data = json_data.encode('utf8').decode('unicode_escape')

    # Convert string to json format
    data_dict = json.loads(json_data)

    return soup_object, data_dict


def extract_date(data_dict):
    """Return the date of the football match (Format: Day - Name of Month - Year)."""
    date = data_dict['h'][0]['date'].split()[0]
    date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    return date.strftime('%d %B %Y')


def extract_summary_stats(soup_object):
    """Return the game's summary statistics in a separate Pandas DataFrame."""
    table = soup_object.find('div', {'class': 'scheme-block', 'data-scheme': 'stats'})

    cols = [val.text for val in table.find_all('div', {'class': 'progress-title'})]
    vals = [val.text for val in table.find_all('div', {'class': 'progress-value'})]

    summary_dict = {}
    j = 0
    for i in range(len(cols)):
        summary_dict[cols[i]] = vals[j:j + 2]

        increment = 3 if i == 1 else 2
        j += increment

    df_summary = pd.DataFrame(summary_dict, index=['Home', 'Away']).T
    df_summary.drop(['CHANCES'], inplace=True)
    df_summary.index = ['Teams', 'Goals', 'xG',
                        'Shots', 'On Target', 'DEEP', 'PPDA', 'xPTS']

    return df_summary


def extract_headline(df_summary):
    """Return the headline of the figure."""
    headline = '{} {} - {} {}'.format(
        df_summary.loc['Teams', 'Home'],
        df_summary.loc['Goals', 'Home'],
        df_summary.loc['Goals', 'Away'],
        df_summary.loc['Teams', 'Away'])

    return headline


def extract_team_names(df_summary):
    """Return a shortened version of the team names (e.g. 'Manchester United' to 'Man. United').
    Also, pad right & left with spaces so that all short names have the same length (11 characters).
    """
    teams_full = [
        'Manchester City', 'Liverpool', 'Chelsea', 'Arsenal', 'West Ham',
        'Tottenham', 'Manchester United', 'Wolverhampton Wanderers', 'Brighton',
        'Leicester', 'Crystal Palace', 'Brentford', 'Aston Villa', 'Southampton',
        'Everton', 'Leeds', 'Watford', 'Burnley', 'Newcastle United', 'Norwich']

    teams_short = [
        'Man. City', 'Liverpool', 'Chelsea', 'Arsenal', 'West Ham', 'Tottenham',
        'Man. United', 'Wolves', 'Brighton', 'Leicester', 'Cr. Palace',
        'Brentford', 'Aston Villa', 'Southampton', 'Everton', 'Leeds', 'Watford',
        'Burnley', 'Newcastle', 'Norwich']

    # Pad right & left so that all short names have the same length
    teams_short = [f'{string:^11}' for string in teams_short]

    idx = [i for i, v in enumerate(teams_full) if v == df_summary.loc['Teams', 'Home']]
    home_team_short = teams_short[idx[0]]

    idx = [i for i, v in enumerate(teams_full) if v == df_summary.loc['Teams', 'Away']]
    away_team_short = teams_short[idx[0]]

    return home_team_short, away_team_short


# def get_crest_img(df_summary):
#     """Return the crests for both teams."""
#     url_home = 'Crests\{}.png'.format(df_summary.loc['Teams', 'Home'])
#     img_home = image.imread(url_home)

#     url_away = 'Crests\{}.png'.format(df_summary.loc['Teams', 'Away'])
#     img_away = image.imread(url_away)

#     return img_home, img_away



import numpy as np
import matplotlib.pyplot as plt

from matplotlib.patches import Arc


def draw_pitch(x_min=0,
               x_max=105,
               y_min=0,
               y_max=68,
               pitch_color='w',
               line_color='grey',
               line_thickness=1.5,
               point_size=20,
               orientation='horizontal',
               aspect='full',
               ax=None):

    if not ax:
        raise TypeError('This function is intended to be used with an existing fig and ax in order to allow flexibility in plotting of various sizes and in subplots.')

    if orientation.lower().startswith('h'):
        first = 0
        second = 1
        arc_angle = 0

        if aspect == 'half':
            ax.set_xlim(x_max / 2, x_max + 5)

    elif orientation.lower().startswith('v'):
        first = 1
        second = 0
        arc_angle = 90

        if aspect == 'half':
            ax.set_ylim(x_max / 2, x_max + 5)

    else:
        raise NameError('You must choose one of horizontal or vertical')

    ax.axis('off')

    rect = plt.Rectangle((x_min, y_min),
                         x_max,
                         y_max,
                         facecolor=pitch_color,
                         edgecolor='none',
                         zorder=-2)

    ax.add_artist(rect)

    x_conversion = x_max / 100
    y_conversion = y_max / 100

    pitch_x = [0, 5.8, 11.5, 17, 50, 83, 88.5, 94.2, 100]  # pitch x markings
    pitch_x = [x * x_conversion for x in pitch_x]

    pitch_y = [0, 21.1, 36.6, 50, 63.2, 78.9, 100]  # pitch y markings
    pitch_y = [x * y_conversion for x in pitch_y]

    goal_y = [45.2, 54.8]  # goal posts
    goal_y = [x * y_conversion for x in goal_y]

    # side and goal lines
    lx1 = [x_min, x_max, x_max, x_min, x_min]
    ly1 = [y_min, y_min, y_max, y_max, y_min]

    # outer boxed
    lx2 = [x_max, pitch_x[5], pitch_x[5], x_max]
    ly2 = [pitch_y[1], pitch_y[1], pitch_y[5], pitch_y[5]]

    lx3 = [0, pitch_x[3], pitch_x[3], 0]
    ly3 = [pitch_y[1], pitch_y[1], pitch_y[5], pitch_y[5]]

    # goals
    lx4 = [x_max, x_max + 2, x_max + 2, x_max]
    ly4 = [goal_y[0], goal_y[0], goal_y[1], goal_y[1]]

    lx5 = [0, -2, -2, 0]
    ly5 = [goal_y[0], goal_y[0], goal_y[1], goal_y[1]]

    # 6 yard boxes
    lx6 = [x_max, pitch_x[7], pitch_x[7], x_max]
    ly6 = [pitch_y[2], pitch_y[2], pitch_y[4], pitch_y[4]]

    lx7 = [0, pitch_x[1], pitch_x[1], 0]
    ly7 = [pitch_y[2], pitch_y[2], pitch_y[4], pitch_y[4]]

    # Halfway line, penalty spots, and kickoff spot
    lx8 = [pitch_x[4], pitch_x[4]]
    ly8 = [0, y_max]

    lines = [
        [lx1, ly1],
        [lx2, ly2],
        [lx3, ly3],
        [lx4, ly4],
        [lx5, ly5],
        [lx6, ly6],
        [lx7, ly7],
        [lx8, ly8],
    ]

    points = [[pitch_x[4], pitch_y[3]]]

    circle_points = [pitch_x[4], pitch_y[3]]
    arc_points1 = [pitch_x[6], pitch_y[3]]
    arc_points2 = [pitch_x[2], pitch_y[3]]

    for line in lines:
        ax.plot(line[first],
                line[second],
                color=line_color,
                lw=line_thickness,
                zorder=-1)

    for point in points:
        ax.scatter(point[first],
                   point[second],
                   color=line_color,
                   s=point_size,
                   zorder=-1)

    circle = plt.Circle((circle_points[first], circle_points[second]),
                        x_max * 0.088,
                        lw=line_thickness,
                        color=line_color,
                        fill=False,
                        zorder=-1)

    ax.add_artist(circle)

    arc1 = Arc((arc_points1[first], arc_points1[second]),
               height=x_max * 0.088 * 2,
               width=x_max * 0.088 * 2,
               angle=arc_angle,
               theta1=128.75,
               theta2=231.25,
               color=line_color,
               lw=line_thickness,
               zorder=-1)

    ax.add_artist(arc1)

    arc2 = Arc((arc_points2[first], arc_points2[second]),
               height=x_max * 0.088 * 2,
               width=x_max * 0.088 * 2,
               angle=arc_angle,
               theta1=308.75,
               theta2=51.25,
               color=line_color,
               lw=line_thickness,
               zorder=-1)

    ax.add_artist(arc2)

    ax.set_aspect('equal')

    return ax

# Data Handling & Analysis
import datetime

import numpy as np
import pandas as pd

# Data Visualisation
import matplotlib.pyplot as plt
import matplotlib.image as image

from matplotlib.patches import Arc
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

# Web Scraping
import json
import requests

from bs4 import BeautifulSoup

# # Custom functions for extracting match info
# import match_scraper

# # Custom function for drawing a football pitch
# from draw_football_pitch import draw_pitch


def create_figure(match_id, fig, ax):
    """Add the figure to the given axes object."""
    soup_object, data_dict = scrape_script_data(match_id)

    df_summary = extract_summary_stats(soup_object)

    date = extract_date(data_dict)
    headline = extract_headline(df_summary)

#     home_team, away_team = extract_team_names(df_summary)
    # crest_home, crest_away = get_crest_img(df_summary)

    df_home = pd.DataFrame(data_dict['h'])
    df_away = pd.DataFrame(data_dict['a'])

    # Convert numeric columns to floats
    float_cols = ['X', 'Y', 'xG']
    for df in [df_home, df_away]:
        df[float_cols] = df[float_cols].astype('float64')

    # Isolate goals and shot data for both teams
    goals_home = df_home[df_home['result'] == 'Goal']
    shots_home = df_home[df_home['result'] != 'Goal']

    goals_away = df_away[df_away['result'] == 'Goal']
    shots_away = df_away[df_away['result'] != 'Goal']

    bg_color = '#0f253a'
    goal_color = 'red'
    edgecolor = 'white'
    plt.rcParams['text.color'] = 'white'

    plt.rcParams['font.family'] = 'Century Gothic'
    plt.rcParams.update({'font.size': 24})

    fig.patch.set_facecolor(bg_color)
    draw_pitch(pitch_color=bg_color, line_color='lightgrey', ax=ax)

    ### 01 - Shots and Goals ###
    for i, df in enumerate([shots_home, goals_home]):
        ax.scatter(x=105 - df['X'] * 105,
                   y=68 - df['Y'] * 68,
                   s=df['xG'] * 1024,
                   lw=[2, 1][i],
                   alpha=0.7,
                   facecolor=['none', goal_color][i],
                   edgecolor=edgecolor)

    for i, df in enumerate([shots_away, goals_away]):
        ax.scatter(x=df['X'] * 105,
                   y=df['Y'] * 68,
                   s=df['xG'] * 1024,
                   lw=[2, 1][i],
                   alpha=0.7,
                   facecolor=['none', goal_color][i],
                   edgecolor=edgecolor)

    ### 02 - Title & Subtitle ###
    ax.text(x=20, y=75, s=headline, size=35, weight='bold')
    ax.text(x=20, y=71, s='Premier League 2021-22  |  {}'.format(date), size=20)

    ### 03 - Team Names ###
#     for i, team in zip([-1, 1], [home_team, away_team]):
#         ax.text(x=105 / 2 + i * 14,
#                 y=63,
#                 s=team,
#                 size=35,
#                 ha='center',
#                 weight='bold')

    ### 04 - Team Logos ###
    # for i, img in zip([-1, 1], [crest_home, crest_away]):

    #     imagebox = OffsetImage(img, zoom=0.6)
    #     ab = AnnotationBbox(imagebox, (105 / 2 + i * 14, 60), frameon=False)
    #     ax.add_artist(ab)

    ### 05 - Stats ###
    features = ['Goals', 'xG', 'Shots', 'On Target', 'DEEP', 'xPTS']
    for i, feature in enumerate(features):
        if float(df_summary.loc[feature, 'Home']) > float(df_summary.loc[feature, 'Away']):
            weights = ['bold', 'normal']
        elif float(df_summary.loc[feature, 'Home']) < float(df_summary.loc[feature, 'Away']):
            weights = ['normal', 'bold']
        else:
            weights = ['normal', 'normal']

        ax.text(x=105 / 2,
                y=46 - i * 8,
                s=feature,
                size=22,
                ha='center',
                va='center',
                bbox=dict(facecolor='yellow',
                          edgecolor=edgecolor,
                          alpha=0.85,
                          pad=0.6,
                          boxstyle='round'))

        ax.text(x=105 / 2 - 14,
                y=46 - i * 8,
                s=df_summary.loc[feature, 'Home'],
                size=20,
                ha='center',
                va='center',
                weight=weights[0],
                bbox=dict(facecolor='white',
                          edgecolor='w',
                          alpha=0.6,
                          pad=0.6,
                          boxstyle='round'))

        ax.text(x=105 / 2 + 14,
                y=46 - i * 8,
                s=df_summary.loc[feature, 'Away'],
                size=20,
                ha='center',
                va='center',
                weight=weights[1],
                bbox=dict(facecolor='firebrick',
                          edgecolor='w',
                          alpha=0.6,
                          pad=0.6,
                          boxstyle='round'))

    ### 06 - Legend - Outcome ###
    ax.text(x=105 / 4 + 0, y=-5, s='Outcome:', ha='center')
    ax.text(x=105 / 4 - 8, y=-10, s='Shot', ha='center')
    ax.text(x=105 / 4 + 8, y=-10, s='Goal', ha='center')

    for i in range(2):
        ax.scatter(x=[105 / 4 - 14, 105 / 4 + 1.5][i],
                   y=-8.8,
                   s=500,
                   lw=[2, 1][i],
                   alpha=0.7,
                   facecolor=[bg_color, goal_color][i],
                   edgecolor=edgecolor)

    ### 07 - Legend - xG value ###
    ax.text(x=3 * 105 / 4, y=-5, s='xG Value:', ha='center')

    for i in range(0, 5):
        ax.scatter(x=[69.8, 73.4, 77.7, 82.4, 87.5][i],
                   y=-8.5,
                   s=((i + 1) * 0.2) * 500,
                   lw=2,
                   color=bg_color,
                   edgecolor=edgecolor)

    ### 08 - Legend - Credit ###
    credit_text = 'Data: Understat | Sameer Pathan'
    ax.text(x=105, y=-14, s=credit_text, size=16, ha='right')
    st.write(fig)

match_id = st.text_input('Enter the match ID')

fig, ax = plt.subplots(figsize=(18.48, 12))

if st.button('Match Summary'):
    create_figure(match_id, fig, ax)


def xg_timeline(match_id):
    link = f"https://understat.com/match/{match_id}"
    res = requests.get(link)
    soup = BeautifulSoup(res.content,'lxml')
    scripts = soup.find_all('script')

    # Get the shotsData, it's the second script executed in order
    strings = scripts[1].string 

    # Getting rid of unnecessary characters from json data
    ind_start = strings.index("('")+2 
    ind_end = strings.index("')") 
    json_data = strings[ind_start:ind_end] 
    json_data = json_data.encode('utf8').decode('unicode_escape')
    shots_match = json.loads(json_data)


    # Creatinf the 2 dfs

    df_away = pd.DataFrame(shots_match['a'])
    df_home = pd.DataFrame(shots_match['h'])

    # Selecting only the useful columns

    df_away = df_away[['minute','player',"a_team",'result','xG','h_a']]
    df_home = df_home[['minute','player',"h_team",'result','xG','h_a']]

    # Renaming columns 

    df_away.rename(columns={"a_team": "team"})
    df_home.rename(columns={"h_team": "team"})

    # Changing data types

    df_away = df_away.astype({"xG": float, "minute": float})
    df_home = df_home.astype({"xG": float, "minute": float})

    # Creating new column xG cumulative
    df_away['xGcum'] = np.cumsum(df_away['xG'])
    df_home['xGcum'] = np.cumsum(df_home['xG'])

    # creating the dictionaries
    x = df_home[df_home['result']=='Goal']['minute'].tolist()
    x1 = df_away[df_away['result']=='Goal']['minute'].tolist()
    y =df_home[df_home['result']=='Goal']['xGcum'].tolist()
    y1 = df_away[df_away['result']=='Goal']['xGcum'].tolist()

    # xG inside the scatterplots
    y_plot =np.round(df_home[df_home['result']=='Goal']['xG'],2).tolist()
    y1_plot = np.round(df_away[df_away['result']=='Goal']['xG'],2).tolist()

    # Annotation text
    text_home = df_home[df_home['result']=='Goal']['player'].tolist()
    text_away = df_away[df_away['result']=='Goal']['player'].tolist()
    label_home = df_home['h_team'].unique().tolist()
    label_away = df_away['a_team'].unique().tolist()

    # More annotation text
    xGcum_away = str(np.round(df_away['xGcum'].iloc[-1],3))
    xGcum_home = str(np.round(df_home['xGcum'].iloc[-1],3))
    team_away = str(df_away['a_team'].iloc[-1])
    team_home = str(df_home['h_team'].iloc[-1])


    # plot style 
    plt.style.use('fivethirtyeight')
    fig,ax = plt.subplots(figsize = (16,8))

    # Step plot for Inter and Udinese 
    ax.step(x = df_home['minute'] ,y = df_home['xGcum'] , where = 'post', color = 'cyan' ,linewidth = 4.0)
    ax.step(x = df_away['minute'] ,y = df_away['xGcum'] , where = 'post', color = 'red' ,linewidth = 4.0)

    #sns.scatterplot(x=x,y=y,s=430,marker='o',color='yellow')
    ax.scatter(x=x,y=y, color='cyan', edgecolor='black',s=955, label="Inter",linewidths=1.5,)
    ax.scatter(x=x1,y=y1, color='red', edgecolor='black',s=955, label="Udinese",linewidths=1.5)

    #FILL AREA BETWEEN LINE AND X 
    plt.fill_between(x,y, alpha=0.08, color='cyan')
    plt.fill_between(x1,y1, alpha=0.08, color='red')

    # Text annotation for goals
    for i in range(len(x1)):
        plt.annotate(text_away[i], (x1[i]- 3, y1[i] + 0.26),c='black',size=13)
    for i in range(len(x)):
        plt.annotate(text_home[i], (x[i]- 3, y[i] + 0.26),c='black',size=13)

    # legend
    legend = ax.legend(loc="upper center",prop={'weight':'bold'})
    legend.legendHandles[0]._sizes = [1000]
    legend.legendHandles[1]._sizes = [1000]

    # title
    fig_text(0.08,1.03, s="xG Flowchart Calcio Serie A\n", fontsize = 25, fontweight = "light")
    fig_text(0.08,0.97, s=" <{} {} xG> vs <{} {} xG>".format(team_home,xGcum_home,team_away,xGcum_away),highlight_textprops=[{"color":'cyan'}, {'color':"red"}], fontsize = 20, fontweight="light")

    # text
    fig_text(0.5,0.01, s="Minute\n", fontsize = 24, fontweight = "bold", color = "black")
    fig_text(0.01,0.6, s="xG\n", fontsize = 24, fontweight = "bold", color = "black",rotation=90)
    fig_text(0.25,0.9, s="First Half\n", fontsize = 18, fontweight = "bold", color = "black")
    fig_text(0.75,0.9, s="Second Half\n", fontsize = 18, fontweight = "bold", color = "black")

    # Finally a dotted line to separate the HT 
    plt.vlines( ymin=0, ymax=4,x=45, color='black', alpha=0.1,linestyle="solid")
    # ticks
    plt.xticks([0,15,30,45,60,75,90])
    plt.yticks([0,0.5,1,1.5,2,2.5,3,3.5,4])

    # Annotate quality chances inside the scatterplots

    # Home team
    for i in range(len(x)):
        plt.annotate(y_plot[i], (x[i], y[i]),c='black',size=12,ha='center',va='center',fontweight='bold')
    # Away team
    for i in range(len(x1)):
        plt.annotate(y1_plot[i], (x1[i], y1[i]),c='black',size=12,ha='center',va='center',fontweight='bold')

    st.write(fig)

if st.button('xG Timeline'):
    xg_timeline(match_id)
