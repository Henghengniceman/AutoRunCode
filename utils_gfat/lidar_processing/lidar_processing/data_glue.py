# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 11:00:49 2020

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function：

"""
import numpy as np
import sys
import os 
MODULE_DIR = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, MODULE_DIR)
import utils_gfat.lidar_processing.lidar_processing.helper_functions as helper_functions

# from numba import jit

# from numba import cfunc
# @cfunc("float64(float64, float64,float64)")
# @jit(nopython=True) 
def data_glue(AnalogData,PhotoncountingData,GlueRangeIndex):
    """
    glue photoncounting data,default glue window length:200 bins
    
    Parameters
    ----------
    
    AnalogData :  Data from analog channel 
        A 1-D array of real values.
    
    PhotoncountingData: Data from Photoncounting channel 
        A 1-D array of real values.
        
    GlueRangeIndex : glue window centralindex
        Type:double. value 
        
    """
    # abstract background
    PhotoncountingData= PhotoncountingData-np.mean(PhotoncountingData[-499:])# abstract background
    AnalogData= AnalogData-np.mean(AnalogData[-499:])# abstract background
    # dead time correction 
    PhotoncountingData = PhotoncountingData/(1-PhotoncountingData*3.8e-3)
    # glue data
    GlueIndexMin=GlueRangeIndex-100
    GlueIndexmax=GlueRangeIndex+100
    a,b,r=helper_functions.linefit(AnalogData[GlueIndexMin:GlueIndexmax],PhotoncountingData[GlueIndexMin:GlueIndexmax])
    AnalogDataCorr=AnalogData*a
    GlueData = np.hstack((AnalogDataCorr[0:int((GlueIndexMin+GlueIndexmax)/2)],PhotoncountingData[int((GlueIndexMin+GlueIndexmax)/2):]))
    # AnalogDataCorrS=list(AnalogDataCorr[0:int((GlueIndexMin+GlueIndexmax)/2)])
    # PhotoncountingDataS=list(PhotoncountingData[int((GlueIndexMin+GlueIndexmax)/2):])
    # AnalogDataCorrS.extend(PhotoncountingDataS)
    # GlueData=np.array(AnalogDataCorrS)
    # GlueData = PhotoncountingData
    return GlueData