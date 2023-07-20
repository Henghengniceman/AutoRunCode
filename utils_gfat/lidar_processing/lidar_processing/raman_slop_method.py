# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 13:44:57 2020

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function： calculate extinction from raman Slop method

"""
import math
import numpy as np
import os
import sys
MODULE_DIR = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, MODULE_DIR)
import utils_gfat.lidar_processing.lidar_processing.helper_functions as helper_functions

def raman_slop_method(Range,RCSData,betaMol,betaMolN,Interval=10):
    """
    Calcute extinction coefficient using Slop method
    
    Parameters
    ----------
    
    Range :  attitude 
        A 1-D array of real values.
    
    RCSData: Range corrected lidar singal 
        A 1-D array of real values.
        
    betaMol: Molecule backscattering coefficient @ 355 nm
        A 1-D array of real values.    
        
    betaMol: Molecule backscattering coefficient @ 386.7 nm
        A 1-D array of real values.       
        
    """
    
    NbetaMol=betaMol*0.78  # NbetaMol = betaMol*0.78; betaMolN is betaMol at 386.7;
    Sm=8*math.pi/3
    lamda=355
    lamdaN=386.8
    AlphaMol = Sm*betaMol
    AlphaMolN = Sm*betaMolN 
    # creat empty list
    Slop = []
    AlphaMolSelect=[]
    AlphaMolNSelect=[]
    # parameter 1
    Para1 = np.log(NbetaMol/RCSData)

    for i in range(1,int(np.floor(len(RCSData)/Interval))+1):
        a,b,r=helper_functions.linefit(Range[(i-1)*Interval:i*Interval],Para1[(i-1)*Interval:i*Interval])
        Slop.append(a)        
        AlphaMolSelect.append(np.mean(AlphaMol[(i-1)*Interval:i*Interval]))
        AlphaMolNSelect.append(np.mean(AlphaMolN[(i-1)*Interval:i*Interval]))
    RangeSelect = Range[int(np.floor(Interval/2))-1:-5:Interval]
    Slop=np.array(Slop)
    AlphaMolSelect=np.array(AlphaMolSelect)
    AlphaMolNSelect=np.array(AlphaMolNSelect)
    AlphaAero=(Slop-AlphaMolSelect-AlphaMolNSelect)/(1+lamda/lamdaN) 
    return RangeSelect,AlphaAero
    
            
