# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 12:21:55 2021

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function： work flow of data analysis

"""
from datetime import datetime
import os 
from ZenithScanningMeasurement import ZenithScanningMeasurement
from AzimuthScanningMeasurement import AzimuthScanningMeasurement
from FixedPointMeasurement import FixedPointMeasurement
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tqdm import tqdm 
import pdb
# from numba import jit

def ShowZenithContourf(BetaSets,DeltaSets):
    Range = np.array(list(BetaSets.index))
    BetaDateTime = list(BetaSets.columns)
    Betas = BetaSets.values
    Deltas = DeltaSets.values
    DeltaDatetime = list(DeltaSets.columns)
    
    if not os.path.exists(('../Figure/Contourf/')):
           os.makedirs(('../Figure/Contourf/'))
    #%%
    Betas = Betas * 1e6
    Betas = np.where(Betas>15,15,Betas)
    Betas = np.where(Betas<0,0,Betas)
    
    
    Deltas = Deltas*100
    Deltas = np.where(Deltas>20,20,Deltas)
    Deltas = np.where(Deltas<0,00,Deltas)
    Deltas = Deltas[0:1333,:]
    LIDARDatas = xr.Dataset(
                         {
                           "Beta":(("range",'betatime'),Betas),
                           "Delta":(("range",'deltatime'),Deltas),
                         },
                           coords={"range": list(Range/1000),"betatime": list(BetaDateTime),"deltatime": list(DeltaDatetime)}, 
                        )        
    Betada = LIDARDatas.Beta
    Deltada = LIDARDatas.Delta
    Date = BetaDateTime[0].strftime('%Y-%m-%d') +'-'+ BetaDateTime[-1].strftime('%Y-%m-%d')
    Betada = LIDARDatas.Beta
    Deltada = LIDARDatas.Delta
    fontdicts={'weight': 'bold', 'size': 18}
    fig, axes = plt.subplots(2, 1,sharex = True,figsize=(16, 12))   
    cs = Betada.plot.contourf(
            ax=axes[1],
            vmin = 0,
            vmax = 15,
            # y="Range",
            levels=13,
            robust=True,
            cmap = 'jet',
            add_colorbar=False,
                      )
    #colorbar 左 下 宽 高 
    l = 0.92
    b = 0.1
    w = 0.015
    h = 0.38
    #对应 l,b,w,h；设置colorbar位置；
    rect = [l,b,w,h] 
    cbar_ax = fig.add_axes(rect) 
    cb = plt.colorbar(cs, cax=cbar_ax)
    cb.set_label('Back.coe. [$\mathregular{m^-}$$\mathregular{^1}$$\mathregular{Sr^-}$$\mathregular{^1}$]' ,fontdict=fontdicts,labelpad =25 ) #设置colorbar的标签字体及其大小
    # set parameter of axis 
    # axes[1].set_xlim(datetime.strptime(Date,'%Y-%m-%d'),datetime.strptime(Date,'%Y-%m-%d')+timedelta(days=1))
    axes[1].set_ylim(0,4)
    axes[1].set_ylabel('Attitude [Km]',fontdict=fontdicts,labelpad = 25)
    for tick in axes[0].yaxis.get_major_ticks():
            tick.label.set_fontsize(12)   
    axes[1].set_yticks(np.arange(0,4))
    axes[1].set_xlabel(('Measurement Time ['+Date+'], UTC'),fontdict=fontdicts,labelpad = 12.5)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    
    for tick in axes[1].xaxis.get_major_ticks():
        tick.label.set_fontsize(15) 
    for tick in axes[1].yaxis.get_major_ticks():
        tick.label.set_fontsize(15) 
    plt.setp(axes[1].get_xticklabels(), rotation=0)        
    
    cs = Deltada.plot.contourf(
            ax=axes[0],
            vmin = 0,
            vmax = 20,
            # y="Range",
            levels=13,
            robust=True,
            cmap = 'jet',
            add_colorbar=False,
                  )
    #color bar
    #colorbar 左 下 宽 高 
    l = 0.92
    b = 0.50
    w = 0.015
    h = 0.38
    #对应 l,b,w,h；设置colorbar位置；
    rect = [l,b,w,h] 
    cbar_ax = fig.add_axes(rect) 
    cb = plt.colorbar(cs, cax=cbar_ax)
    cb.set_label('Depo.Rat. [%]' ,fontdict=fontdicts,labelpad =25 ) #设置colorbar的标签字体及其大小
    axes[0].set_ylim(0,4)
    
    # axes[0].set_title('February, 2021, KIT ',fontdict={'weight': 'bold', 'size': 20})
    axes[0].set_ylabel('Attitude [Km]',fontdict=fontdicts,labelpad = 25)
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    
    for tick in axes[0].yaxis.get_major_ticks():
            tick.label.set_fontsize(15) 
    axes[0].set_yticks(np.arange(0,4))
    plt.subplots_adjust(wspace=0, hspace=0,right=0.9)
    fig.savefig(('../Figure/Contourf/'+Date+'BetaAndDelta.jpg'),dpi=300)
    plt.close()  
    
def WriteLogFile(loginfo,Date,FileNameHead):
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    if not os.path.exists(('../' +Date+'/LogFile/')):
       os.makedirs(('../' +Date+'/LogFile/'))
    with open('../' +Date+'/LogFile/'+FileNameHead+now +'.log',"w") as f:
        print(loginfo,file = f)
        
class WorkFlow(object):
    def __init__(self,MainPath):
        self.ConfigInfo = {} 
        self.MainPath = MainPath
    def ReadConfigFile(self,ConfigFilePath):
        with open(ConfigFilePath) as f:
            lines = f.readlines()
            for line in lines [3:]:
                if len(line.split(':')) == 2:
                    try:
                        self.ConfigInfo.update({line.split(':')[0].replace(' ',''):float(line.split(':')[1])})
                    except:
                        self.ConfigInfo.update({line.split(':')[0].replace(' ',''):line.split(':')[1].replace(' ','')})

            for line in lines[:3]:
                if len(line.split(':')) == 2:
                    self.ConfigInfo.update({line.split(':')[0].replace(' ',''):datetime.strptime(line.split(':')[1].replace(' ','').replace('\n',' '), '%Y-%m-%d ')})    
        # log info
        self.loginfo = ''
        for line in lines:
            self.loginfo = self.loginfo+line
        # date 
        self.Date = self.ConfigInfo['StartDate'].strftime('%Y%m%d')
        self.MainPath = self.ConfigInfo['DataPath']
        # pdb.set_trace()
    # @jit()
    def ZenithScanning(self):
        print('\n-----ZenithScanning start-----\n')
        ZenithDataPaths =[]
        for year in os.listdir(self.MainPath):

            if year.startswith('20') and float(year) >= self.ConfigInfo['StartDate'].year and float(year) <= self.ConfigInfo['EndDate'].year:
                if os.path.exists((self.MainPath +'/' + year + '/Scanning_Measurements')):
                    for month in os.listdir(self.MainPath +'/' + year + '/Scanning_Measurements'):
                        if (month.startswith('0') or month.startswith('1')):
                            for day in os.listdir(self.MainPath +'/' + year + '/Scanning_Measurements/'+month):
                                if (day.startswith('0') or day.startswith('1') or day.startswith('2') or day.startswith('3')):
                                    # print(float(year+month+day))
                                    if float(year+month+day) >= float(self.ConfigInfo['StartDate'].strftime('%Y%m%d'))and float(year+month+day)  <= float(self.ConfigInfo['EndDate'].strftime('%Y%m%d')):
                                        for Time in os.listdir(self.MainPath +'/' + year + '/Scanning_Measurements/'+month+'/'+day):
                                            if Time.startswith('ZS'):
                                                ZenithDataPaths.append(self.MainPath +'/' + year + '/Scanning_Measurements/'+month+'/'+day+'/'+Time)
        BetaSets = pd.DataFrame()
        DeltaSets = pd.DataFrame()
        BetaRetrieved = 0
        DepolarizationRetrieved = 0
        # ZenithDataPaths = ZenithDataPaths[8:]
        for datepath in tqdm(ZenithDataPaths):
            ZSM = ZenithScanningMeasurement(datepath,self.ConfigInfo)
            ZSM.ReadData()
            # print(ZSM.FileNames != [])
            if ZSM.BinWidthCheck and ZSM.FileNames != []:
                ZSM.DataPreProcess()
                if self.ConfigInfo['Overlap']:
                    ZSM.OverlapCorrection()
                if self.ConfigInfo['RCSProfiles']:
                    ZSM.ShowRCSProfiles()
                if self.ConfigInfo['RCSPolar']:
                    ZSM.ShowRCSPolar()
                if self.ConfigInfo['BetaProfiles'] or self.ConfigInfo['BetaPolar'] or self.ConfigInfo['BetaData']:
                    ZSM.AeroFernald()
                    BetaRetrieved = 1
                if self.ConfigInfo['BetaProfiles']:
                    ZSM.ShowBetaProfiles()
                if self.ConfigInfo['BetaPolar']:
                    ZSM.ShowBetaPolar()
                if self.ConfigInfo['BetaData']:
                    ZSM.SaveBeta()
                if self.ConfigInfo['DeltaProfiles'] or self.ConfigInfo['DeltaPolar'] or self.ConfigInfo['DeltaData']:
                    ZSM.DepolarizationCal()
                    DepolarizationRetrieved = 1
                if self.ConfigInfo['DeltaProfiles']:
                    ZSM.ShowDepolarizationProfiles()
                if self.ConfigInfo['DeltaPolar']:
                    ZSM.ShowDepolarizationPolar()
                if self.ConfigInfo['DeltaData']:
                    ZSM.SaveDepolarization()
                #%% contour plot
                if self.ConfigInfo['ZenithContourf'] and BetaRetrieved and DepolarizationRetrieved:
                    BetaSet,deltaSet = ZSM.GetContourfData()   
                    BetaSets=pd.concat([BetaSets,BetaSet],axis=1)
                    DeltaSets=pd.concat([DeltaSets,deltaSet],axis=1)
                self.BetaSets = BetaSets
                self.DeltaSets = DeltaSets
            if self.ConfigInfo['ZenithContourf'] and BetaRetrieved and DepolarizationRetrieved and len(BetaSets.columns)>1:
                ShowZenithContourf(BetaSets,DeltaSets)
        if len(ZenithDataPaths)>0:
            loginfo = self.loginfo+'\n'+str(len(ZenithDataPaths))+' Groups Data was analysised'
            WriteLogFile(loginfo,self.Date,'ZS_')
        
    def AzimuthScanning(self):
        print('\n-----AzimuthScanning starts-----\n')
        AzimuthDataPaths =[]
        for year in os.listdir(self.MainPath):
            # print(year)
            if year.startswith('20') and float(year) >= self.ConfigInfo['StartDate'].year and float(year) <= self.ConfigInfo['EndDate'].year:
                if os.path.exists((self.MainPath +'/' + year + '/Scanning_Measurements')):
                     for month in os.listdir(self.MainPath +'/' + year + '/Scanning_Measurements'):
                        if (month.startswith('0') or month.startswith('1')):
                            for day in os.listdir(self.MainPath +'/' + year + '/Scanning_Measurements/'+month):
                                if (day.startswith('0') or day.startswith('1') or day.startswith('2') or day.startswith('3')):
                                    if float(year+month+day) >= float(self.ConfigInfo['StartDate'].strftime('%Y%m%d'))and float(year+month+day)  <= float(self.ConfigInfo['EndDate'].strftime('%Y%m%d')):
                                         for Time in os.listdir(self.MainPath +'/' + year + '/Scanning_Measurements/'+month+'/'+day):
                                            if Time.startswith('AS'):
                                                AzimuthDataPaths.append(self.MainPath +'/' + year + '/Scanning_Measurements/'+month+'/'+day+'/'+Time)
                
            
        for datepath in tqdm(AzimuthDataPaths):
            ASM = AzimuthScanningMeasurement(datepath,self.ConfigInfo)
            ASM.ReadData()
            if ASM.BinWidthCheck:
                ASM.DataPreProcess()
                if self.ConfigInfo['Overlap']:
                    ASM.OverlapCorrection()
                ASM.CalculateAndDrawRefernce()
                if self.ConfigInfo['RCSProfiles']:
                    ASM.ShowRCSProfiles()
                if self.ConfigInfo['RCSPolar']:
                    ASM.ShowRCSPolar()
                    ASM.ShowRCSPolarMap()
                if self.ConfigInfo['BetaProfiles'] or self.ConfigInfo['BetaPolar'] or self.ConfigInfo['BetaData']:
                    ASM.AeroFernald()
                if self.ConfigInfo['BetaProfiles']:
                    ASM.ShowBetaProfiles()
                if self.ConfigInfo['BetaPolar']:
                    ASM.ShowBetaPolar()
                    ASM.ShowBetaPolarMap()
                if self.ConfigInfo['BetaData']:
                    ASM.SaveBeta()
                if self.ConfigInfo['DeltaProfiles'] or self.ConfigInfo['DeltaPolar'] or self.ConfigInfo['DeltaData']:
                    ASM.DepolarizationCal()
                if self.ConfigInfo['DeltaProfiles']:
                    ASM.ShowDepolarizationProfiles()
                if self.ConfigInfo['DeltaPolar']:
                    ASM.ShowDepolarizationPolar()
                    ASM.ShowpolarizationPolarMap()
                if self.ConfigInfo['DeltaData']:
                    ASM.SaveDepolarization()
        if len(AzimuthDataPaths)>0:
            loginfo = self.loginfo+'\n'+str(len(AzimuthDataPaths))+' Groups Data was analysised'
            WriteLogFile(loginfo,self.Date,'AS_')
    def FixedPoint(self):
        print('\n-----FixedPoint starts-----\n')
        FixedPointDataPaths =[]
        for year in os.listdir(self.MainPath):
            # print(self.ConfigInfo['StartDate'].year)
            if year.startswith('20') and float(year) >= self.ConfigInfo['StartDate'].year and float(year) <= self.ConfigInfo['EndDate'].year:
                if os.path.exists((self.MainPath +'/' + year + '/Fixed_point')):
                    for datapath in os.listdir(self.MainPath +'/' + year + '/Fixed_point'):
                        if datapath.startswith(year) and float(datapath) >= float(self.ConfigInfo['StartDate'].strftime('%Y%m%d'))and float(datapath) <= float(self.ConfigInfo['EndDate'].strftime('%Y%m%d')):
                            FixedPointDataPaths.append(self.MainPath +'/' + year + '/Fixed_point/'+datapath)  
        for datepath in tqdm(FixedPointDataPaths):
            # print(datepath)
            FPM = FixedPointMeasurement(datepath,self.ConfigInfo)
            FPM.GetFileName()
            FPM.GetDataFileFromLogFile()
            FPM.FindGroupID()
            FPM.Read_Data()
            FPM.GroupData()
            FPM.DataPreProcess()
            if self.ConfigInfo['Overlap']:
                FPM.OverlapCorrection()
            if self.ConfigInfo['RCSProfiles']:
                FPM.ShowRCSProfiles()
            if self.ConfigInfo['BetaProfiles'] or self.ConfigInfo['BetaData'] or self.ConfigInfo['FixBetaContourf']:
                FPM.AeroFernald()
            if self.ConfigInfo['BetaProfiles']:
                FPM.ShowBetaProfiles()
            FPM.SecectAndClassDate()
            if self.ConfigInfo['FixBetaContourf']:
                FPM.ShowBetaContourf()
            if self.ConfigInfo['BetaData']:
                FPM.SaveBeta()
            if self.ConfigInfo['DeltaProfiles'] or self.ConfigInfo['DeltaData'] or self.ConfigInfo['FixDeltaContourf']:
                FPM.DepolarizationCal()
            if self.ConfigInfo['DeltaProfiles']:
                FPM.ShowDepolarizationProfiles()
            if self.ConfigInfo['FixDeltaContourf']:
                FPM.ShowDepolarizationContourf()
            if self.ConfigInfo['DeltaData']:
                FPM.SaveDepolarization()     
        if len(FixedPointDataPaths)>0:
            loginfo = self.loginfo+'\n'+str(len(FixedPointDataPaths))+' Days Data was analysised'
            WriteLogFile(loginfo,self.Date,'FP_')

# MainPath = 'D:/hengheng zhang/raymetrics/Lidar_Data'
# ConfigFilePath = 'Config.init'
# workflowI = WorkFlow(MainPath)
# workflowI.ReadConfigFile(ConfigFilePath)
# workflowI.AzimuthScanning()

# workflowI.ZenithScanning()
# BetaSets = workflowI.BetaSets
# DeltaSets = workflowI.DeltaSets
# ShowZenithContourf

# workflowI.AzimuthScanning()            

def auto_analysis():    
    MainPath = ''
    ConfigFilePath = 'Config.init'
    workflowI = WorkFlow(MainPath)
    workflowI.ReadConfigFile(ConfigFilePath)
    workflowI.ZenithScanning()
    workflowI.AzimuthScanning()
    workflowI.FixedPoint()
    
