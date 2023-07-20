# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 12:24:34 2021

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function：ForwardAeroFernald

"""
import numpy as np
import math 
import sys
import os 
MODULE_DIR = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, MODULE_DIR)
from utils_gfat.lidar_processing.lidar_processing.molecule_scatter import molecule_scatter
# from Src.MoleculeScatter import MoleculeScatter
# from Src.forward_integration_backscatter import forward_integration_backscatter
from utils_gfat import lidar_elastic_retrieval

#%% Geographic information 
GeographicInformation ={'Karlsruhe':[119,49.0953,8.4298],
                        'Stuttgart':[247,48.7986,9.2024],
                        'Julich':[110,50.9084,6.4131]}
class forward_aero_fernald:
    # Sm=8*math.pi/3
    # R_zc = 1

    def __init__(self,DataInformation,StationGeoInfo): 
        
        """
            Parameter initialization
            
            Parameters
            ----------
            
            Sm: ratio of extinction to backscattering coefficient [molecule]
            R_zc: reference backscattering ratio 
            Sa: ratio of extinction to backscattering coefficient [aerosol] 
            ReferenceHeight: Reference Height in Unit [m]
        """
        self.Sm=8*math.pi/3
        self.Range = DataInformation['Range']
        self.Attitude =DataInformation['Attitude']
        self.Data = DataInformation['Data']
        self.Date = DataInformation['Date']
        self.RangeIndex = np.floor(DataInformation['ReferenceHeight']/(self.Range[1]-self.Range[0]))
        # self.UpperRangeIndex = np.floor(DataInformation['UpperReferenceHeight']/(self.Range[1]-self.Range[0]))
        self.ReferenceHeight = DataInformation['ReferenceHeight']
        # self.UpperReferenceHeight = DataInformation['UpperReferenceHeight']
        self.Sa = DataInformation['Sa']
        self.R_zc = DataInformation['R_zc']
        self.baseAlt = StationGeoInfo['altitude']                              
        self.baseLongitude=StationGeoInfo['longitude'] 
        self.baseLatitude=StationGeoInfo['latitude']   
   

        
    # def setGeographicInformation(self,ObservationSite): 
    #     """
    #         Set Geographic Information
            
    #         Parameters
    #         ----------
            
    #         ObservationSite : observation Site name 
    #             Type: dict 
    #             Dict_Key: site name <Karlsruhe,Stuttgart,Stuttgart>
    #             Dict_Value: list [Attitude,Latitude,longitude]  
    #     """
    #     self.baseAlt = GeographicInformation[ObservationSite][0]                              
    #     self.baseLatitude=GeographicInformation[ObservationSite][1]                          
    #     self.baseLongitude=GeographicInformation[ObservationSite][2] 
        
        
        
    # def setDataInformation(self,DataInformation):
        
    #     """
    #         Set Data Information
            
    #         Parameters
    #         ----------
    #         DataInformation: Range,attitude, RawData, DateTime
    #             Type: String Dict
    #             Dict_Key: data attitube; range, attitude,Rawdata, Datetime
    #             Dict_Value: the corresponding value 
    #     """
        
    #     self.Range = DataInformation['Range']
    #     self.Attitude =DataInformation['Attitude']
    #     self.Data = DataInformation['Data']
    #     self.Date = DataInformation['Date']
    #     self.RangeIndex = np.floor(DataInformation['ReferenceHeight']/(self.Range[1]-self.Range[0]))
    #     self.UpperRangeIndex = np.floor(DataInformation['UpperReferenceHeight']/(self.Range[1]-self.Range[0]))
    #     self.Sa = DataInformation['Sa']
    #     self.R_zc = DataInformation['R_zc']
      
    def setRadioSonderData(self,RadionSondeData):
        """
            Set Radio Data Information
            
            Parameters
            ----------
            DataInformation: Temperature,Pressure
                Type: String Dict
                Dict_Key: data attitube; Temperature,Pressure
                Dict_Value: the corresponding value 
        """
        
        self.Temperature = RadionSondeData['Temperature']
        self.Pressure = RadionSondeData['Pressure']
 
    def __call__(self,Use_Radio_Sonde = False):
        """
            Calculate Molecule Scatter and Aerosol Scatter 
            
            Parameters
            ----------
            DataInformation: 
                Type: bool: True --> radiosonde, False --> standard atmosphere model. 
                Default:False 

        """
        #%% Range Corrected 
        
        self.RCS = self.Data*np.square(self.Range)
        
        #%% Calculate Molecule
        if Use_Radio_Sonde:
            self.BetaMol = molecule_scatter(self.baseLatitude,self.baseLongitude,self.Attitude+self.baseAlt,self.Date,
                                          TemperatureRA=self.Temperature,PressureRA=self.Pressure,
                                          InputSelection='radio_sonde')
        else:
            self.BetaMol = molecule_scatter(self.baseLatitude,self.baseLongitude,self.Attitude+self.baseAlt,self.Date)
       
        self.AlphaMol = self.BetaMol*self.Sm
        
        ## Calculate Aerosol Backscattering 
        # self.BetaAero=forward_integration_backscatter(self.Sa,self.Sm,self.R_zc,self.RangeIndex,self.UpperRangeIndex,self.Range,self.AlphaMol,self.RCS)    
        self.BetaAero = lidar_elastic_retrieval.klett_forward(self.RCS, self.Range, self.BetaMol, self.Sm,
                              lr_aer = self.Sa, ymin = self.ReferenceHeight - 250, ymax = self.ReferenceHeight + 250,aerosol_backscatter_at_reference=(self.R_zc-1))


        # print(self.UpperRangeIndex)
    # def calMoleculeAlpha(self):
    #     """
    #         Calculate Molecule Extinction
            
    #     """
        
    # def calculateAeroBeta(self):
    #     """
    #         Calculate Aerosol backacattering coefficient
            
    #     """

    def getAeroBeta(self):
        """
            get Aerosol backacattering coefficient
            
        """
        return self.BetaAero
       