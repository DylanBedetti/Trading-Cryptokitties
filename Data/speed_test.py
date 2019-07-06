import line_profiler
import pandas as pd
import requests
import json
import warnings
import codecs
warnings.filterwarnings('ignore')

pd.set_option('max_columns', 30)
data = pd.read_csv('train_complete.csv')

@profile
def data_to_csv():
    for k in range(5):
        i_d = data.iloc[k, 1]

        file= codecs.open("html/output_" + str(i_d) + ".html", 'r',  encoding="utf8")
        parsed = json.loads(file.read())
        
        p = [parsed['generation'], parsed['color'], parsed['is_fancy'],parsed['is_exclusive'], parsed['fancy_type'],\
            parsed['is_prestige'],parsed['prestige_type'], parsed['prestige_ranking'],parsed['fancy_ranking'],parsed['prestige_time_limit']]

        # Random
        data.iloc[k, 3] = p[0]        
        data.iloc[k, 4] = p[1]
        data.iloc[k, 5] = p[2]
        data.iloc[k, 6] = p[3]
        data.iloc[k, 7] = p[4]
        data.iloc[k, 8] = p[5]
        data.iloc[k, 9] = p[6]
        data.iloc[k, 10] = p[7]
        data.iloc[k, 11] = p[8]
        data.iloc[k, 12] = p[9]

        if parsed['enhanced_cattributes'] != []:
            data.iloc[k, 13] = parsed['enhanced_cattributes'][0]['description']
            data.iloc[k, 14] = parsed['enhanced_cattributes'][1]['description']
            data.iloc[k, 15] = parsed['enhanced_cattributes'][2]['description']
            data.iloc[k, 16] = parsed['enhanced_cattributes'][3]['description']
            data.iloc[k, 17] = parsed['enhanced_cattributes'][4]['description']
            data.iloc[k, 18] = parsed['enhanced_cattributes'][5]['description']
            data.iloc[k, 19] = parsed['enhanced_cattributes'][6]['description'] 
            data.iloc[k, 20] = parsed['enhanced_cattributes'][7]['description']

        # Status
        data.iloc[k, 21] = parsed['status']['cooldown_index']
        data.iloc[k, 22] = parsed['status']['is_ready']
        data.iloc[k, 23] = parsed['status']['is_gestating']

        # Purrs
        data.iloc[k, 24] = parsed['purrs']['count']
        data.iloc[k, 25] = parsed['purrs']['is_purred']

        # watchlist
        data.iloc[k, 26] = parsed['watchlist']['count']
        data.iloc[k, 27] = parsed['watchlist']['is_watchlisted']



        print(f"we at: {k} out of 106261. Giving us percent complete of {round(100*k/106261, 5)}%   ", end = "\r")
        
data_to_csv()