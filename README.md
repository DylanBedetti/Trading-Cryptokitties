# Trading-Cryptokitties
A <b>machine learning</b> based tool to predict the <b>expected sale values</b> of <b>Cryptokitties</b>. 

---

## To Do
- [x] Collect initial data
- [x] Connect to current kitties on sale!
- [x] Create Update algorithm
- [x] Collect trend data
- [x] Collect eth price data
- [x] Get predict data working
- [x] Make a combine script (for train_dense, trend and eth price) - probably going to be a bit nasty
- [ ] Add columns that measures scarcity of cat?
- [ ] Make tool to see past cryptokittie sales that are similar
- [ ] Create model class which check if model saved avaliable or trains new model
- [ ] Connect email - send top 50 buys with important stats
- [ ] Log best 50 buy for each day
- [ ] Make everything into classes
- [ ] Make website to display everything?
- [ ] add logging
- [ ] figure out how to optimise model performance
- [ ] create main file to run everything
- [ ] create requirements.txt
- [ ] test on raspberry pi
- [ ] host website on raspberry pi!!!

How do you know if its actually a good prediction? or just a one off really shit one?
Mewtation gems??

## Overview
- Subactions will be called by a `main.py` script. This will also organise which results to send via email.

> **Data**
- Initial - collecting all of the initial data to be used, should only be run once
- Update - used to update the `train_dense.csv` with the latest data
- Prediction - collecting the latest data for kitties on sale (~50,000) through steps of 500-1000
- Trends - collecting google trend data
- Eth_price - collecting ethereum price 
- Combine - will combine the collected data (either for train or predict)

> **Model**
- Train - use combined training data to train a model, output saved in `Saved_models` and `Label_encoders`
- Predict - use combined predicting data to predict on data, output saved in `Predictions`
- Clean - run to delete excess saved models and label encoders (want to keep lightweight)

> **Email** 
- Send - send an email with given contents 

## How to use (Python 3.6.8)

> create a virtual env ect....
pip install -r requirements.txt



## Important links

- create cool links
Cryptokitties sale contract:
https://etherscan.io/address/0xb1690c08e213a35ed9bab7b318de14420fb57d8c#tokentxnsErc721