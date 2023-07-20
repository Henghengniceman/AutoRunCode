# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 16:33:06 2021

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function： Fixed point data analysis

"""
# from ReadLicel import ReadLicel
import os 
from datetime import datetime, timedelta
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.dates as mdates
import sys
MODULE_DIR = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, MODULE_DIR)
from utils_gfat.lidar_processing.lidar_processing.data_glue import data_glue
from utils_gfat.lidar_processing.lidar_processing.window_fliter import window_fliter
from utils_gfat.backward_aero_fernald import backward_aero_fernald

from utils_gfat.lidar_processing.lidar_processing.merge_polarized_channels import merge_polarized_channels
from utils_gfat.lidar_processing.lidar_processing.read_licel import read_licel



# DayPath = 'D:/hengheng zhang/raymetrics/Lidar_Data/Fixed_Point/20210309'

class FixedPointMeasurement(object):
    def __init__(self,DayPath,ConfigInfo):
        self.DayPath = DayPath
        self.GlueRange = ConfigInfo['GlueRange']
        self.V_constant =ConfigInfo['V_constant']
        self.ReferenceHeight = ConfigInfo['FixPointReferenceHeight']
        self.Sa = ConfigInfo['Sa']
        self.R_zc = ConfigInfo['R_zc']
        self.DepolSNR = ConfigInfo['DepolSNR']
        self.DataFiles = []
        self.logFiles = []
        self.GlueP = []
        self.GlueS  = []
        self.DateTimes = []
        self.Zeniths = [] 
        self.Azimuths = [] 
        self.Shoots = []        
        #%% group file
        self.GroupStartFiles = []
        self.GroupEndFiles = []
        self.GroupIDs = []
        self.GroupGlueP = []
        self.GroupGlueS = []
        self.GroupDateTimes = []
        self.GroupZeniths = [] 
        self.GroupAzimuths = [] 
        self.GroupShoots = []
        self.UV7d5mDP = []
        self.GroupBetaAeros = []
        self.GroupReievalIndex = []
        self.GroupUV7d5mDP = []
        
    def GetFileName(self):
        for file in os.listdir(self.DayPath):
            if file.startswith('datalog'):
                self.logFiles.append(file)
            elif file.startswith('RM'):
                self.DataFiles.append(file)         
    def GetDataFileFromLogFile(self):
        with open(self.DayPath+'/'+self.logFiles[0]) as f:
            lines = f.readlines()
        Groups = lines[0].split('')
        Groups = Groups[1:]
        for group in Groups:
            Time = group.split('')[1].split(' ')[0].split(':')
            Date = group.split('')[1].split(' ')[1].split('/')
            self.GroupStartFiles.append('RM'+Date[2][2:4]+Date[1][1]+Date[0]+Time[0]+'.'+Time[1]+Time[2]+Time[3])
            Time = group.split('')[2].split(' ')[0].split(':')
            Date = group.split('')[2].split(' ')[1].split('/')
            self.GroupEndFiles.append('RM'+Date[2][2:4]+Date[1][1]+Date[0]+Time[0]+'.'+Time[1]+Time[2]+Time[3])
    def FindGroupID(self):
        StartFileNos = []
        EndFileNos = []
        DataFileNos = []
        for startfile,endfile in zip(self.GroupStartFiles,self.GroupEndFiles):
            StartFileNos.append(int(startfile.replace('RM','').replace('.','')))
            EndFileNos.append(int(endfile.replace('RM','').replace('.','')))
        for datafile in self.DataFiles:
            DataFileNos.append(int(datafile.replace('RM','').replace('.','')))
        
        for startno,endno in zip(StartFileNos,EndFileNos):
            # print(endnp)
            pos_min = np.array(DataFileNos)>=startno
            pos_max =  np.array(DataFileNos)<=endno
            pos_rst = pos_min & pos_max
            ID  = np.where(pos_rst == True)
            self.GroupIDs.append(ID)
    # Read All Data
    def Read_Data(self):
        for file in self.DataFiles:
            DataSet  = read_licel(self.DayPath+'/'+file)
            self.Range = DataSet['UV7d5mAP']['Data'][:,0]
            self.GlueRangeIndex = int(self.GlueRange/(self.Range[1]-self.Range[0]))
            self.DateTimes.append(DataSet['DateTime'])
            self.Zeniths.append(abs(DataSet['ScanningAngle'][0]))
            self.Azimuths.append(abs(DataSet['ScanningAngle'][1]))
            self.Shoots.append(DataSet['shoots'])
            self.GlueP.append(data_glue(DataSet['UV7d5mAP']['Data'][:,1],DataSet['UV7d5mDP']['Data'][:,1],self.GlueRangeIndex))
            self.GlueS.append(data_glue(DataSet['UV7d5mAS']['Data'][:,1],DataSet['UV7d5mDS']['Data'][:,1],self.GlueRangeIndex))
            self.UV7d5mDP.append(DataSet['UV7d5mDP']['Data'][:,1])
        self.StationGeoInfo = DataSet['StationGeoInfo']
        self.GlueP = np.array(self.GlueP).T
        self.GlueS = np.array(self.GlueS).T
    def GroupData(self):
        for groupid in self.GroupIDs:
            # Data Group 
            self.GroupGlueP.append(np.nansum(self.GlueP[:,groupid][:,0,:],axis=1))
            self.GroupGlueS.append(np.nansum(self.GlueS[:,groupid][:,0,:],axis=1))
            #%% time Group
            tt = []
            for date in self.DateTimes[np.nanmin(groupid):np.nanmax(groupid)+1]:
                tt.append(datetime.timestamp(date)) 
            self.GroupDateTimes.append(datetime.fromtimestamp(np.nanmean(tt)))
            self.GroupZeniths.append(self.Zeniths[groupid[0][0]])
            self.GroupAzimuths.append(self.Azimuths[groupid[0][0]])
            self.GroupShoots.append(np.nansum(np.array(self.Shoots)[groupid]))
            self.GroupUV7d5mDP.append(np.nansum(np.array(self.UV7d5mDP).T[:,groupid][:,0,:],axis=1))
            # self.GroupUV7d5mDP = np.array(self.UV7d5mDP)[:,groupid][:,0,:]

        self.GroupGlueP = np.array(self.GroupGlueP).T
        self.GroupGlueS = np.array(self.GroupGlueS).T
            
    def DataPreProcess(self):
        #%% correct for ND-block   
        NDTimePeriod  = [datetime.timestamp(datetime(2021,2,23,12)),datetime.timestamp(datetime(2021,2,26,17))]
        for colindex,date in enumerate(self.GroupDateTimes):
            tt = datetime.timestamp(date)
            if tt > NDTimePeriod[0] and tt < NDTimePeriod[1]:
                self.GroupGlueS[:,colindex] = self.GroupGlueS[:,colindex]/0.0439
        #%% combine Data
        self.GroupGlueRaw,self.DepolarizationRatio= merge_polarized_channels(self.GroupGlueP,self.GroupGlueS)

        # self.GroupGlueRaw=self.GroupGlueP+self.GroupGlueS*self.V_constant
        for i in range(0,np.size(self.GroupGlueRaw,axis=1)):
            self.GroupGlueRaw[:,i]=window_fliter(self.GroupGlueRaw[:,i],name='Hamming', N=11) # smooth signal using hamming window
     #%% OverlapCorrection 
    def OverlapCorrection(self):
        OverlapSet = pd.read_excel('./OverLap/OverLap.xlsx',index_col=0)
        Overlap = OverlapSet.values
        for i in range(0,np.size(self.GroupGlueRaw,1)):
                self.GroupGlueRaw[0:30,i] = self.GroupGlueRaw[0:30,i]/Overlap.T 
    #%% show RCS            
    def ShowRCSProfiles(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/RCS/')):
           os.makedirs(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/RCS/'))   
        RCS = []
        for i in range (0,np.size(self.GroupGlueRaw,axis=1)):
            RCS.append(self.GroupGlueRaw[:,i]*np.square(self.Range))
        #%% show RCS
        for i in range (0,np.size(self.GroupGlueRaw,axis=1)-1):
            if self.GroupZeniths[i] == 90:
                with plt.style.context(['science','no-latex']):
                  fig, ax = plt.subplots()
                  ax.semilogy(self.Range[0:2000]/1000,self.GroupGlueRaw[0:2000,i],label = 'vertical')
                  if self.GroupZeniths[i+1] == 30: 
                      ax.semilogy(self.Range[0:4000]/2000,self.GroupGlueRaw[0:4000,i+1],label = 'slant')
                  ax.legend()
                  ax.set_title(self.GroupDateTimes[i].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.GroupDateTimes[i+1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
                  ax.set(xlabel='Range [Km]')
                  ax.set(ylabel='Amplitude')  
                  ax.set_xlim(0,15)
                  fig.savefig(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/RCS/'+self.GroupDateTimes[i].strftime('%Y%m%d%H%M%S')+'.jpg'),dpi=300)
                  plt.close()
            # else:
            #     print(0)
        
    def AeroFernald(self):  
        self.RangeIndex = int(self.ReferenceHeight/(self.Range[1]-self.Range[0]))
        
        for i in range (0,np.size(self.GroupGlueRaw,axis=1)-1):
            if self.GroupZeniths[i] == 90:
                VerticalData = {'Range':self.Range,
                    'Attitude':self.Range,
                    'Data':self.GroupGlueRaw[:,i],
                    'Date':self.DateTimes[i],
                    'ReferenceHeight':self.ReferenceHeight,
                    'Sa': self.Sa,
                    'R_zc':self.R_zc} 
            
                VerticalAeroFernaldAngle  =  backward_aero_fernald(VerticalData,self.StationGeoInfo)
                # VerticalAeroFernaldAngle.setGeographicInformation('Karlsruhe')
                # VerticalAeroFernaldAngle.setDataInformation(VerticalData)
                VerticalAeroFernaldAngle()
                VerticalBetaAero = VerticalAeroFernaldAngle.getAeroBeta()
                self.GroupBetaAeros.append(VerticalBetaAero)
                self.GroupReievalIndex.append(i)
                if self.GroupZeniths[i+1] == 30:
                    VerticalBackscatterRatio = VerticalBetaAero/VerticalAeroFernaldAngle.BetaMol
                    
                    R_zc = np.nanmean(VerticalBackscatterRatio[int(self.RangeIndex/2)-10:int(self.RangeIndex/2)+10])
                    if R_zc <0 or np.isnan(R_zc):
                            R_zc = 0
                    SlantData = {'Range':self.Range,
                                  'Attitude':self.Range/2,
                                  'Data':self.GroupGlueRaw[:,i+1],
                                  'Date':self.DateTimes[i+1],
                                  'ReferenceHeight':self.ReferenceHeight,
                                  'Sa': self.Sa,
                                  'R_zc':self.R_zc} 
                    
                    SlantAeroFernaldAngle  =  backward_aero_fernald(SlantData,self.StationGeoInfo)
                    # SlantAeroFernaldAngle.setGeographicInformation('Karlsruhe')
                    # SlantAeroFernaldAngle.setDataInformation(SlantData)
                    SlantAeroFernaldAngle()
                    SlantBetaAero = SlantAeroFernaldAngle.getAeroBeta()
                    self.GroupBetaAeros.append(SlantBetaAero)
                    self.GroupReievalIndex.append(i+1)
        self.GroupBetaAeros = np.array(self.GroupBetaAeros).T
        
    def ShowBetaProfiles(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/BetaProfiles/')):
            os.makedirs(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/BetaProfiles/'))   
        for i in range (0,np.size(self.GroupBetaAeros,axis=1)-1):
            if self.GroupZeniths[i] == 90:
                with plt.style.context(['science','no-latex']):
                   fig, ax = plt.subplots(dpi=200)
                   ax.plot(self.GroupBetaAeros[0:self.RangeIndex,i]*1e6,self.Range[0:self.RangeIndex]/1000,label='vertical')
                   if self.GroupZeniths[i+1] == 30: 
                       ax.plot(self.GroupBetaAeros[0:self.RangeIndex,i+1]*1e6,self.Range[0:self.RangeIndex]/2000,label='slant')
                   ax.legend()
                   ax.set_ylabel('Height [km]',fontdict={'weight': 'normal', 'size': 15})
                   ax.set_xlabel('Backscatter Coefficient[M$\mathregular{m^-}$$\mathregular{^1}$$\mathregular{Sr^-}$$\mathregular{^1}$]',fontdict={'weight': 'normal', 'size': 15})
                   ax.set_title(self.DateTimes[i].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTimes[i+1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
                  
                   ax.set_xlim([0, 10])
                   ax.set_ylim([0, 10])
                   fig.savefig(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Figure/BetaProfiles/'+self.DateTimes[i].strftime('%Y%m%d%H%M%S')+'.jpg'),dpi=300)
                   plt.close()
                   
    def SecectAndClassDate(self): # selct data to save
        self.VerticalGroupDateTime = []
        self.SlantGroupDateTime = []
        self.VerticalGroupShoots  = []
        self.SlantGroupShoots = []
      
        for i in self.GroupReievalIndex:
            if self.GroupZeniths[i] == 90 :
                self.VerticalGroupDateTime.append(self.GroupDateTimes[i])
                self.VerticalGroupShoots.append(self.GroupShoots[i])
            else:
                self.SlantGroupDateTime.append(self.GroupDateTimes[i])
                self.SlantGroupShoots.append(self.GroupShoots[i])
        
        self.VerticalGroupShoots = np.array(self.VerticalGroupShoots)
        self.SlantGroupShoots = np.array(self.SlantGroupShoots)
        
    def ShowBetaContourf(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/BetaContourf/')):
            os.makedirs(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/BetaContourf/'))
        VerticalGroupBetas = []
        SlantGroupBetas = []
        for i in self.GroupReievalIndex:
            if self.GroupZeniths[i] == 90:
                VerticalGroupBetas.append(self.GroupBetaAeros[0:self.RangeIndex,i])
            else:
                SlantGroupBetas.append(self.GroupBetaAeros[0:self.RangeIndex,i])
        VerticalGroupBetas = np.array(VerticalGroupBetas).T
        SlantGroupBetas = np.array(SlantGroupBetas).T
        
        BetaDatas = xr.Dataset(
                     {
                       "VerticalBeta":(("verticalrange",'verticaltime'),VerticalGroupBetas*1e6),
                       "SlantBeta":(("slantrange",'slanttime'),SlantGroupBetas*1e6),

                     },
                       coords={"verticalrange": list(self.Range[0:self.RangeIndex]/1000),"verticaltime": self.VerticalGroupDateTime,
                               'slantrange':list(self.Range[0:self.RangeIndex]/2000),"slanttime": self.SlantGroupDateTime}, 
                    )        
        VerticalBetada = BetaDatas.VerticalBeta
        SlantBetada = BetaDatas.SlantBeta
        Date = self.VerticalGroupDateTime[0].strftime('%Y-%m-%d')
        #%% set figure font
        fontdicts={'weight': 'bold', 'size': 18}
        fig, axes = plt.subplots(2, 1,sharex = True,figsize=(16, 12))   
        cs = SlantBetada.plot.contourf(
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
        axes[1].set_xlim(datetime.strptime(Date,'%Y-%m-%d'),datetime.strptime(Date,'%Y-%m-%d')+timedelta(days=1))
        axes[1].set_ylim(0,6)
        axes[1].set_ylabel('Attitude [Km]',fontdict=fontdicts,labelpad = 25)
        for tick in axes[0].yaxis.get_major_ticks():
                tick.label.set_fontsize(12)   
        axes[1].set_yticks(np.arange(0,6))
        axes[1].set_xlabel(('Measurement Time ['+Date+'], UTC'),fontdict=fontdicts,labelpad = 12.5)
        # hoursLoc = mdates.HourLocator(byhour=[6,12,18])  # 为6小时为1副刻度
        # axes[1].xaxis.set_minor_locator(hoursLoc)
        # axes[1].xaxis.set_minor_formatter(mdates.DateFormatter('%H'))
        # axes[1].xaxis.set_major_locator(mdates.HourLocator(interval=6))          
        # axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
        axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))

        for tick in axes[1].xaxis.get_major_ticks():
            tick.label.set_fontsize(15) 
        for tick in axes[1].yaxis.get_major_ticks():
            tick.label.set_fontsize(15) 
        plt.setp(axes[1].get_xticklabels(), rotation=0)        
        
        cs = VerticalBetada.plot.contourf(
                ax=axes[0],
                vmin = 0,
                vmax = 15,
                # y="Range",
                levels=13,
                robust=True,
                cmap = 'jet',
                add_colorbar=False,
                      )
        #color bar
        #colorbar 左 下 宽 高 
        l = 0.92
        b = 0.5
        w = 0.015
        h = 0.38
        #对应 l,b,w,h；设置colorbar位置；
        rect = [l,b,w,h] 
        cbar_ax = fig.add_axes(rect) 
        cb = plt.colorbar(cs, cax=cbar_ax)
        cb.set_label('Back.coe. [$\mathregular{m^-}$$\mathregular{^1}$$\mathregular{Sr^-}$$\mathregular{^1}$]' ,fontdict=fontdicts,labelpad =25 ) #设置colorbar的标签字体及其大小
        # set parameter of axis 
        axes[0].set_xlim(datetime.strptime(Date,'%Y-%m-%d'),datetime.strptime(Date,'%Y-%m-%d')+timedelta(days=1))
        axes[0].set_ylim(0,6)
        
        # axes[0].set_title('February, 2021, KIT ',fontdict={'weight': 'bold', 'size': 20})
        axes[0].set_ylabel('Attitude [Km]',fontdict=fontdicts,labelpad = 25)
        axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))

        for tick in axes[0].yaxis.get_major_ticks():
                tick.label.set_fontsize(15) 
        axes[0].set_yticks(np.arange(0,6))
        plt.subplots_adjust(wspace=0, hspace=0,right=0.9)

        fig.savefig(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Figure/BetaContourf/BackscatterCoefficient.jpg'),dpi=300)
        plt.close()    
      
    def SaveBeta(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Data/BetaProfiles/')):
           os.makedirs(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Data/BetaProfiles/'))
        #%% select data    
        VerticalGroupBetas = []
        SlantGroupBetas = []
        for i in self.GroupReievalIndex:
            if self.GroupZeniths[i] == 90:
                VerticalGroupBetas.append(self.GroupBetaAeros[0:self.RangeIndex,i])
            else:
                SlantGroupBetas.append(self.GroupBetaAeros[0:self.RangeIndex,i])
        
        
        VerticalGroupBetas = np.array(VerticalGroupBetas).T
        SlantGroupBetas = np.array(SlantGroupBetas).T
        
            
        VerticalRangeWrite = list(self.Range[0:self.RangeIndex])
        VerticalData = np.vstack((self.VerticalGroupShoots,VerticalGroupBetas))
        VerticalRangeWrite.insert(0,'ShootsNumber')
        VerticalDatasetFrame=pd.DataFrame(data=VerticalData,index=VerticalRangeWrite,columns=self.VerticalGroupDateTime)  # 1st row as the column names
        VerticalDatasetFrame.index.name = 'Range'
        
        SlantRangeWrite = list(self.Range[0:self.RangeIndex])
        SlantData = np.vstack((self.SlantGroupShoots,SlantGroupBetas))
        SlantRangeWrite.insert(0,'ShootsNumber')
        SlantDatasetFrame=pd.DataFrame(data=SlantData,index=SlantRangeWrite,columns=self.SlantGroupDateTime)  # 1st row as the column names
        SlantDatasetFrame.index.name = 'Range'   
        
        writer = pd.ExcelWriter(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Data/BetaProfiles/Betas.xlsx'), engine='xlsxwriter')
        VerticalDatasetFrame.to_excel(writer, sheet_name='VerticalBeta')
        SlantDatasetFrame.to_excel(writer, sheet_name='SlantBeta')
        writer.save()
        
    def DepolarizationCal(self):
        GroupGlueP = np.ones_like(self.GroupGlueP)
        GroupGlueS = np.ones_like(self.GroupGlueS) 
        for i in range(0,np.size(self.GroupGlueP,axis=1)):
            GroupGlueP[:,i] = window_fliter(self.GroupGlueP[:,i],name='Hamming', N=11)
            GroupGlueS[:,i] = window_fliter(self.GroupGlueS[:,i],name='Hamming', N=11)
        Noiselevel = np.nanmean(np.array(self.GroupUV7d5mDP).T[-500:,:])
        if Noiselevel<0.1:
            Noiselevel =0.1  
        GroupDepolarizationRatio=self.DepolarizationRatio
        self.GroupDepolarizationRatio = np.ones_like(GroupDepolarizationRatio)*np.nan
        for j in range(0,np.size(GroupDepolarizationRatio,1)):
            for i in range(0,np.size(GroupDepolarizationRatio,0)):
                if self.GroupGlueRaw[i,j]>Noiselevel*self.DepolSNR:
                    self.GroupDepolarizationRatio[i,j] = GroupDepolarizationRatio[i,j]   
                    
    def ShowDepolarizationProfiles(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/DepolarizationProfiles/')):
            os.makedirs(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/DepolarizationProfiles/'))   
        
        for i in range (0,np.size(self.GroupDepolarizationRatio,axis=1)-1):
            if self.GroupZeniths[i] == 90:
                with plt.style.context(['science','no-latex']):
                   fig, ax = plt.subplots(dpi=200)
                   ax.plot(self.GroupDepolarizationRatio[0:self.RangeIndex,i]*1e2,self.Range[0:self.RangeIndex]/1000,label='vertical')
                   if self.GroupZeniths[i+1] == 30: 
                       ax.plot(self.GroupDepolarizationRatio[0:self.RangeIndex,i+1]*1e2,self.Range[0:self.RangeIndex]/2000,label='slant')
                   ax.legend()
                   ax.set_ylabel('Height [km]',fontdict={'weight': 'normal', 'size': 15})
                   ax.set_xlabel('Depolarization Ratio',fontdict={'weight': 'normal', 'size': 15})
                   ax.set_title(self.DateTimes[i].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTimes[i+1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
                  
                   ax.set_xlim([0, 10])
                   ax.set_ylim([0, 10])
                   fig.savefig(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Figure/DepolarizationProfiles/'+self.DateTimes[i].strftime('%Y%m%d%H%M%S')+'.jpg'),dpi=300)
                   plt.close()
    def ShowDepolarizationContourf(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/DepolarizationContourf/')):
            os.makedirs(('../'+self.GroupDateTimes[0].strftime('%Y%m%d')+'/Figure/DepolarizationContourf/'))
        #%% select data    
        VerticalGroupDepolarizationRatio = []
        SlantGroupDepolarizationRatio = []
        for i in self.GroupReievalIndex:
            if self.GroupZeniths[i] == 90:
                VerticalGroupDepolarizationRatio.append(self.GroupDepolarizationRatio[0:self.RangeIndex,i])
            else:
                SlantGroupDepolarizationRatio.append(self.GroupDepolarizationRatio[0:self.RangeIndex,i])
        
        
        VerticalGroupDepolarizationRatio = np.array(VerticalGroupDepolarizationRatio).T
        SlantGroupDepolarizationRatio = np.array(SlantGroupDepolarizationRatio).T
        
        
        DeltaDatas = xr.Dataset(
                     {
                       "VerticalBeta":(("verticalrange",'verticaltime'),VerticalGroupDepolarizationRatio*100),
                       "SlantBeta":(("slantrange",'slanttime'),SlantGroupDepolarizationRatio*100),

                     },
                       coords={"verticalrange": list(self.Range[0:self.RangeIndex]/1000),"verticaltime": self.VerticalGroupDateTime,
                               'slantrange':list(self.Range[0:self.RangeIndex]/2000),"slanttime": self.SlantGroupDateTime}, 
                    )        
        VerticalDeltada = DeltaDatas.VerticalBeta
        SlantDeltada = DeltaDatas.SlantBeta
        Date = self.VerticalGroupDateTime[0].strftime('%Y-%m-%d')
        #%% set figure font
        fontdicts={'weight': 'bold', 'size': 18}
        fig, axes = plt.subplots(2, 1,sharex = True,figsize=(16, 12))   
        cs = SlantDeltada.plot.contourf(
                ax=axes[1],
                vmin = 0,
                vmax = 20,
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
        cb.set_label('Depo.Rat. [%]' ,fontdict=fontdicts,labelpad =25 ) #设置colorbar的标签字体及其大小
        # set parameter of axis 
        axes[1].set_xlim(datetime.strptime(Date,'%Y-%m-%d'),datetime.strptime(Date,'%Y-%m-%d')+timedelta(days=1))
        axes[1].set_ylim(0,6)
        axes[1].set_ylabel('Attitude [Km]',fontdict=fontdicts,labelpad = 25)
        for tick in axes[0].yaxis.get_major_ticks():
                tick.label.set_fontsize(12)   
        axes[1].set_yticks(np.arange(0,6))
        axes[1].set_xlabel(('Measurement Time ['+Date+'], UTC'),fontdict=fontdicts,labelpad = 12.5)
        axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))

        for tick in axes[1].xaxis.get_major_ticks():
            tick.label.set_fontsize(15) 
        for tick in axes[1].yaxis.get_major_ticks():
            tick.label.set_fontsize(15) 
        plt.setp(axes[1].get_xticklabels(), rotation=0)        

        # plt.xticks(rotation=45)
        # fig.autofmt_xdate(rotation=90)
        # 
        cs = VerticalDeltada.plot.contourf(
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
        b = 0.5
        w = 0.015
        h = 0.38
        #对应 l,b,w,h；设置colorbar位置；
        rect = [l,b,w,h] 
        cbar_ax = fig.add_axes(rect) 
        cb = plt.colorbar(cs, cax=cbar_ax)
        cb.set_label('Depo.Rat. [%]' ,fontdict=fontdicts,labelpad =25 ) #设置colorbar的标签字体及其大小
        # set parameter of axis 
        axes[0].set_xlim(datetime.strptime(Date,'%Y-%m-%d'),datetime.strptime(Date,'%Y-%m-%d')+timedelta(days=1))
        axes[0].set_ylim(0,6)
        
        # axes[0].set_title('February, 2021, KIT ',fontdict={'weight': 'bold', 'size': 20})
        axes[0].set_ylabel('Attitude [Km]',fontdict=fontdicts,labelpad = 25)
        for tick in axes[0].yaxis.get_major_ticks():
                tick.label.set_fontsize(15) 
        axes[0].set_yticks(np.arange(0,6))
        axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))

        plt.subplots_adjust(wspace=0, hspace=0,right=0.9)

        fig.savefig(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Figure/DepolarizationContourf/Depolarization.jpg'),dpi=300)
        plt.close()   
    
    def SaveDepolarization(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Data/DepolarizationProfiles/')):
           os.makedirs(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Data/DepolarizationProfiles/'))
        #%% select data    
        VerticalGroupDepolarizationRatio = []
        SlantGroupDepolarizationRatio = []
        for i in self.GroupReievalIndex:
            if self.GroupZeniths[i] == 90:
                VerticalGroupDepolarizationRatio.append(self.GroupDepolarizationRatio[0:self.RangeIndex,i])
            else:
                SlantGroupDepolarizationRatio.append(self.GroupDepolarizationRatio[0:self.RangeIndex,i])
        
        
        VerticalGroupDepolarizationRatio = np.array(VerticalGroupDepolarizationRatio).T
        SlantGroupDepolarizationRatio = np.array(SlantGroupDepolarizationRatio).T
        
            
        VerticalRangeWrite = list(self.Range[0:self.RangeIndex])
        VerticalData = np.vstack((self.VerticalGroupShoots,VerticalGroupDepolarizationRatio))
        VerticalRangeWrite.insert(0,'ShootsNumber')
        VerticalDatasetFrame=pd.DataFrame(data=VerticalData,index=VerticalRangeWrite,columns=self.VerticalGroupDateTime)  # 1st row as the column names
        VerticalDatasetFrame.index.name = 'Range'
        
        SlantRangeWrite = list(self.Range[0:self.RangeIndex])
        SlantData = np.vstack((self.SlantGroupShoots,SlantGroupDepolarizationRatio))
        SlantRangeWrite.insert(0,'ShootsNumber')
        SlantDatasetFrame=pd.DataFrame(data=SlantData,index=SlantRangeWrite,columns=self.SlantGroupDateTime)  # 1st row as the column names
        SlantDatasetFrame.index.name = 'Range'

        writer = pd.ExcelWriter(('../'+self.DateTimes[0].strftime('%Y%m%d')+'/Data/DepolarizationProfiles/Delats.xlsx'), engine='xlsxwriter')
        VerticalDatasetFrame.to_excel(writer, sheet_name='Verticaldelta')
        SlantDatasetFrame.to_excel(writer, sheet_name='Slantdelta')
        writer.save()
      
       
# FixPointMeasurementI = FixPointMeasurement(DayPath)
# FixPointMeasurementI.GetFileName()
# FixPointMeasurementI.GetDataFileFromLogFile()
# FixPointMeasurementI.FindGroupID()
# FixPointMeasurementI.Read_Data()
# FixPointMeasurementI.GroupData()
# FixPointMeasurementI.DataPreProcess()
# FixPointMeasurementI.OverlapCorrection()
# FixPointMeasurementI.ShowRCSProfiles()
# FixPointMeasurementI.AeroFernald()
# FixPointMeasurementI.ShowBetaProfiles()
# FixPointMeasurementI.SecectAndClassDate()
# FixPointMeasurementI.ShowBetaContourf()
# FixPointMeasurementI.SaveBeta()
# FixPointMeasurementI.DepolarizationCal()
# FixPointMeasurementI.ShowDepolarizationContourf()
# FixPointMeasurementI.ShowDepolarizationProfiles()
# FixPointMeasurementI.SaveDepolarization()
# aa = FixPointMeasurementI.DepolarizationRatio
# aa = FixPointMeasurementI.DepolarizationRatio
# aa1 =FixPointMeasurementI.UV7d5mDP



    

# DateTimes = []
# Zeniths  = []
# Shoots = []
# Datas = [] 
# GlueP = []
# GlueS = []
# GlueRangeIndex = 300
# for file in DataFiles[0:10]:
#     DataSet  = ReadLicel(DayPath+'/'+file)
#     DateTimes.append(DataSet['UV7d5mAP']['DateTime'])
#     Zeniths.append(abs(DataSet['UV7d5mAP']['ScanningAngle'][0]))
#     Shoots.append(DataSet['UV7d5mAP']['shoots'])
#     GlueP.append(DataGlue(DataSet['UV7d5mAP']['Data'][:,1],DataSet['UV7d5mDP']['Data'][:,1],GlueRangeIndex))
#     GlueS.append(DataGlue(DataSet['UV7d5mAS']['Data'][:,1],DataSet['UV7d5mDS']['Data'][:,1],GlueRangeIndex))
# for 

    
    
    

    