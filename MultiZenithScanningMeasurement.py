# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 14:26:54 2022

@author: ka1319
"""
# import os 
import numpy as np
import pandas as pd 
# import FunctionModel
# import matplotlib.pyplot as plt
# from tqdm import tqdm
# from ReadLicel import ReadLicel
# from Src.DataGlue import DataGlue
# from Src.window_fliter import window_fliter
# import math 
# from Src.BackwardAeroFernald import BackwardAeroFernald
# import pandas as pd
# import pdb
# from utils_gfat.backward_aero_fernald import backward_aero_fernald

from ZenithScanningMeasurement import ZenithScanningMeasurement


class MultiZenithScanningMeasurement(ZenithScanningMeasurement):
    def __init__(self,TimeFolderDir,ConfigInfo):
        super(MultiZenithScanningMeasurement,self).__init__(TimeFolderDir,ConfigInfo)
    def GroupData(self):
        self.FileInEachGroup = len(set(self.Zenith))
        self.GroupNumber = int(len(self.Zenith)/self.FileInEachGroup)
        self.GlueRawAll = self.GlueRaw
        self.ZenithAll = self.Zenith
        self.AzimuthAll = self.Azimuth
        self.TimeFolderDirAll = self.TimeFolderDir
        self.DateTimeAll = self.DateTime
        # import pdb
        # pdb.set_trace()
        # print(self.FileInEachGroup)
        # print(self.GroupNumber)
    def ShowRCSProfiles(self):
        for i in range(self.GroupNumber):
            self.GlueRaw = self.GlueRawAll[:,i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.Zenith = self.ZenithAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.TimeFolderDir = self.TimeFolderDirAll+'_'+str(i)
            ZenithScanningMeasurement.ShowRCSProfiles(self)
    def ShowRCSPolar(self):
        for i in range(self.GroupNumber):
            self.GlueRaw = self.GlueRawAll[:,i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.Zenith = self.ZenithAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.TimeFolderDir = self.TimeFolderDirAll+'_'+str(i)
            ZenithScanningMeasurement.ShowRCSPolar(self)
    def AeroFernald(self):
        self.BetaAeroAll = []
        for i in range(self.GroupNumber):
            self.GlueRaw = self.GlueRawAll[:,i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.Zenith = self.ZenithAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.DateTime = self.DateTimeAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.TimeFolderDir = self.TimeFolderDirAll+'_'+str(i)
            ZenithScanningMeasurement.AeroFernald(self)
            self.BetaAeroAll.append(self.BetaAeros)
            self.BetaAeros = []
    def ShowBetaProfiles(self):
        for i in range(self.GroupNumber):
            self.GlueRaw = self.GlueRawAll[:,i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.BetaAeros = self.BetaAeroAll[i]
            self.Zenith = self.ZenithAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.TimeFolderDir = self.TimeFolderDirAll+'_'+str(i)
            ZenithScanningMeasurement.ShowBetaProfiles(self)
    def ShowBetaPolar(self):
        for i in range(self.GroupNumber):
            self.BetaAeros = self.BetaAeroAll[i]
            self.Zenith = self.ZenithAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.TimeFolderDir = self.TimeFolderDirAll+'_'+str(i)
            ZenithScanningMeasurement.ShowBetaPolar(self)
    def SaveBeta(self):
        for i in range(self.GroupNumber):
            self.BetaAeros = self.BetaAeroAll[i]
            self.Zenith = self.ZenithAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.Azimuth = self.AzimuthAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.TimeFolderDir = self.TimeFolderDirAll+'_'+str(i)
            self.DateTime = self.DateTimeAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            ZenithScanningMeasurement.SaveBeta(self)
    def ShowDepolarizationProfiles(self):
        self.DepolarizationRatioAll = self.DepolarizationRatio
        for i in range(self.GroupNumber):
            self.TimeFolderDir = self.TimeFolderDirAll+'_'+str(i)
            self.DepolarizationRatio = self.DepolarizationRatioAll[:,i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            ZenithScanningMeasurement.ShowDepolarizationProfiles(self)
    def ShowDepolarizationPolar(self):
        for i in range(self.GroupNumber):
            self.TimeFolderDir = self.TimeFolderDirAll+'_'+str(i)
            self.DepolarizationRatio = self.DepolarizationRatioAll[:,i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.Zenith = self.ZenithAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            ZenithScanningMeasurement.ShowDepolarizationPolar(self)
    def SaveDepolarization(self):
        for i in range(self.GroupNumber):
            self.Zenith = self.ZenithAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.Azimuth = self.AzimuthAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.TimeFolderDir = self.TimeFolderDirAll+'_'+str(i)
            self.DateTime = self.DateTimeAll[i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            self.DepolarizationRatio = self.DepolarizationRatioAll[:,i*self.FileInEachGroup:(i+1)*self.FileInEachGroup]
            ZenithScanningMeasurement.SaveDepolarization(self)
    def GetContourfData(self):
        BetaAeroVertical = []
        DepolarizationRatioVertical = []
        DateTime = []
        for i in range(self.GroupNumber):
            BetaAeroVertical.append(self.BetaAeroAll[i][:,0])
            DepolarizationRatioVertical.append(self.DepolarizationRatioAll[:,i*self.FileInEachGroup])
            DateTime.append(self.DateTimeAll[i*self.FileInEachGroup])
        BetaAeroVertical = np.array(BetaAeroVertical).T
        DepolarizationRatioVertical = np.array(DepolarizationRatioVertical).T
        if self.Zenith[0] == 90:
            BetaSet = pd.DataFrame(data = BetaAeroVertical[0:self.ReferenceIndex,:],index = self.Range[0:self.ReferenceIndex],columns = DateTime)
            DeltaSet = pd.DataFrame(data = DepolarizationRatioVertical[0:self.ReferenceIndex,:],index = self.Range[0:self.ReferenceIndex],columns = DateTime)
        return BetaSet,DeltaSet
           
        
        