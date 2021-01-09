#!/usr/bin/env python3
"""
Created on Sat Jan  9 09:35:49 2021

@author: metalcorebear
"""

import parameters
import helper_monkey as mojo

if __name__ == '__main__':
    mojo.main(parameters.API_KEY, pair=parameters.pair, granularity=parameters.granularity, duration=parameters.duration, cash_buffer=parameters.cash_buffer, reframe_threshold=parameters.reframe_threshold, continuous=parameters.continuous, chandelier=parameters.chandelier)