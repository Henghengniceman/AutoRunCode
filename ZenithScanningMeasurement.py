# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 15:39:02 2021

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function：

"""
import os 
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import math 
import pdb
import sys
MODULE_DIR = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, MODULE_DIR)
from utils_gfat.lidar_processing.lidar_processing.read_licel import read_licel
from utils_gfat.lidar_processing.lidar_processing.data_glue import data_glue
from utils_gfat.lidar_processing.lidar_processing.window_fliter import window_fliter
from utils_gfat.lidar_processing.lidar_processing.merge_polarized_channels import merge_polarized_channels
from utils_gfat.backward_aero_fernald import backward_aero_fernald

# from ReadLicel import ReadLicel
# from Src.DataGlue import DataGlue
# from Src.window_fliter import window_fliter
# from Src.BackwardAeroFernald import BackwardAeroFernald
# from Src.merge_polarized_channels import merge_polarized_channels
# import pandas as pd





class ZenithScanningMeasurement(object):
    def __init__(self,TimeFolderDir,ConfigInfo):
        self.TimeFolderDir = TimeFolderDir
        self.GlueRange = ConfigInfo['GlueRange']
        self.V_constant =ConfigInfo['V_constant']
        self.ReferenceHeight = ConfigInfo['ZenithReferenceHeight']
        self.Sa = ConfigInfo['Sa']
        self.R_zc = ConfigInfo['R_zc']
        self.ShowDepolHeight = ConfigInfo['ShowDepolHeight']
        self.DepolSNR = ConfigInfo['DepolSNR']
        # self.V_constant = 0.0335
        self.Zenith = []
        self.Azimuth = [] 
        self.DateTime = []
        self.GlueP = []
        self.GlueS  = []
        self.UV7d5mDP = []
        self.DataSets =[]
        self.FileNames = []
        self.BetaAeros  = []
        self.BinWidthCheck = True
        # self.StationGeoInfo = None
    #%% read data
    def ReadData(self):
        # print(BinWidthCheck)
        DataFolderNames = os.listdir(self.TimeFolderDir)
        # import pdb
        # pdb.set_trace()
        # print(DataFolderNames)
        for filename in DataFolderNames:
            # print(filename)
            self.FileNames.append(filename)
            DataPath = (self.TimeFolderDir+'/'+filename)
            if filename.split('/')[-1].startswith('RM'):
                # print(DataPath)
                DataSet  = read_licel(DataPath)
                self.BinWidthCheck = self.BinWidthCheck and DataSet['BinWithCheck'] 
                self.DataSets.append(DataSet)
        self.BinWidthCheck = self.BinWidthCheck and len(DataFolderNames)>1   
        # pdb.set_trace()
        # print(self.FileNames)
        # print(self.BinWidthCheck)


    #%% Data Preprocess        
    def DataPreProcess(self):
        self.Range = self.DataSets[0]['UV7d5mAP']['Data'][:,0]
        self.StationGeoInfo = self.DataSets[0]['StationGeoInfo']
        self.GlueRangeIndex = int(self.GlueRange/(self.Range[1]-self.Range[0]))
        # print(self.GlueRangeIndex)
        for DataSet_no, current_DataSet in enumerate(self.DataSets):
            self.Zenith.append(abs(current_DataSet['ScanningAngle'][0]))
            self.Azimuth.append(abs(current_DataSet['ScanningAngle'][1]))
            self.DateTime.append(current_DataSet['DateTime'])
            self.GlueP.append(data_glue(current_DataSet['UV7d5mAP']['Data'][:,1],current_DataSet['UV7d5mDP']['Data'][:,1],self.GlueRangeIndex))
            self.GlueS.append(data_glue(current_DataSet['UV7d5mAS']['Data'][:,1],current_DataSet['UV7d5mDS']['Data'][:,1],self.GlueRangeIndex))
            # self.GlueP.append(current_DataSet['UV7d5mDP']['Data'][:,1]-np.nanmean(current_DataSet['UV7d5mDP']['Data'][-500:,1]))
            # self.GlueS.append(current_DataSet['UV7d5mDS']['Data'][:,1]-np.nanmean(current_DataSet['UV7d5mDS']['Data'][-500:,1]))

            self.UV7d5mDP.append(current_DataSet['UV7d5mDP']['Data'][:,1])
        # print(self.StationGeoInfo)
        self.GlueP = np.array(self.GlueP).T
        self.GlueS = np.array(self.GlueS).T
        # self.GlueRaw=self.GlueP+self.GlueS*self.V_constant
        self.GlueRaw,self.DepolarizationRatio= merge_polarized_channels(self.GlueP,self.GlueS)

        
        for i in range(0,np.size(self.GlueRaw,axis=1)):
            self.GlueRaw[:,i]=window_fliter(self.GlueRaw[:,i],name='Hamming', N=11) # smooth signal using hamming window
        self.GlueRawAll = self.GlueRaw
    #%% OverlapCorrection 
    def OverlapCorrection(self):
        OverlapSet = pd.read_excel('./OverLap/OverLap.xlsx',index_col=0)
        Overlap = OverlapSet.values
        for i in range(0,np.size(self.GlueRaw,1)):
                self.GlueRaw[0:30,i] = self.GlueRaw[0:30,i]/Overlap.T 
    #%% show RCS plot
    def ShowRCSProfiles(self):
        GlueRCS =[]
        for i in range (0,np.size(self.GlueRaw,axis=1)):
            GlueRCS.append(self.GlueRaw[:,i]*np.square(self.Range))
        GlueRCS = np.array(GlueRCS).T
        # import pdb
        # pdb.set_trace()
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/RCS/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/RCS/'),mode=0o777)    
        with plt.style.context(['science','no-latex']):
            fig, ax = plt.subplots()
            for i in range(len(self.Zenith)):
                ax.semilogy(self.Range[0:1500]/1000*np.sin(math.radians(abs(self.Zenith[i]))),GlueRCS[0:1500,i])
            ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
            ax.set(xlabel='Range [Km]')
            ax.set(ylabel='Amplitude')  
            ax.set_xlim(0,10)
            # print('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/RCS/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
            fig.savefig(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/RCS/'+self.TimeFolderDir.split('/')[-1]+'.jpg'),dpi=300)
            plt.close()
        #%% show plot
    def ShowRCSPolar(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarRCS/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarRCS/'))
                
        GlueRCS =[]
        for i in range (0,np.size(self.GlueRaw,axis=1)):
            GlueRCS.append(self.GlueRaw[:,i]*np.square(self.Range))
        GlueRCS = np.array(GlueRCS).T
        
        # if self.Azimuth[0] == 180:
        #     Zenith = 180-np.array(self.Zenith)
        # else:
        #     Zenith = np.array(self.Zenith)
        Zenith = np.abs(self.Zenith)
        r, theta = np.meshgrid(self.Range[1:1500]/1000,np.radians(np.abs(Zenith)))
        GlueRCS = np.where(GlueRCS>8e7,8e7,GlueRCS)
        GlueRCS = np.where(GlueRCS<0,0,GlueRCS)
        GlueRCS[-1,-1] = 8e7
        GlueRCS[-1,-2] = 0
        with plt.style.context(['science','no-latex']):
               fig = plt.figure(figsize=(5,5),dpi=120)
               # position=fig.add_axes([0.12, 0.08, 0.78, 0.03]) #位置[左,下,右,上]
               ax = fig.subplots(subplot_kw=dict(projection='polar'))
               cs=ax.contourf(theta, r, GlueRCS[1:1500,:].T,cmap = 'jet')
               cbar=fig.colorbar(cs, ax=ax,orientation='horizontal',fraction=0.04,pad=0.15)
               cbar.set_label('Range Corrected LiDAR Signal')
               ax.set_xlim(np.radians(np.min(Zenith)),np.radians(np.max(Zenith)))
               ax.set(xlabel='Range [km]')
               # ax.set(ylabel='Range [km]')
               # ax.tick_params(axis='x', labelrotation=45)
               ax.xaxis.set_label_coords(0.5, -0.1) 
               ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
               plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarRCS/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
               plt.close()
                
    #%% Fernald 
    def AeroFernald(self):
        Data = {'Range':self.Range,
                'Attitude':self.Range*np.sin(math.radians(abs(self.Zenith[0]))),
                'Data':self.GlueRaw[:,0],
                'Date':self.DateTime[0],
                'ReferenceHeight':self.ReferenceHeight,
                'Sa': self.Sa,
                'R_zc':self.R_zc
                } 
        # pdb.set_trace()
        VerticalAeroFernal  =  backward_aero_fernald(Data,self.StationGeoInfo)
        # VerticalAeroFernal.setGeographicInformation('Karlsruhe')
        # VerticalAeroFernal.setDataInformation(Data)
        VerticalAeroFernal()
        VerticalBetaAero = VerticalAeroFernal.getAeroBeta()
        VerticalBackscatterRatio = VerticalBetaAero/VerticalAeroFernal.BetaMol
        self.ReferenceIndex  = int(self.ReferenceHeight/(self.Range[1]-self.Range[0]))

        for i in range(np.size(self.GlueRaw,1)): 
                VerticalReferenceIndex  = int(self.ReferenceIndex*np.sin(math.radians(abs(self.Zenith[i]))))
                R_zc = np.nanmean(VerticalBackscatterRatio[VerticalReferenceIndex-10:VerticalReferenceIndex+10])
                Data = {'Range':self.Range,
                        'Attitude':self.Range*np.sin(math.radians(abs(self.Zenith[i]))),
                        'Data':self.GlueRaw[:,i],
                        'Date':self.DateTime[i],
                        'ReferenceHeight':self.ReferenceHeight,
                        'Sa': self.Sa,
                        'R_zc':R_zc
                        } 
                
                AeroFernaldAngle  =  backward_aero_fernald(Data,self.StationGeoInfo)
                # AeroFernaldAngle.setGeographicInformation('Julich')
                # AeroFernaldAngle.setDataInformation(Data)
                AeroFernaldAngle()
                BetaAero = AeroFernaldAngle.getAeroBeta()
                # pdb.set_trace()
                self.BetaAeros.append(BetaAero)
        self.BetaAeros = np.array(self.BetaAeros).T
    #%% show and save Beta
    def ShowBetaProfiles(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/BetaProfiles/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/BetaProfiles/'))
        with plt.style.context(['science','no-latex']):
              fig, ax = plt.subplots(dpi=200)
              for i in range(0,np.size(self.GlueRaw,1)):
                  ax.plot(self.BetaAeros[50:self.ReferenceIndex,i]*1e6,self.Range[50:self.ReferenceIndex]*np.sin(math.radians(abs(self.Zenith[i])))/1000,label=str(abs(self.Zenith[i])) )
              ax.set_ylabel('Height [km]',fontdict={'weight': 'normal', 'size': 15})
              ax.set_xlabel('Backscattering coefficient [M$\mathregular{m^-}$$\mathregular{^1}$$\mathregular{Sr^-}$$\mathregular{^1}$]',fontdict={'weight': 'normal', 'size': 15})
              ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
              # ax.legend()
              ax.set_xlim([-5, 7.5])
              ax.set_ylim([0, self.ReferenceHeight/1000])
              # ax.set_xlim([-1,4])
              plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/BetaProfiles/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
              plt.close()
        #%% ploar plot   
    def ShowBetaPolar(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarBeta/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarBeta/'))
        BetaAeros = np.where(self.BetaAeros<0,np.nan,self.BetaAeros)
        BetaAeros = np.where(self.BetaAeros>2e-5,2e-5,self.BetaAeros)

        # BetaAeros = BetaAeros*1e6
        # if self.Azimuth[0] == 180:
        #     Zenith = 180-np.array(self.Zenith)
        # else:
        #     Zenith = np.array(self.Zenith)
        Zenith = np.abs(self.Zenith)
        r, theta = np.meshgrid(self.Range[1:400]/1000,np.radians(np.abs(Zenith)))
        
        with plt.style.context(['science','no-latex']):
                fig = plt.figure(figsize=(5,5),dpi=120)
                # position=fig.add_axes([0.12, 0.08, 0.78, 0.03]) #位置[左,下,右,上]
                ax = fig.subplots(subplot_kw=dict(projection='polar'))
                cs=ax.contourf(theta, r, BetaAeros[1:400,:].T*1e6,cmap = 'jet')
                cbar=fig.colorbar(cs, ax=ax,orientation='horizontal',fraction=0.04,pad=0.15)
                cbar.set_label('Backscattering coefficient [M$\mathregular{m^-}$$\mathregular{^1}$$\mathregular{Sr^-}$$\mathregular{^1}$]')
                ax.set_xlim(np.radians(np.min(Zenith)),np.radians(np.max(Zenith)))
                ax.set(xlabel='Range [km]')
                # ax.set(ylabel='Range [km]')
                # ax.tick_params(axis='x', labelrotation=45)
                ax.xaxis.set_label_coords(0.5, -0.1) 
                ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
                plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarBeta/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
                plt.close()
    def SaveBeta(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Data/BetaProfiles/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Data/BetaProfiles/'))
        Range = list(self.Range)
        Data = np.vstack((self.Azimuth,self.Zenith,self.BetaAeros))
        Range.insert(0,'StationAzimuth')
        Range.insert(1,'StationZenith')
        DatasetFrame=pd.DataFrame(data=Data,index=Range,columns=self.DateTime)  # 1st row as the column names
        DatasetFrame.index.name = 'Range'      
        DatasetFrame.to_excel('../'+self.DateTime[0].strftime('%Y%m%d')+'/Data/BetaProfiles/'+self.TimeFolderDir.split('/')[-1]+'.xlsx')
    def DepolarizationCal(self):
        GlueP = np.ones_like(self.GlueP)
        GlueS = np.ones_like(self.GlueS) 
        for i in range(0,np.size(self.GlueP,axis=1)):
            GlueP[:,i] = window_fliter(self.GlueP[:,i],name='Hamming', N=11)
            GlueS[:,i] = window_fliter(self.GlueS[:,i],name='Hamming', N=11)
        Noiselevel = np.nanmean(np.array(self.UV7d5mDP).T[-500:,:])
        # self.Noiselevel = np.array(self.UV7d5mDP).T[-500:,:]
        if Noiselevel<0.1:
            Noiselevel =0.1      
            
        DepolarizationRatio=self.DepolarizationRatio
        # self.DepolarizationRatio = DepolarizationRatio

        self.DepolarizationRatio = np.ones_like(DepolarizationRatio)*np.nan

        for j in range(0,np.size(DepolarizationRatio,1)):
            for i in range(0,np.size(DepolarizationRatio,0)):
                if self.GlueRawAll[i,j]>Noiselevel*self.DepolSNR:
                    self.DepolarizationRatio[i,j] = DepolarizationRatio[i,j]
                               
    def ShowDepolarizationProfiles(self):
        self.DepoIndex = int(self.ShowDepolHeight/(self.Range[1]-self.Range[0]))
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/DepolarizationProfiles/')):
               os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/DepolarizationProfiles/'))
        with plt.style.context(['science','no-latex']):
                fig, ax = plt.subplots(dpi=200)
                for i in range(0,np.size(self.DepolarizationRatio,1)):
                    ax.plot(self.DepolarizationRatio[0:self.DepoIndex]*1e2,self.Range[0:self.DepoIndex]*np.sin(math.radians(abs(self.Zenith[i])))/1000)
                ax.set_ylabel('Height [km]',fontdict={'weight': 'normal', 'size': 15})
                ax.set_xlabel('Depolarization Ratio [%]',fontdict={'weight': 'normal', 'size': 15})
                ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
                self.DepolarizationRatio[np.isinf(self.DepolarizationRatio)]=np.nan
                ax.set_xlim([0, np.nanmax(self.DepolarizationRatio[0:self.DepoIndex])*1e2])
                ax.set_ylim([0, self.ShowDepolHeight/1000])
                plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/DepolarizationProfiles/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
                plt.close()
    def  ShowDepolarizationPolar(self):    
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarDepolarization/')):
            os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarDepolarization/'))
        DepolarizationRatio = np.where(np.isnan(self.DepolarizationRatio),0,self.DepolarizationRatio)
        DepolarizationRatio = DepolarizationRatio*100
        # DepolarizationRatio = np.where(DepolarizationRatio>20,0,DepolarizationRatio)
        DepolarizationRatio = np.where(DepolarizationRatio<0,np.nan,DepolarizationRatio)
        # if self.Azimuth[0] == 180:
        #     Zenith = 180-np.array(self.Zenith)
        # else:
        #     Zenith = np.array(self.Zenith)
        Zenith = np.abs(self.Zenith)
        r, theta = np.meshgrid(self.Range/1000,np.radians(np.abs(self.Zenith)))
        DepolarizationRatio[-1,-1] = 20
        DepolarizationRatio[-1,-2] = 0
        # print(np.nanmax(DepolarizationRatio))
        # print(np.nanmin(DepolarizationRatio))
            # DepolarizationRatio = np.where(DepolarizationRatio<0,np.nan,DepolarizationRatio)

            
        with plt.style.context(['science','no-latex']):
           fig = plt.figure(figsize=(5,5),dpi=120)
           # position=fig.add_axes([0.12, 0.15, 0.78, 0.03]) #位置[左,下,右,上]
           ax = fig.subplots(subplot_kw=dict(projection='polar'))
           cs=ax.contourf(theta, r, DepolarizationRatio.T,vmin=0,vmax=20,cmap = 'jet')
           cbar=fig.colorbar(cs, ax=ax,orientation='vertical',fraction=0.04,pad=0.1)
           cbar.set_label('Volume Depolarization Ratio [%]')
           ax.set_xlim(np.radians(0),np.radians(90))
           ax.set_ylim(0,6)
           # ax.set(xlabel='Range [km]')
           ax.set_xticks([np.radians(15),np.radians(30),np.radians(45),np.radians(60),np.radians(75),np.radians(90)])
           ax.set(ylabel='Altitude [km]')
           # ax.text(np.radians(10),2.5,'Range [km]',rotation=0)
           # ax.xaxis.set_label_coords(0.9, 0.17)
           ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
           plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarDepolarization/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
           plt.close()
    def SaveDepolarization(self):   
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Data/DepolarizationProfiles/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Data/DepolarizationProfiles/'))             
        RangeWrite = list(self.Range[0:self.DepoIndex])
        Data = np.vstack((self.Azimuth,self.Zenith,self.DepolarizationRatio[0:self.DepoIndex]))
        RangeWrite.insert(0,'StationAzimuth')
        RangeWrite.insert(1,'StationZenith')
        DatasetFrame=pd.DataFrame(data=Data,index=RangeWrite,columns=self.DateTime)  # 1st row as the column names
        DatasetFrame.index.name = 'Range'      
        DatasetFrame.to_excel('../'+self.DateTime[0].strftime('%Y%m%d')+'/Data/DepolarizationProfiles/'+self.TimeFolderDir.split('/')[-1]+'.xlsx')   
    def GetContourfData(self):
        if self.Zenith[0] == 90:
            BetaSet = pd.DataFrame(data = self.BetaAeros[0:self.ReferenceIndex,0],index = self.Range[0:self.ReferenceIndex],columns = self.DateTime[0:1])
            DeltaSet = pd.DataFrame(data = self.DepolarizationRatio[0:self.ReferenceIndex,0],index = self.Range[0:self.ReferenceIndex],columns = self.DateTime[0:1])
        return BetaSet,DeltaSet
#%% main function    
# DayPath = 'D:/hengheng zhang/raymetrics/Lidar_Data/2021/Scanning_Measurements/02/13'
# ConfigInfo ={'GlueRange':2250,'V_constant':0.0335,'ZenithReferenceHeight':4000,
#               'Sa':40,'R_zc':1.0,'ShowDepolHeight':10000,'DepolSNR':3}              
# TimeFolderNames=[]
# for file in os.listdir(DayPath):
#     if file.startswith('ZS'):
#         TimeFolderNames.append(file)
# for TimeFoldername in tqdm(TimeFolderNames[10:11]):
#     TimeFolderDir = (DayPath + '/'+TimeFoldername)
#     ScanningMeasurementI  = ZenithScanningMeasurement(TimeFolderDir,ConfigInfo)
#     ScanningMeasurementI.ReadData()
#     ScanningMeasurementI.DataPreProcess()
#     aa= ScanningMeasurementI.DataSets
#     ScanningMeasurementI.OverlapCorrection()
#     ScanningMeasurementI.ShowRCSProfiles()
#     ScanningMeasurementI.ShowRCSPolar()
#     ScanningMeasurementI.AeroFernald()
#     ScanningMeasurementI.ShowBetaProfiles()
#     ScanningMeasurementI.ShowBetaPolar()
#     ScanningMeasurementI.SaveBeta()
#     ScanningMeasurementI.DepolarizationCal()
#     ScanningMeasurementI.ShowDepolarizationProfiles()
#     ScanningMeasurementI.ShowDepolarizationPolar()
#     ScanningMeasurementI.SaveDepolarization()
#     # aa = ScanningMeasurementI.Noiselevel
   
  
  
       
       
      