# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 17:55:54 2022

@author: ka1319
"""
from datetime import datetime
import numpy as np

def merge_polarized_channels(signal_p,signal_s):
    calib = {'date': datetime(2018, 2, 5), 'eta_an': 0.763297, 'eta_pc': 0.763297,'eta': 0.763297, 'GR': 1.00000, 'GT': 1.00000, 'HR': 0.95621, 'HT': -0.95629, 'K': 22.5} #Considering y = - 1 i.e., parallel in R. 
    signal_merge = np.abs((calib['eta']/ calib['K']) * calib['HR'] * signal_s - calib['HT'] * signal_p)
    eta = calib['eta'] / calib['K']
    ratio = (signal_p / signal_s) / eta
    lvdr = ((calib['GT'] + calib['HT']) * ratio - (calib['GR'] + calib['HR'])) / ((calib['GR'] - calib['HR']) - (calib['GT'] - calib['HT']) * ratio)
    
    return signal_merge,lvdr