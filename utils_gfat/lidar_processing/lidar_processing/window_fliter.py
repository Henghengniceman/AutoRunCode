# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 11:44:11 2020

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function：

"""
import numpy as np
import math
from numba import jit


@jit(nopython=True) 
def window_fliter(RawSignal, name='Hamming', N=20):
    """
    window filter to smooth signal 
    
    Parameters
    ----------
    
    RawSignal : Lidar raw singal 
        A 1-D array of real values.
        
    name: select window type 
        value --- > string 
        'Hamming' ---> Hamming window  
        'Hanning'--> Hanning window
        'Rect'--> rectangle window
        
    N: window length -- Keyword Arguments
       type: int
        
    """
    
    # Rect/Hanning/Hamming
    # RawSignal = RawSignal - np.nanmean(RawSignal[-500:])
    if name == 'Hamming':
        WindowParameter = np.array([0.54 - 0.46 * np.cos(2 * np.pi * n / (N - 1)) for n in range(N)])
    elif name == 'Hanning':
        WindowParameter = np.array([0.5 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) for n in range(N)])
    elif name == 'Rect':
        WindowParameter = np.ones(N)
        
    WindowParameter=WindowParameter/np.sum(WindowParameter) # Normalized window parameter 
    SingalLen=len(RawSignal)
    Window_length=len(WindowParameter)
    Outputsignal=np.zeros((SingalLen,))
    # apply window filter 
    for i in range(math.ceil(Window_length/2),SingalLen-math.floor(Window_length/2)):
        for j in range(1,Window_length):
            Outputsignal[i] = Outputsignal[i]+RawSignal[i-math.ceil(Window_length/2)+j]*WindowParameter[j]           
    Outputsignal[0:math.floor(Window_length/2)+1] = RawSignal[0:math.floor(Window_length/2)+1]
    Outputsignal[-1*math.floor(Window_length/2):]=RawSignal[-1*math.floor(Window_length/2):]
    return Outputsignal  
        

