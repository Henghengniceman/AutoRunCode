# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 09:52:46 2020

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function： get molecule backscattering 

"""
# import numpy as np
# import math
# from datetime import datetime
# from nrlmsise00 import msise_flat
# def MoleculeScatter(baseLatitude,baseLongitude,Height,DateTime,TemperatureRA=np.nan,PressureRA=np.nan,InputSelection='atmos_model',lamda=355):
#     """
#     Calcute molecule scattering
#     ----------
    
#     1. InputSelection='atmos_model' ---> from stand atmosphere model 
    
#     2. InputSelection='radio_sonde' ---> from radio sonde data
    
#     3. lamda ---> specify the wavelength to calculate

#     Parameters
#     ----------
    
#     baseLatitude : observation station attitude 
#         A 1-D array of real values.
        
#     baseLongitude : observation station Longitude 
#         A 1-D array of real values.
        
#     DateTime : observation time 
#         Type: datetime 
        
#     TemperatureRA : tempreature from  radiosonde -- Keyword Arguments
#         A 1-D array of real values.
        
#     PressureRA : Pressure from  radiosonde -- Keyword Arguments
#         A 1-D array of real values.
    
#     InputSelection: select atmoshere source 
#         value --- > string 
#         'stmos_model' ---> stand atmosphere model  
#         'radio_sonde'--> radio sonde data  
        
#     lamda: specify the wavelenth to calculate 
#         value --- > double 
#         355 ---> elstic channel 
#         386.8 --> Raman channel 
#     """
    
    
#     k=1.38e-23
#     Ns_constant= 3.62845e-8
#     Ns_constantN= 3.57125e-8
#     Fk = 1.05289
#     FkN = 1.05166
#     Ns = 2.5477e25
#     if InputSelection=='atmos_model':      
#         #MsiseOut=msise_flat(datetime(int(DateTime[0:4]), int(DateTime[4:6]), int(DateTime[6:8]), int(DateTime[8:10]), int(DateTime[10:12]), int(DateTime[12:14])), Height/1000, baseLatitude, baseLongitude, 150, 150, 4)
#         MsiseOut=msise_flat(DateTime, Height/1000, baseLatitude, baseLongitude, 150, 150, 4)
#         Nair=np.sum(MsiseOut[:,0:9],axis = 1)
#         #Nair = MsiseOut[0,:,10]
#         Nair=Nair*math.pow(10,6)
#         if lamda==355:
#             betaMol = Nair*((9*np.square(math.pi))/(math.pow(lamda*math.pow(10,-9),4)*np.square(Ns)))*Ns_constant*Fk
#         elif lamda== 386.8:
#             betaMol = Nair*((9*np.square(math.pi))/(math.pow(lamda*math.pow(10,-9),4)*np.square(Ns)))*Ns_constantN*FkN
#     elif InputSelection=='radio_sonde':        
#         ppRA=PressureRA*100
#         NairRA=ppRA/(k*TemperatureRA)
#         if lamda==355:
#             betaMol = NairRA*((9*np.square(math.pi))/(math.pow(lamda*math.pow(10,-9),4)*np.square(Ns)))*Ns_constant*Fk
#         elif lamda==386.8:
#             betaMol = NairRA*((9*np.square(math.pi))/(math.pow(lamda*math.pow(10,-9),4)*np.square(Ns)))*Ns_constantN*FkN
#     return  betaMol 



import numpy as np
import math
import utils_gfat.lidar_processing.lidar_processing.helper_functions as helper_functions
from utils_gfat import lidarQA
# import matplotlib.pyplot as plt
# import pdb
# from nrlmsise00 import msise_flat

def molecule_scatter(baseLatitude,baseLongitude,Height,DateTime,TemperatureRA=np.nan,PressureRA=np.nan,InputSelection='atmos_model',lamda=355):
    """
    Calcute molecule scattering
    ----------
    
    1. InputSelection='atmos_model' ---> from stand atmosphere model 
    
    2. InputSelection='radio_sonde' ---> from radio sonde data
    
    3. lamda ---> specify the wavelength to calculate

    Parameters
    ----------
    
    baseLatitude : observation station attitude 
        A 1-D array of real values.
        
    baseLongitude : observation station Longitude 
        A 1-D array of real values.
        
    DateTime : observation time 
        Type: datetime 
        
    TemperatureRA : tempreature from  radiosonde -- Keyword Arguments
        A 1-D array of real values.
        
    PressureRA : Pressure from  radiosonde -- Keyword Arguments
        A 1-D array of real values.
    
    InputSelection: select atmoshere source 
        value --- > string 
        'stmos_model' ---> stand atmosphere model  
        'radio_sonde'--> radio sonde data  
        
    lamda: specify the wavelenth to calculate 
        value --- > double 
        355 ---> elstic channel 
        386.8 --> Raman channel 
    """
    
    
    k=1.38e-23
    Parameters_molecule ={355:[3.62845e-8,1.05289],
                          386.8:[3.57125e-8,1.05166],
                          532:[3.44032E-08,1.000278235],
                          1064: [3.33502E-08,1.000273943]
        }
    # Ns_constant= 3.62845e-8
    # Ns_constantN= 3.57125e-8
    # Fk = 1.05289
    # FkN = 1.05166
    Ns = 2.5477e25
    if InputSelection=='atmos_model':   
        
        temperature_prf = np.ones(Height.size)*np.nan
        pressure_prf = np.ones(Height.size)*np.nan
        for i, _height in enumerate(Height):
            sa = helper_functions.standard_atmosphere(_height)
            pressure_prf[i] = sa[0]
            temperature_prf[i] = sa[1]
        molp = lidarQA.molecular_properties(355, pressure_prf,temperature_prf,Height)
        betaMol = molp['molecular_beta'].values
        #MsiseOut=msise_flat(datetime(int(DateTime[0:4]), int(DateTime[4:6]), int(DateTime[6:8]), int(DateTime[8:10]), int(DateTime[10:12]), int(DateTime[12:14])), Height/1000, baseLatitude, baseLongitude, 150, 150, 4)
        # MsiseOut=msise_flat(DateTime, Height/1000, baseLatitude, baseLongitude, 150, 150, 4)
        # Nair=np.sum(MsiseOut[:,0:5],axis = 1)+np.sum(MsiseOut[:,6:9],axis = 1)
        # print(Nair)
        # print(MsiseOut[0,0])
        # print(MsiseOut[0,5])
        # print(MsiseOut[0,9])

        #Nair = MsiseOut[0,:,10]
        # Nair=Nair*math.pow(10,6)
        # betaMol = Nair*((9*np.square(math.pi))/(math.pow(lamda*math.pow(10,-9),4)*np.square(Ns)))*Parameters_molecule[lamda][0]*Parameters_molecule[lamda][1]
        # plt.plot(Height,betaMol1)
        # plt.plot(Height,betaMol)
        # pdb.set_trace()
    elif InputSelection=='radio_sonde':        
        ppRA=PressureRA*100
        NairRA=ppRA/(k*TemperatureRA)
        # betaMol = NairRA*((9*np.square(math.pi))/(math.pow(lamda*math.pow(10,-9),4)*Parameters_molecule[lamda][0]*Parameters_molecule[lamda][1]
        betaMol = NairRA*((9*np.square(math.pi))/(math.pow(lamda*math.pow(10,-9),4)*np.square(Ns)))*Parameters_molecule[lamda][0]*Parameters_molecule[lamda][1]

    return  betaMol