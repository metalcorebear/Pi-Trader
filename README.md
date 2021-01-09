# Pi Trader

(C) 2021 Mark M. Bailey, PhD

## About

Pi Trader is a cryptocurrency trading bot for Raspberry Pi.  This script instantiates a Raspberry Pi trading bot that interfaces with the Coinbase Pro API.  First, it optimizes a trading strategy by backtesting against historic data from the Coinbase exchange.  The strategy is based on buy/risk parameters defined as multiples of the Exponential Average True Range (eATR).  OHLC data are refreshed each iteration, and a buy/sell signal is calculated and executed if appropriate.  For buy signals, the maximum possible number of coins are purchased (with a user-specified fiat buffer preserved).  For sell signals, all coins are exchanged for fiat. Strategy is re-optimized at user-defined intervals.<br>

This is what I would consider to be a "dumb" trading strategy based solely on price deviations from an indicator.  I am curious about exploring machine learning solutions for trading strategy optimization.  Future iterations of this project may include that as an option.<br>

Note that this is an experimental bot, and like all trading strategies, I can not guarantee that it will be profitable if implemented.<br>

If anyone is interested in making this project better, I'd be happy to collaborate.

## References
* Carr, Michael. "Measure Volatility With Average True Range," *Investopedia,* Nov 2019, Link: https://www.investopedia.com/articles/trading/08/average-true-range.asp#:~:text=The%20average%20true%20range%20%28ATR%29%20is%20an%20exponential,signals%2C%20while%20shorter%20timeframes%20will%20increase%20trading%20activity.
* Hall, Mary. "Enter Profitable Territory With Average True Range," *Investopedia,*" Sep 2020, Link: https://www.investopedia.com/articles/trading/08/atr.asp.

## Updates
* 2021-01-09: Initial commit.

## Requirements
* Raspberry Pi running Debian.
* Configured WiFi adaptor or ethernet connection.
* Active Coinbase Pro account API with all access permissions enabled.
* Recommend installing on a fresh, fully-updated image of Debian.

## Installation
* In terminal, navigate to folder and run `git clone https://github.com/metalcorebear/Pi-Trader.git`.
* Navigate to folder and execute `sudo ./setup.sh` to set up the virtual environment.
* Edit "parameters.py" file, as appropriate, with Coinbase API keys and other parameters (see below).

## Parameters
API Key parameters for Coinbase Pro.<br>

* key = Public Key (str)
* secret = Secret Key (str)
* passphrase = Passphrase (str)<br>

Other bot parameters:<br>

* API_KEY = parameters.API_KEY (dict)
* pair = trading pair id (str)
* granularity = interval time for each iteration in seconds (int)
* duration = time to run script in seconds (int)
* cash_buffer = fraction of total cash to keep in account at any given time (float)
* reframe_threshold = frequency of strategy reoptimization in hours (float)
* continuous - set to True if script should run indefinitely (bool)
* chandelier = use/don't use chandelier method for eATR calculation (bool)

## Execution
* To execute, simply run `./run.sh`
