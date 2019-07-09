import requests
import json
import pandas as pd
import codecs
pd.set_option("max_columns", 30)
import os
import aiofiles
import asyncio
import nest_asyncio
nest_asyncio.apply()
import aiohttp
import datetime

# figure out faster way of loading data


class Update_kitties_for_sale:
    '''
    This class should be called in the main file.
    
    This class will pull data of kitties on sale from the cryptokitties API
    
    It will only consider kitties between 0.08 ETH to 1 ETH (approx 60,000) 
    
    '''
    
    def __init__(self):
        self.home_dir = os.getcwd()
        
    
    def Update_kitties(self):
        # changing directory to crawley
        os.chdir(self.home_dir + '\\Crawler')
        
        date_format = datetime.datetime.now().isoformat().replace(':', "-")[:-7]
        print(date_format)
        
        # deleting files in the html folder
        files = [os.path.join(os.getcwd(), "html\\", os.listdir('html')[i]) for i in range(len(os.listdir("html")))]
        
        for i in range(len(os.listdir('html'))):
            os.remove(files[i]) 
        
        
        
        # collecting urls to use for html pull
        # html files will include a 100 kitties each, this will minimise the required files I need to pull
        all_urls = []
        for i in range(int(53662/100)+ 2):
            all_urls.append(f'https://public.api.cryptokitties.co/v1/kitties?include=sale&price=8000000000000000-100000000000000000&orderBy=current_price&limit={100}&offset={i*100}&orderDirection=asc')
            
        # define the payload and token
        payload = {}
        headers = {
          'x-api-token': 'w-5V-v6V__trBl7yxGMXnwhLiGkq-03XnCVNaKePPd4',
          'Content-Type': 'application/json',
        }
        
        ##########################################################################
        #async function
        async def download_html(session, url):
            async with session.request('GET', url, headers = headers, data = payload, allow_redirects=False) as res:
                filename = f'html/output_{len(os.listdir("html/"))}.html'
                print(len(os.listdir("./html")), end = "\r")
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
        
        # loop calling the html files
        for i in range(int(len(all_urls)/10)+ 1):
            urls = all_urls[i*10: i*10 + 10]
            print('step: ' + str(i) + ' out of: ' + str(round(int(len(all_urls))/10 - 1)) +'   Number of files: ' + str(len(os.listdir("html/"))))
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                asyncio.gather(*(main(url) for url in urls))
            )
   
        # Error handling
        ##########################################################################
        
        print("\n\nerror handling\n\n")
        errors = []
        for i in os.listdir("html/"):
            file = codecs.open("html/" + str(i), 'r',  encoding="utf8")
            try:
                parsed = json.loads(file.read())
            except:
                pass

            try:
                parsed['code']
                print(i)
                errors.append(i)
            except:
                pass
        
       
        for e in errors:
            limit = 100
            offset = (int(e[7:].split(".")[0])-1)*100

            url = f'https://public.api.cryptokitties.co/v1/kitties?include=sale&price=8000000000000000-10000000000000000&orderBy=current_price&limit={100}&offset={offset}&orderDirection=asc'
            response = requests.request('GET', url, headers = headers, data = payload, allow_redirects=False).text

            file = open("html/" + e, 'w', encoding="utf-8")
            file.write(response)
            file.close()

            print(e)
            
        print("\n\nDone with errors\n\n")
        
        ##########################################################################
        
        # Sorting dirs so they can be read in the same order that they were placed
        def sorting(val): 
            return (int(val[7:].split(".")[0])-1)  

        dirs = sorted(os.listdir("html/"), key = sorting)
        
        # collecting all of the kittie id_s
        id_s = []
        for d in dirs:
            file= codecs.open("html/"+ d, 'r',  encoding="utf8")
            try:
                parsed = json.loads(file.read())
            except:
                pass
            print(d + " DONE!", end = "\r")

            for i in range(100):
                try: 
                    id_s.append(parsed['kitties'][i]['id'])
                except:
                    print(str(d), end = "\r")
        
        ##########################################################################
        # Creating dataframe and columns
        data = pd.DataFrame(id_s, columns = ['ID'])
        
        data['USD'] = ''
        data['time'] = ''
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


        # resorting columns!
        data = data[['time', 'ID', "USD"] + list(data.columns)[3:]]
        
        ##########################################################################
        # Populating DF with data from html's
        k = 0
        for d in dirs:
            file= codecs.open("html/"+ d, 'r',  encoding="utf8")
            try:
                parsed = json.loads(file.read())
            except:
                pass

            parsed = parsed['kitties']

            for i in range(100):
                try: 
                    # Price
                    data.iloc[k, 2] =  int(parsed[i]['auction']['current_price'])/1000000000000000000

                    # Random
                    data.iloc[k, 3] = parsed[i]['generation']        
                    data.iloc[k, 4] = parsed[i]['color']
                    data.iloc[k, 5] = parsed[i]['is_fancy']
                    data.iloc[k, 6] = parsed[i]['is_exclusive']
                    data.iloc[k, 7] = parsed[i]['fancy_type']
                    data.iloc[k, 8] = parsed[i]['is_prestige']
                    data.iloc[k, 9] = parsed[i]['prestige_type']
                    data.iloc[k, 10] = parsed[i]['prestige_ranking']
                    data.iloc[k, 11] = parsed[i]['fancy_ranking']
                    data.iloc[k, 12] = parsed[i]['prestige_time_limit']

                    # Enhanced cattributes
                    if parsed[i]['enhanced_cattributes'] != []:
                        data.iloc[k, 13] = parsed[i]['enhanced_cattributes'][0]['description']
                        data.iloc[k, 14] = parsed[i]['enhanced_cattributes'][1]['description']
                        data.iloc[k, 15] = parsed[i]['enhanced_cattributes'][2]['description']
                        data.iloc[k, 16] = parsed[i]['enhanced_cattributes'][3]['description']
                        data.iloc[k, 17] = parsed[i]['enhanced_cattributes'][4]['description']
                        data.iloc[k, 18] = parsed[i]['enhanced_cattributes'][5]['description']
                        data.iloc[k, 19] = parsed[i]['enhanced_cattributes'][6]['description'] 
                        data.iloc[k, 20] = parsed[i]['enhanced_cattributes'][7]['description']

                    # Status
                    data.iloc[k, 21] = parsed[i]['status']['cooldown_index']
                    data.iloc[k, 22] = parsed[i]['status']['is_ready']
                    data.iloc[k, 23] = parsed[i]['status']['is_gestating']

                    # Purrs
                    data.iloc[k, 24] = parsed[i]['purrs']['count']
                    data.iloc[k, 25] = parsed[i]['purrs']['is_purred']

                    # watchlist
                    data.iloc[k, 26] = parsed[i]['watchlist']['count']
                    data.iloc[k, 27] = parsed[i]['watchlist']['is_watchlisted']


                    print(f"we at: {k} out of {data.shape[0]}. Giving us percent complete of {round(100*k/int(data.shape[0]), 5)}%   ", end = "\r")

                    if k % 100 == 0:
                        data.to_csv("Latest_kitties_{}.csv".format(date_format), index = False)

                    k = k + 1
                except:
                    print("\n" + str(d))
        data.to_csv("Latest_kitties_{}.csv".format(date_format), index = False)
        print("ALL DONE updated kitties")
        
        os.chdir(self.home_dir)