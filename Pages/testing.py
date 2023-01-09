import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import streamlit as st
import json
import requests

from bs4 import BeautifulSoup
np.random.seed(42)

fig, ax = plt.subplots()
ax.scatter(*np.random.random((2, 26)))
ax.set_title("Mouse over a point")

mplcursors.cursor(hover=True)

plt.show()


st.write("Testing code")




# url = 'https://understat.com/match/{}'.format(match_id)
url = 'https://understat.com/match/7120'
response = requests.get(url)
soup_object = BeautifulSoup(response.content, 'lxml')

# Retrieve all data with a <script> tag - Field data are in the second <script> group
script_data = soup_object.find_all('script')
# st.write(script_data)


# field_stats = script_data[1].string

# # Strip unnecessary symbols and get only JSON data
# ind_start = field_stats.index("('") + 2
# ind_end = field_stats.index("')")

# json_data = field_stats[ind_start:ind_end]
# json_data = json_data.encode('utf8').decode('unicode_escape')

# # Convert string to json format
# data_dict = json.loads(json_data)


import json
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen

scrape_url = "https://understat.com/league/EPL/2020"
page_connect = urlopen(scrape_url)

page_html = BeautifulSoup(page_connect, "html.parser")
page_html.findAll(name="script")

json_raw_string = page_html.findAll(name="script")[2].string

start_ind = json_raw_string.index("\\")
stop_ind = json_raw_string.index("')")

data = json_raw_string[start_ind:stop_ind]
data = data.encode("utf8").decode("unicode_escape")

data = json.loads(data)

df = pd.DataFrame(data.values())
df = df.explode("history")
h = df.pop("history")
df = pd.concat([df.reset_index(drop=True), pd.DataFrame(h.tolist())], axis=1)

# for example print xG column:
st.write(df.groupby("title")["xG"].sum().sort_values(ascending=False))

