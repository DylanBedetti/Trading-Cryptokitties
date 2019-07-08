import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder
import glob
from collections import defaultdict
import bisect
import pickle
import datetime

# MAKE SURE MODEL TRAINING ON ENTIRE DATASET!
class Model_functions:
    '''
    This class will provide two functions:
    
    1) Retraining a model on the avaliable data and then saving this model in Saved_models with the label encodings in Saved_encoder
    
    2) Predict using the latest model (and if there isnt one then create one!)
     - Predict will save the predictions in Saved_predictions
     - This will then be picked up by the email sender and will send the top 50 results!
    '''
    
    def __init__(self):
        
        self.home_dir = os.getcwd()
        
#     def Model_train(self):
        
        
        
    def Model_predict(self):
        
        # Changing folder
        os.chdir(self.home_dir + '\\Model')
        
        date_time = datetime.datetime.now().isoformat().replace(':', "-")[:-7]
        
        # finding latest model to load up
        latest_model = os.listdir("Saved_models/")[-1]
        
        print(f"\nThe latest model is {latest_model}")
        
        # finding latest kitties to predict on
        latest_kitties = glob.glob('../Crawler/*.csv')[-1]
        
        print(f"\nThe latest kitties is {latest_kitties}")
        
        data = pd.read_csv(latest_kitties)
        
        print("Updating data fields")
        
        # Updating time field
        t = pd.read_csv("../Data/train_complete.csv")['time'].apply(lambda x: x[:10])
        t = pd.to_timedelta(pd.to_datetime(t), unit = 'seconds').astype('timedelta64[D]')[0]
        data['time'] = t
        
        # changing time column to date
        c = list(data.columns)
        c[0] = "date"
        data.columns = c
        
        # Updating prestige time
        data['prestige_time_limit'] = data['prestige_time_limit'].apply(lambda x: np.nan if pd.isnull(x) else x[:10])
        data['prestige_time_limit'] = pd.to_timedelta(pd.to_datetime(data['prestige_time_limit']), unit = 'seconds').astype('timedelta64[D]')
        
        # getting trends data
        trends = pd.read_csv("../Data/trends.csv")
            
        # getting ETH data
        ETH = pd.read_csv("../Data/ETH_price.csv")
        ETH = ETH[["date", "close"]]
        
        # updating columns
        data['trends'] = trends['cryptokitties']
        data['close'] = ETH['close']
        
        # updating price to USD
        data['USD'] = data['USD'] * ETH['close'][0]
        
        # filling nulls with '0'
        data = data.fillna('0')
        
        ######################################################################
        # label encoding
        print("Label Encoding")
        
        d = defaultdict(LabelEncoder)
        
        # getting directories
        dirs = [x.split(".")[0] for x in os.listdir("Saved_encoder/")]
        
        # loading classes for each label encoder
        for e in dirs:
            d[e].classes_ = np.load(f'Saved_encoder/{e}.npy', allow_pickle = True)
            
        cols = ['color', 'fancy_type', 'prestige_type', 'enhanced_cattributes_eyes', 'enhanced_cattributes_pattern', 'enhanced_cattributes_body', 'enhanced_cattributes_mouth', 'enhanced_cattributes_colorprimary', 'enhanced_cattributes_colorsecondary', 'enhanced_cattributes_colortertiary', 'enhanced_cattributes_coloreyes']
        
        # Checking for others in columns!
        for c in cols:
            data[c] = data[c].map(lambda s: 'other' if s not in d[c].classes_ else s)

            le_classes = d[c].classes_.tolist()
            bisect.insort_left(le_classes, 'other')
            d[c].classes_ = le_classes
        
        # label encoding columns
        data[cols] = data[cols].apply(lambda x: d[x.name].transform(x))
        
        ######################################################################
        # Prediction
        print("Prediction time")
        
        X = data.drop('USD', axis = 1)
        
        loaded_model = pickle.load(open(f"Saved_models/{latest_model}", 'rb'))
        res = loaded_model.predict(X)
        
        data['predictions'] = res
        
        data.to_csv(f"Saved_predictions/predictions_{date_time}.csv")
        
        print("Predictions completed. Saved in Saved_predictions")
        
#         return res
        os.chdir(self.home_dir)



        
       