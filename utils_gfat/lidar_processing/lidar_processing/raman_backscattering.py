# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 17:21:26 2020

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function： calculate backscattering from Raman channel 

"""
import math
import numpy as np
import matplotlib.pyplot as plt
def raman_backscattering(Range,ElasticRaw,RamanRaw,R_zc,RangeIndex,CorrectionAerosolAlpha,AlphaMol,AlphaNMol):
    """
    Calcute aerosol backscattering coeffient using Raman method 
    ----------
   
    Parameters
    ----------
    Range : attitude 
        A 1-D array of real values.
        
    ElasticRaw : Elastic lidar Raw signal 
        A 1-D array of real values.
        
    RamanRaw : Raman lidar Raw signal  
        A 1-D array of real values.
        
    R_zc : reference value  
        1 for free of aerosol 
        
    RangeIndex : reference height index 
        Type:int
            
    CorrectionAerosolAlpha: extinction coecifient for calculating differential AOD 
        A 1-D array of real values.
        
    AlphaMol: extinction coecifient of molecule @ 355nm  
        A 1-D array of real values.
        
    AlphaNMol: extinction coecifient of molecule @ 386.8nm  
        A 1-D array of real values.
    """
    
    lamdaN=386.8
    lamda=355
    Sm=8*math.pi/3
    BetaMol =AlphaMol/Sm
    NBetaMol=BetaMol*0.78  # NbetaMol = betaMol*0.78; betaMolN is betaMol at 386.7;

    CorrectionAerosolAlphaN=CorrectionAerosolAlpha*(lamda/lamdaN)
    CorrectionAerosolAlpha = np.hstack((CorrectionAerosolAlpha,np.zeros(len(AlphaMol)-len(CorrectionAerosolAlpha))))
    CorrectionAerosolAlphaN = np.hstack((CorrectionAerosolAlphaN,np.zeros(len(AlphaMol)-len(CorrectionAerosolAlphaN))))
    AlphaTotalRA = CorrectionAerosolAlpha+AlphaMol[0:len(CorrectionAerosolAlpha)]
    AlphaNTotalRA=CorrectionAerosolAlphaN+AlphaNMol[0:len(CorrectionAerosolAlphaN)]
    AOD=[]
    AODN=[]
    Z_ref_min = int(RangeIndex-50)
    Z_ref_max = int(RangeIndex+50)
    Ref_height=int(RangeIndex)
    for i in range(0,int(len(Range))):
        #i=0
        AOD.append(np.nansum(AlphaTotalRA[i:Ref_height])*(Range[1]-Range[0]))
        AODN.append(np.nansum(AlphaNTotalRA[i:Ref_height])*(Range[1]-Range[0]))
   
    AOD=np.array(AOD)
    AODN=np.array(AODN)
    # fig = plt.figure(figsize=(5,6),dpi=120)
    # with plt.style.context(['science','no-latex']):
    #     ax = fig.add_subplot(1,1,1)
        
    #     ax.plot(AOD,Range, label='Elastic') 
    #     ax.plot(AODN,Range, label='N') 
    
    Transimission = np.exp(AOD)
    TransimissionN = np.exp(AODN)
    
    Differential_transimission = TransimissionN / Transimission
    BetaAero = R_zc*np.mean(BetaMol[Z_ref_min-1:Z_ref_max])*((np.mean(RamanRaw[Z_ref_min-1:Z_ref_max])*ElasticRaw*NBetaMol)/(np.mean(ElasticRaw[Z_ref_min-1:Z_ref_max])*RamanRaw*np.mean(NBetaMol[Z_ref_min-1:Z_ref_max])))

    BetaAero=BetaAero*Differential_transimission
    
    
    # fig = plt.figure(figsize=(5,6),dpi=120)
    # with plt.style.context(['science','no-latex']):
    #     ax = fig.add_subplot(1,1,1)
       
    #     ax.plot(BetaAero[0:2000]*1e6,Range[0:2000]/1000, label='Elastic') 
    #     ax.plot(BetaMol[0:2000]*1e6,Range[0:2000]/1000, label='Elastic') 
    #     ax.set_xlim(0,30)
    #     ax.set_xlim(0,15)
    BetaAero = BetaAero-BetaMol

    
    return BetaAero

