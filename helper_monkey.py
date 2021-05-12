#!/usr/bin/env python3
"""
Created on Fri Jan  8 11:25:49 2021

@author: metalcorebear
"""

import cbpro
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import time

# data acquistion functions

def get_product_data(pair):
    output = {}
    public_client = cbpro.PublicClient()
    products = public_client.get_products()
    for item in products:
        if item['id'] == pair:
            output.update(item)
    return output
    
def get_historic_data(pair='BTC-USD', granularity=900, **options):
    public_client = cbpro.PublicClient()
    history = public_client.get_product_historic_rates(pair, granularity=granularity)
    history_array = np.array(history)
    history_pd = pd.DataFrame(history_array, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
    return history_pd, history_array

def get_latest(pair='BTC-USD', granularity=900):
    public_client = cbpro.PublicClient()
    start = datetime.now()
    end = start + timedelta(minutes=int(granularity/60))
    history = public_client.get_product_historic_rates(pair, granularity=granularity, start=str(start.isoformat()), end=str(end.isoformat()))
    #history_array = np.array(history)
    return history

def new_history(history_array, history):
    history_array_list = history_array.tolist()
    history.extend(history_array_list)
    history_array = np.array(history)
    #history = np.array(history, dtype=history_array.dtype)
    #history_array = np.concatenate((history, history_array), axis=0)
    history_array = history_array[:-1,:]
    return history_array


# Trading functions

def make_trade(pair, amount, trade_type, key, secret, passphrase):
    auth_client = cbpro.AuthenticatedClient(key, secret, passphrase)
    if trade_type == 'buy':
        response = auth_client.buy(order_type='market', product_id=pair, funds=amount)
    if trade_type == 'sell':
        response = auth_client.sell(order_type='market', product_id=pair, size=amount)
    return response

def check_order_status(response, key, secret, passphrase):
    auth_client = cbpro.AuthenticatedClient(key, secret, passphrase)
    order_id = response['id']
    output = True
    if order_id is not None:
        check = auth_client.get_order(order_id)
        output = check['settled']
    return output

def get_currency_balance(currency, key, secret, passphrase):
    auth_client = cbpro.AuthenticatedClient(key, secret, passphrase)
    response = auth_client.get_accounts()
    for item in response:
        if item['currency'] == currency:
            output = float(item['available'])
    return output

# strategy functions

def reframe_data(data):
    # history = [time, low, high, open, close, volume]
    data.rename(columns={'low':'low', 'high':'high', 'open':'Open', 'close':'Adj Close'}, inplace=True)
    data = data[['Open', 'high', 'low', 'Adj Close']]
    data = data.iloc[::-1]
    data = data.values
    data = pd.DataFrame(data, columns=['Open', 'high', 'low', 'Adj Close'])
    return data

def eATR(data, lookback=10):
    m = data.values
    z = np.zeros((m.shape[0], 2))
    m = np.concatenate((m, z), axis=1)
    columns = ['Open', 'high', 'low', 'Adj Close', 'ATR', 'eATR']
    # calculate ATR values
    for i in range(1, len(m)):
        atr = [m[i,1] - m[i,2], abs(m[i,1] - m[i-1,3]), abs(m[i-1,3] - m[i,2])]
        m[i,4] = max(atr)
    # calcualate exponential moving average
    alpha = 2.0/float(lookback+1.0)
    sma = sum(m[:lookback,4]) / float(lookback)
    m[lookback,5] = sma
    for i in range(1,len(m)-lookback):
         m[i+lookback,5] = m[i+lookback,4]*alpha + m[i-1+lookback,5]*(1.0-alpha)
    out = pd.DataFrame(m, columns=columns, index=data.index)
    return out

def strategize(data, strategy={'buy':1.0, 'risk':1.0}, chandelier=False):
    m = data.values
    z = np.zeros((m.shape[0], 2))
    m = np.concatenate((m, z), axis=1)
    columns = ['Open', 'high', 'low', 'Adj Close', 'ATR', 'eATR', 'buy_point', 'sell_point']
    for i in range(1, len(m)):
        if (m[i,3] > (m[i-1,3] + strategy['buy']*m[i-1,5])) and (m[i-1,5]>0):
            m[i,6] = 1
        if chandelier:
            if (m[i,3] < (m[i-1,1] - strategy['risk']*m[i-1,5])) and (m[i-1,5]>0):
                m[i,7] = 1
        else:
            if (m[i,3] < (m[i-1,3] - strategy['risk']*m[i-1,5])) and (m[i-1,5]>0):
                m[i,7] = 1
    out = pd.DataFrame(m, columns=columns, index=data.index)
    return out

def evaluate(data, risk_factor=1.0, chandelier=False):
    m = data.values
    profits = []
    risk_rewards = []
    winning = 0
    all_trades = 0
    
    j = 0
    j_start = 1
    first_buy = []
    
    for i in range(1,len(m)-1):
        
        if m[i,6] == 1:
            buy = m[i,3]
            if len(first_buy) == 0:
                first_buy.append(buy)
            if j_start < i:
                j_start = i+1
            else:
                j_start = j
            for j in range(j_start,len(m)):
                if m[j,7] == 1:
                    sell = m[j,3]
                    all_trades += 1
                    profit = sell-buy
                    profits.append(profit)
                    if chandelier:
                        stop = m[i-1,1] - risk_factor*m[i,5] 
                    else:
                        stop = m[i-1,3] - risk_factor*m[i,5]
                    risk_reward = profit / (buy - stop)
                    risk_rewards.append(risk_reward)
                    if profit > 0:
                        winning += 1
                    break
    
    if len(profits) != 0:   
        expected = np.average(np.array(profits))
        total_profit = sum(profits)
        ROI = round(total_profit / first_buy[0],2)
    else:
        expected = 0.0
        total_profit = 0.0
        ROI = 0.0
    total_profit = sum(profits)
    profits = np.array(profits)
    equity_curve = profits.cumsum()
    if all_trades != 0:
        hit_ratio = round(float(winning) / float(all_trades), 2)
    else:
        hit_ratio = 0.0
    gross_profits = [k for k in profits if k > 0]
    gross_losses = [abs(k) for k in profits if k < 0]
    if sum(gross_losses) != 0.0:
        profit_factor = round(sum(gross_profits) / sum(gross_losses), 2)
    else:
        profit_factor = np.nan
    if len(risk_rewards) != 0:
        risk_reward = np.average(np.array(risk_rewards))
    else:
        risk_reward = 0.0
    output = {'hit_ratio':round(hit_ratio,2), 'total_trades':all_trades, 'expected':round(expected,2), 'total_profit':round(total_profit,2), 'ROI':ROI, 'profit_factor':round(profit_factor,2), 'risk_ratio':round(risk_reward,2), 'equity_curve':equity_curve}
    return output

def simulate_strategies(data, buy_range = (1.0, 4.0, 0.25), risk_range=(1.0, 4.0, 0.25), chandelier=False):
    buy_i = (buy_range[1] - buy_range[0])/buy_range[2]
    buy_test = [buy_range[0] + float(i)*buy_range[2] for i in range(int(buy_i)+1)]
    risk_i = (risk_range[1] - risk_range[0])/risk_range[2]
    risk_test = [risk_range[0] + float(i)*risk_range[2] for i in range(int(risk_i)+1)]
    strategies = []
    
    for i in buy_test:
        for j in risk_test:
            s = {'buy':i, 'risk':j}
            strategies.append(s)
    
    for i in range(len(strategies)):
        strategy = strategies[i]
        eatr = eATR(data)
        strat = strategize(eatr, strategy=strategy, chandelier=chandelier)
        sim = evaluate(strat, risk_factor=strategy['risk'], chandelier=chandelier)
        strategy.update(sim)
    return strategies

def find_optimal_strategy(strategies):
    previous_number_to_beat = 0.0
    best_strategy = {'buy':1.0,'risk':1.0}
    for strategy in strategies:
        profit = strategy['total_profit']
        if profit > previous_number_to_beat:
            best_strategy = strategy
            previous_number_to_beat = profit
    return best_strategy

def optimize_strategy(data, buy_range = (1.0, 4.0, 0.25), risk_range=(1.0, 4.0, 0.25), chandelier=False):
    strategies = simulate_strategies(data, buy_range = (1.0, 4.0, 0.25), risk_range=(1.0, 4.0, 0.25), chandelier=chandelier)
    best_strategy = find_optimal_strategy(strategies)
    return best_strategy

def iterate_signal(history_array, strategy, pair='BTC-USD', granularity=900, chandelier=False):
    history = get_latest(pair=pair, granularity=granularity)
    history_array = new_history(history_array, history)
    history_pd = pd.DataFrame(history_array, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
    history_pd = reframe_data(history_pd)
    history_pd = eATR(history_pd, lookback=10)
    history_pd = strategize(history_pd, strategy=strategy, chandelier=chandelier)
    end_point = len(history_pd) - 1
    buy_point, sell_point = history_pd['buy_point'][end_point], history_pd['sell_point'][end_point]
    if buy_point == 1:
        buy_point = True
    else:
        buy_point = False
    if sell_point == 1:
        sell_point = True
    else:
        sell_point = False
    return history_array, buy_point, sell_point


# MAIN FUNCTION

def main(API_KEY, pair='BTC-USD', granularity=900, duration=7*24*60*60, cash_buffer=0.1, reframe_threshold=48.0, continuous=False, chandelier=False):
    
    key, secret, passphrase = API_KEY['key'], API_KEY['secret'], API_KEY['passphrase']
    print('Initializing optimal trading strategy...')
    
    # Get initial optimal strategy
    history_pd, history_array = get_historic_data(pair=pair, granularity=granularity)
    reframed = reframe_data(history_pd)
    best_strategy = optimize_strategy(reframed, buy_range = (1.0, 4.0, 0.25), risk_range=(1.0, 4.0, 0.25), chandelier=False)
    
    # Initializing timestamp
    
    running = True
    total_cycles = int(duration/granularity)
    cycle = 0
    
    total_hours = duration/3600
    
    t = 0
    hour = 1.0
    
    response = {'id':None}
    
    while running:
        
        # Timecheck and reoptimization check
        cycle += 1
        if cycle >= total_cycles:
            if not continuous:
                print('{}: Duration exceeded.'.format(str(round(t))))
                t += 1
                running = False
            else:
                running = True
        elapsed_hours = (cycle/total_cycles)*total_hours
        if (elapsed_hours - hour) >= reframe_threshold:
            print('{}: Reoptimizing trading strategy...'.format(str(t)))
            t += 1
            hour = hour + 1.0
            history_pd, history_array = get_historic_data(pair=pair, granularity=granularity)
            reframed = reframe_data(history_pd)
            best_strategy = optimize_strategy(reframed, buy_range = (1.0, 4.0, 0.25), risk_range=(1.0, 4.0, 0.25), chandelier=False)

        # Check crypto status
        output = get_product_data(pair)
        iteration = 0
        while output['status'] != 'online':
            print('{}: Crypto status error. Waiting...'.format(str(round(t))))
            t += 1
            print('Waiting for {} seconds...'.format(str(granularity)))
            time.sleep(granularity)
            cycle += 1
            history_array, buy_point, sell_point = iterate_signal(history_array, best_strategy, pair=pair, granularity=granularity, chandelier=chandelier)
            output = get_product_data(pair)
            iteration += 1
            if iteration == 10:
                print('{}: Crypto availability timeout...try again later.'.format(str(round(t))))
                t += 1
                running = False
            continue
        
        # Iterate price array
        history_array, buy_point, sell_point = iterate_signal(history_array, best_strategy, pair=pair, granularity=granularity, chandelier=chandelier)

        if sell_point:
            balance = get_currency_balance('BTC', key, secret, passphrase)
            if balance > float(output['base_min_size']):
                response = make_trade(pair, balance, 'sell', key, secret, passphrase)
                print('{}: Sold {} crypto.'.format(str(t), str(balance)))
                t += 1
            else:
                print('{}: No crypto to sell.'.format(str(t)))
                t += 1
                
        elif buy_point:
            balance = get_currency_balance('USD', key, secret, passphrase)
            if balance > 6.0:  # Since the minimum buy amount is subject to change in the future this is a hotfix, and could be better solved by doing base_min_size * current_BTC_price
                tender = round((1.0-cash_buffer)*balance,2)
                response = make_trade(pair, tender, 'buy', key, secret, passphrase)
                print('{}: Purchased BTC for ${}.'.format(str(t), str(round(tender,2))))
                t += 1
            else:
                print('{}: Not enough fiat to buy.'.format(str(t)))
                t += 1
        
        else:
            print('{}: No transaction point this iteration.'.format(str(t)))
            t += 1
        
        print('Waiting for {} seconds...'.format(str(granularity)))
        time.sleep(granularity)
        cycle += 1
        history_array, buy_point, sell_point = iterate_signal(history_array, best_strategy, pair=pair, granularity=granularity, chandelier=chandelier)
        
        # Check transaction status
        cleared = check_order_status(response, key, secret, passphrase)
        while cleared == False:
            print('{}: Still waiting for transaction to settle...'.format(str(t)))
            t += 1
            print('Waiting for {} seconds...'.format(str(granularity)))
            time.sleep(granularity)
            cycle += 1
            history_array, buy_point, sell_point = iterate_signal(history_array, best_strategy, pair=pair, granularity=granularity, chandelier=chandelier)
            cleared = check_order_status(response, key, secret, passphrase)
            continue
        
        running = True
        continue
    
    print('{}: Session terminated.'.format(str(t)))
