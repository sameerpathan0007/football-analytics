#import modules
import os
import glob
import pandas as pd
#list all csv files only
csv_files = glob.glob('*.{}'.format('csv'))
print(csv_files)

df_append = pd.DataFrame()
#append all files together
for file in csv_files:
            df_temp = pd.read_csv(file)
            df_append = df_append.append(df_temp, ignore_index=True)


df_append.to_csv('D:\Analytics\scouting.csv')

# df = pd.read_csv('D:\Analytics\epl_full.csv')
# df2 = df.head(5)
# home = df['home_team'][0]
# away = df['away_team'][0]

# match = f'{home} vs {away}'

# # print(match)
# final = {}
# for index, row in df2.iterrows():
#     new = row['home_team'] + ' vs ' + row['away_team']
#     final[new] = row['match_id']

# print(final)


