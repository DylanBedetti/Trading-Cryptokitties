import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder


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
        
    def Train_model(self):
        
       