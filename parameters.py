#!/usr/bin/env python3
"""
Created on Fri Jan  8 11:17:23 2021

@author: metalcorebear
"""

"""
Contains all parameters for crypto trading bot.

"""

"""
API Key parameters for Coinbase Pro.
*** Ensure that all API permissions are enabled.***

# key = Public Key (str)
# secret = Secret Key (str)
# passphrase = Passphrase (str)

"""
API_KEY = {'key':'XXXXXXX', 'secret':'XXXXXXX', 'passphrase':'XXXXXXX'}


"""
Other bot parameters.

# API_KEY = parameters.API_KEY (dict)
# pair = trading pair id (str)
# granularity = interval time for each iteration in seconds.  Default value is 15*60 (15 minutes).  Note that this has not been tested for other durations, and shorter intervals may trigger API rate limitaitons and will reduce the overall timeframe of historic OHLC data used in strategy backtesting (due to the 300 value limit of the Coinbase Pro historic data API call). (int)
# duration = time to run script in seconds (int)
# cash_buffer = fraction of total cash to keep in account at any given time (float)
# reframe_threshold = frequency of strategy reoptimization in hours (float)
# continuous - set to True if script should run indefinitely (bool)
# chandelier = use/don't use chandelier method for eATR calculation (bool)

"""
pair = 'BTC-USD'
granularity = 15*60
duration = 2*60*60
cash_buffer = 0.1
reframe_threshold = 48.0
continuous = False
chandelier = False
