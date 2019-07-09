import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error, median_absolute_error
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
        
    def Model_train(self, length = 100000):
        '''
        length = number of last datapoints to consider 
        '''
        
        # Changing folder
        os.chdir(self.home_dir + '\\Model')
        
        ######################################################################
        # Initial
        
        # reading trends data
        trends = pd.read_csv("../Data/trends.csv")
        
        # reading ETH data
        ETH = pd.read_csv("../Data/ETH_price.csv")
        ETH = ETH[["date", "close"]]
        
        # reading training data
        data = pd.read_csv("../Data/train_complete.csv")
        data['time'] = data['time'].apply(lambda x: x[:10])
        
        # changing time to date column
        c = list(data.columns)
        c[0] = "date"
        data.columns = c

        # MERGING AND CHANING COLUMNS
        data = pd.merge(data, trends, on='date')
        data = pd.merge(data, ETH, on='date')

        # changing time columns
        data['date'] = pd.to_timedelta(pd.to_datetime(data['date']), unit = 'seconds').astype('timedelta64[D]')
        data['prestige_time_limit'] = data['prestige_time_limit'].apply(lambda x: np.nan if pd.isnull(x) else x[:10])
        data['prestige_time_limit'] = pd.to_timedelta(pd.to_datetime(data['prestige_time_limit']), unit = 'seconds').astype('timedelta64[D]')

        # filling nulls 
        data = data.fillna('0')
        
        # Scarcity
        fancy_scarcity = dict(data['fancy_type'].value_counts())
        data['fancy_type_scarcity'] = data['fancy_type'].map(lambda x: fancy_scarcity[x])
        np.save("Saved_scarcity_values/fancy_type_scarcity.npy", fancy_scarcity)

        color_scarcity = dict(data['color'].value_counts())
        data['color_scarcity'] = data['color'].map(lambda x: color_scarcity[x])
        np.save("Saved_scarcity_values/color_scarcity.npy", color_scarcity)

        generation_scarcity = dict(data['generation'].value_counts())
        data['generation_scarcity'] = data['generation'].map(lambda x: generation_scarcity[x])
        np.save("Saved_scarcity_values/generation_scarcity.npy", generation_scarcity)
        
        ######################################################################
        # Label Encoding
        
        # define labelencoder
        d = defaultdict(LabelEncoder)
        
        # defining columns to fit
        cols = ['color', 'fancy_type', 'prestige_type', 'enhanced_cattributes_eyes', 'enhanced_cattributes_pattern', 'enhanced_cattributes_body', 'enhanced_cattributes_mouth', 'enhanced_cattributes_colorprimary', 'enhanced_cattributes_colorsecondary', 'enhanced_cattributes_colortertiary', 'enhanced_cattributes_coloreyes']
        
        # applying fit_transform
        data[cols] = data[cols].apply(lambda x: d[x.name].fit_transform(x))
        
        # Saving encodings
        for c in d:
            np.save(f'Saved_encoder/{c}.npy', d[c].classes_)
        
        ######################################################################
        # Preparing Data
        y = data["USD"]
        X = data.drop("USD", axis = 1)
        
         # the lastest values to predict on
        n = 500
        
        # Splitting X and y
        y = y[:length]
        X = X.iloc[:length, :]

        X_test = X.iloc[:n, :]
        y_test = y[:n]

        X_train = X.iloc[n:, :]
        y_train = y[n:]
        
        ######################################################################
        # Training Model
        regr = RandomForestRegressor(n_estimators=100, verbose= 3,n_jobs=8)
        regr.fit(X_train, y_train)
        
        pred = regr.predict(X_train)
        print('Train model errors')
        print('MSE (mean sqaured error) : ' + str(mean_squared_error(y_train, pred)))
        print('MAE (mean absolute error): ' + str(mean_absolute_error(y_train, pred)))
        print('MAE (median absolute error): ' + str(median_absolute_error(y_train, pred)))

        pred = regr.predict(X_test)
        print(f'future prediction errors (next {n} sales)')
        print('MSE (mean sqaured error) : ' + str(mean_squared_error(y_test, pred)))
        print('MAE (mean absolute error): ' + str(mean_absolute_error(y_test, pred)))
        print('MAE (median absolute error): ' + str(median_absolute_error(y_test, pred)))
        
        ######################################################################
        # Saving Model
        date_time = datetime.datetime.now().isoformat().replace(':', "-")[:-7] 
        
        filename = f"Saved_models/ML_Model_{date_time}.sav"
        pickle.dump(regr, open(filename, 'wb'))
        
        print(f"Model Saved as: {filename}")
        
        print("\n\n-------Completed Training-------\n\n")
        
        os.chdir(self.home_dir)
        
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
        
        orig_data = pd.read_csv(latest_kitties)
        data = orig_data
        
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
        data['trends'] = trends['cryptokitties'][0]
        data['close'] = ETH['close'][0]
        
        # updating price to USD
        data['USD'] = data['USD'] * ETH['close'][0]
        
        # filling nulls with '0'
        data = data.fillna('0')
        
#         print("\n\n-------Table Overview-------\n\n")
#         print(data.head(5))
#         print(data.tail(5))
        
        
        print("adding Scarcity values")
        
        
        # Scarcity
        fancy_scarcity = np.load("Saved_scarcity_values/fancy_type_scarcity.npy", allow_pickle = True).item()
        data['fancy_type'] = data['fancy_type'].map(lambda s: 'other' if s not in fancy_scarcity.keys() else s)
        fancy_scarcity["other"] = 1000
        data['fancy_type_scarcity'] = data['fancy_type'].map(lambda x: fancy_scarcity[x])

        color_scarcity =  np.load("Saved_scarcity_values/color_scarcity.npy", allow_pickle = True).item()
        data['color'] = data['color'].map(lambda s: 'other' if s not in color_scarcity.keys() else s)
        color_scarcity['other'] = 1000
        data['color_scarcity'] = data['color'].map(lambda x: color_scarcity[x])

        generation_scarcity = np.load("Saved_scarcity_values/generation_scarcity.npy", allow_pickle = True).item()
        data['generation'] = data['generation'].map(lambda s: 100 if s not in generation_scarcity.keys() else s)
        generation_scarcity['other'] = 1
        data['generation_scarcity'] = data['generation'].map(lambda x: generation_scarcity[x])

        
        
        
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
        
        orig_data['predictions'] = res
        
        orig_data.to_csv(f"Saved_predictions/predictions_{date_time}.csv", index = False)
        
        print("Predictions completed. Saved in Saved_predictions")
        
        os.chdir(self.home_dir)



        
       