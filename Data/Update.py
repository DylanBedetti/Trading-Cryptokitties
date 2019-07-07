import pandas as pd
import requests
import json
import warnings
from cryptory import Cryptory
import os
import codecs
import shutil
import aiofiles
import asyncio
import nest_asyncio
nest_asyncio.apply()
import aiohttp
warnings.filterwarnings('ignore')


# HOW TO DEAL WITH ERRORS FROM HTML??

class Update_train_dataset:
    '''
    This class should be called in the main file.
    
    This class will do the following:
    ---------------------------------
    1) Nonfungible --> (time, ID, USD) --> Kitties API --> (25 datapoints) --> update train_complete.csv
    
    2) Cryptory --> ETH_price.csv
    
    3) Cryptory --> trends.csv
    
    '''
    
    def __init__(self):
        self.home_dir = os.getcwd()
        
    def Update_ETH_price(self):
        # Change to data directory
        os.chdir(self.home_dir + '\\Data')
        
        # define date to pull from 
        my_cryptory = Cryptory(from_date = "2017-05-01")

        # get historical ethereum prices from coinmarketcap
        df = my_cryptory.extract_coinmarketcap("ethereum")
        
        # save as csv
        df.to_csv('ETH_price.csv', index = 0)
        
        print("\nUpdated Ethereum price data, saved in ETH_price.csv\n")
        
        # change directory back to original
        os.chdir(self.home_dir)
        
    def Update_trends(self):
        # Change to data directory
        os.chdir(self.home_dir + '\\Data')
        
        # define date
        my_cryptory = Cryptory(from_date = "2017-05-01")
        
        # pull data from google trends
        df = my_cryptory.get_google_trends(kw_list=["cryptokitties"])
        
        # save as csv
        df.to_csv('trends.csv', index = 0)
        
        print("\nUpdated google trends data, saved in trends.csv\n")
        
        # change directory back to original
        os.chdir(self.home_dir)
        
    
    def Update_train_dense(self):
        '''
        Update train_dense and return to update all function
        '''
        # read latest training data
        data = pd.read_csv('train_complete.csv')
        # finding latest data that I have
        latest_time = data['time'][0]
        latest_ID = data['ID'][0]
        latest_USD = data['USD'][0]

        # defining dict to store new data
        updated = {'results':[]}

        # for loop with arbitrarily large number 
        for i in range(500):
            data_points = 80
            start = data_points*i # Starting point to collect data
            URL = "https://nonfungible.com/api/v1/market/cryptokitties/history/?start={}&length={}&columns[0][name]=blockTimestamp&order[0][dir]=desc".format(start, data_points)

            # using requests to get json data, converting into python dict
            r = requests.get(url = URL)
            data = r.json()

            for k in range(data_points):
                # type cannot equal mint, only interested in sale type
                if data['data'][k]['saleType'] != 'mint':
                    # extract important information
                    ID = data['data'][k]['assetId']
                    USD = data['data'][k]['usdPrice']
                    time = data['data'][k]['blockTimestamp']
                    
                    print(time, ID, USD, end = "\r")
                    
                    # check if latest point is the same as our current latest point
                    if (str(time) == latest_time) and (int(ID) == latest_ID) and (float(USD) == latest_USD):
                        print(f"FOUND LATEST POINT!, it is time: {time}, USD: {USD}, ID: {ID}")
                        return pd.DataFrame(updated['results'], columns=['time', 'ID', 'USD'])


                    updated['results'].append([time, ID, USD])

    def Populate_dense(self, data):
        for k in range(len(data)):
            i_d = data.iloc[k, 1]

            file= codecs.open("html/output_" + str(i_d) + ".html", 'r',  encoding="utf8")
            parsed = json.loads(file.read())

            # Random
            data.iloc[k, 3] = parsed['generation']        
            data.iloc[k, 4] = parsed['color']
            data.iloc[k, 5] = parsed['is_fancy']
            data.iloc[k, 6] = parsed['is_exclusive']
            data.iloc[k, 7] = parsed['fancy_type']
            data.iloc[k, 8] = parsed['is_prestige']
            data.iloc[k, 9] = parsed['prestige_type']
            data.iloc[k, 10] = parsed['prestige_ranking']
            data.iloc[k, 11] = parsed['fancy_ranking']
            data.iloc[k, 12] = parsed['prestige_time_limit']

            # Enhanced cattributes
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


            print(f"we at: {k} out of {len(data)}. Giving us percent complete of {round(100*k/len(data), 5)}%   ", end = "\r")
        print("\nWE DONE POPULATING DF WITH LATEST HTML")
        return data

    
    
    def Update_all(self):
        # Change directory into Data folder
        os.chdir(self.home_dir + '\\Data')

        data = self.Update_train_dense()

        # Time to initialise all of the columns we are interested in 
        # Random
        data['generation'] = ''
        data['color'] = ''
        data['is_fancy'] = ''
        data['is_exclusive'] = ''
        data['fancy_type'] = ''
        data['is_prestige'] = ''
        data['prestige_type'] = ''
        data['prestige_ranking'] = ''
        data['fancy_ranking'] = ''
        data['prestige_time_limit'] = ''

        # Enhanced cattributes
        data['enhanced_cattributes_eyes'] = '' 
        data['enhanced_cattributes_pattern'] = '' 
        data['enhanced_cattributes_body'] = '' 
        data['enhanced_cattributes_mouth'] = '' 
        data['enhanced_cattributes_colorprimary'] = '' 
        data['enhanced_cattributes_colorsecondary'] = '' 
        data['enhanced_cattributes_colortertiary'] = '' 
        data['enhanced_cattributes_coloreyes'] = '' 

        # Status
        data['status_cooldown_index'] = ''
        data['status_is_ready'] = ''
        data['status_is_gestating'] = ''

        # Purrs
        data['purrs_count'] = ''
        data['purrs_is_purred'] = ''

        # watchlist
        data['watchlist_count'] = ''
        data['watchlist_is_watchlisted'] = ''

        # definig url_list to pull from!
        url_list = ['https://public.api.cryptokitties.co/v1/kitties/' + str(i) for i in data['ID'].unique()]

        print(f"We need to pull {len(url_list)} URL's")
        
        
        # Files to delete!
        files = [os.path.join(os.getcwd(), "html\\", os.listdir('html')[i]) for i in range(len(os.listdir("html")))]
        
        for i in range(len(os.listdir('html'))):
            os.remove(files[i]) 
            

        # define the payload and headers!
        payload = {}
        headers = {
          'x-api-token': 'w-5V-v6V__trBl7yxGMXnwhLiGkq-03XnCVNaKePPd4',
          'Content-Type': 'application/json',
        }

        # async function to get url
        async def download_html(session, url):
            async with session.request('GET', url, headers = headers, data = payload, allow_redirects=False) as res:
                filename = f'html/output_{os.path.basename(url)}.html'
                print(len(os.listdir("html/")), end = "\r")
                async with aiofiles.open(filename, 'wb') as f:
                    while True:
                        chunk = await res.content.read(1024)
                        if not chunk:
                            break
                        await f.write(chunk)

                return await res.release()

        async def main(url):
            connector = aiohttp.TCPConnector(limit=60)
            async with aiohttp.ClientSession(connector=connector) as session:
                await download_html(session, url)

        # Scanning through the url_list to downlaod html files
        for i in range(int(len(url_list)/100)+1):
            urls = url_list[i*100:i*100+100]
            print('step: ' + str(i) + '   Number of files: ' + str(len(os.listdir("./html"))))
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                asyncio.gather(*(main(url) for url in urls))
            )
        
        # Completed!
        n = len(os.listdir("html/"))
        print(f"DONE PULLING {n} HTML FILES")
        
        # Time to populate the df with the data from the html files
        new_data = self.Populate_dense(data)
        
        # Time to pull the old data
        old_data = pd.read_csv("train_complete.csv")
        
        # Merge the new data with the old
        new_data = new_data.append(old_data)
        
        # Save this file
        new_data.to_csv("train_complete.csv", index = False)
        
        # Print response
        print(f"\n\nNew Data has been merged with old data. \nAdded an aditional {data.shape[0]} rows \nGiving a total of {new_data.shape[0]} data points\nSaved in train_complete.csv\n\n")
        
        
        os.chdir(self.home_dir)

