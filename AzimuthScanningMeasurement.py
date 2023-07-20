# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 14:46:34 2021

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function：AzimuthScanningMeasurement

"""
import os 
import numpy as np 
import matplotlib.pyplot as plt
import math 
from shapely.geometry import LineString
import branca
import geojsoncontour
import folium
from folium import plugins
from ZenithScanningMeasurement import ZenithScanningMeasurement
import sys
MODULE_DIR = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, MODULE_DIR)
from utils_gfat.lidar_processing.lidar_processing.molecule_scatter import molecule_scatter
import utils_gfat.lidar_processing.lidar_processing.helper_functions as helper_functions
from utils_gfat.backward_aero_fernald import backward_aero_fernald
from utils_gfat.forward_aero_fernald import forward_aero_fernald

# from Src.MoleculeScatter import MoleculeScatter
# from Src.linefit import linefit
# from Src.BackwardAeroFernald import BackwardAeroFernald
# from Src.forward_aero_fernald import forward_aero_fernald




class AzimuthScanningMeasurement(ZenithScanningMeasurement):
    def __init__(self,TimeFolderDir,ConfigInfo):
        super(AzimuthScanningMeasurement,self).__init__(TimeFolderDir,ConfigInfo)
        self.ReferenceHeight = ConfigInfo['AzimuthReferenceHeight']
        self.Sm =8*math.pi/3
    def ShowRCSProfiles(self):
        GlueRCS =[]
        for i in range (0,np.size(self.GlueRaw,axis=1)):
            GlueRCS.append(self.GlueRaw[:,i]*np.square(self.Range))
        GlueRCS = np.array(GlueRCS).T
        os.chdir(os.path.dirname(__file__))

        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/RCS/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/RCS/'))
        
        
                
        with plt.style.context(['science','no-latex']):
            fig, ax = plt.subplots()
            for i in range(len(self.Zenith)):
                ax.semilogy(self.Range[0:1500]/1000,GlueRCS[0:1500,i])
                ax.semilogy(self.Range[self.ReferenceIndexFitiing-50:self.ReferenceIndexFitiing]/1000,
                            GlueRCS[self.ReferenceIndexFitiing-50:self.ReferenceIndexFitiing,i],color='k')

            ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
            ax.set(xlabel='Range [Km]')
            ax.set(ylabel='Amplitude')  
            ax.set_xlim(0,10)
            fig.savefig(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/RCS/'+self.TimeFolderDir.split('/')[-1]+'.jpg'),dpi=300)
            plt.close()
            # polar plot
    def ShowRCSPolar(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarRCS/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarRCS/'))
            
        GlueRCS =[]
        for i in range (0,np.size(self.GlueRaw,axis=1)):
            GlueRCS.append(self.GlueRaw[:,i]*np.square(self.Range))
        GlueRCS = np.array(GlueRCS).T
        Zenith = np.radians(np.abs(self.Zenith))   
        r, theta = np.meshgrid(self.Range[0:1333]/1000,np.radians(np.abs(self.Azimuth)))
        x,y,z = r*np.sin(theta)*np.cos(Zenith[0]),r*np.cos(theta)*np.cos(Zenith[0]),r*np.sin(Zenith[0])
        
        GlueRCS = np.where(GlueRCS<0,0,GlueRCS)
        GlueRCS = np.where(np.isnan(GlueRCS),0,GlueRCS)
        scamap = plt.cm.ScalarMappable(cmap='jet')
        fcolors = scamap.to_rgba(GlueRCS[0:1333,:].T)
        # print(np.size(fcolors.T,0))
        # print(np.size(x,0))
        with plt.style.context(['science','no-latex']):
              fig = plt.figure(figsize=(9,9),dpi=120)
              ax = fig.add_subplot(projection='3d')
              # ax = fig.gca(projection='3d')
              ax.plot_surface(x,y,z,facecolors=fcolors,rstride=1,cstride=1,cmap = 'jet')
              cbar=fig.colorbar(scamap,orientation='vertical',fraction=0.03,pad=0.1)
              cbar.set_label('Range Corrected LiDAR Signal')
              ax.set_xlim(0,10)
              ax.set_ylim(-10,10)
              ax.set_zlim(0,10)
              ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
              ax.set(xlabel='Range [km]')
              ax.set(ylabel='Range [km]')
              ax.set(zlabel='Range [km]')
              ax.set_box_aspect([1,2,1])
              plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarRCS/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
              plt.close()
    def convertRangeToLatLon(self, lat0,lon0,Distance,Angle):
        R = 6378.1 #Radius of the Earth
        # lat0, latitude of lidar station 
        # lon0, longitude of lidar station 
        # Distance, units m
        # angle, angle with of North in degree
        
        brng = math.radians(Angle) #Bearing is 90 degrees converted to radians.
        d = Distance #Distance in km
        
        #lat2  52.20444 - the lat result I'm hoping for
        #lon2  0.36056 - the long result I'm hoping for.
        
        lat1 = math.radians(lat0) #Current lat point converted to radians
        lon1 = math.radians(lon0) #Current long point converted to radians
        
        lat2 = math.asin( math.sin(lat1)*math.cos(d/R) +
             math.cos(lat1)*math.sin(d/R)*math.cos(brng))
        
        lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),
                     math.cos(d/R)-math.sin(lat1)*math.sin(lat2))
        
        lat2 = math.degrees(lat2)
        lon2 = math.degrees(lon2)
        return lat2, lon2
    
    def ShowRCSPolarMap(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarRCSMap/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarRCSMap/'))
        GlueRCS =[]
        for i in range (0,np.size(self.GlueRaw,axis=1)):
            GlueRCS.append(self.GlueRaw[:,i]*np.square(self.Range))
        GlueRCS = np.array(GlueRCS).T
        Bin_size = 800
        AzimuthHorizon =  np.array(self.Azimuth) - 10
        RangeHorizon = self.Range[0:Bin_size]/1000
        RCS = GlueRCS[0:Bin_size,:]
        RangeHorizon,AzimuthHorizon = np.meshgrid(RangeHorizon,AzimuthHorizon)
        lons = np.ones_like(AzimuthHorizon)
        lats = np.ones_like(AzimuthHorizon)
        for i in range(0,np.size(AzimuthHorizon,0)):
            for j in range(0,np.size(AzimuthHorizon,1)):
                lats[i,j],lons[i,j] = self.convertRangeToLatLon(49.02028888888889,8.336347222222223,RangeHorizon[i,j],AzimuthHorizon[i,j])
        colors = ['#0000ff','#0015ff','#002aff','#0040ff','#0055ff','#006aff','#0080ff','#0095ff',
          '#00aaff','#00bfff','#00d5ff','#00eaff','#00ffff','#00ffea','#00ffd5','#00ffbf', 
          '#00ffAA','#00ff95','#00ff80','#00ff6a','#00ff55','#00ff40','#00ff2A','#00ff15',
          '#00ff00','#17ff00','#2eff00','#46ff00','#5dff00','#74ff00','#8bff00','#a2ff00',
          '#b9ff00','#d1ff00','#e8ff00','#ffff00','#ffea00','#ffd500','#ffbf00','#ff9500',
          '#ffa500','#ff6a00','#ff5500','#ff4000','#ff2A00','#ff1500','#ff0000','#ff0000']

        levels = len(colors)
        cm     = branca.colormap.LinearColormap(colors, vmin=np.nanmin(RCS), vmax=np.nanmax(RCS)).to_step(levels)

        cs = plt.contourf(lons,lats,RCS.T,levels,colors=colors,alpha=0.5,vmin=np.nanmin(RCS), vmax=np.nanmax(RCS))
        geojson = geojsoncontour.contourf_to_geojson(
            contourf=cs,
            min_angle_deg=3.0,
            ndigits=5,
            stroke_width=1,
            fill_opacity=1)
         
        geomap = folium.Map([49.02028888888889,8.336347222222223], zoom_start=14,tiles='Stamen Terrain')
         
        folium.GeoJson(
            geojson,
            style_function=lambda x: {
                'color':     x['properties']['stroke'],
                'weight':    x['properties']['stroke-width'],
                'fillColor': x['properties']['fill'],
                'opacity':   1,
            }).add_to(geomap)
        folium.Marker([49.02028888888889,8.336347222222223], popup="<i>LIDAR Station</i>", tooltip='LIDAR Station').add_to(geomap)
        # Add the colormap to the folium map
        cm.caption = ('RCS'+self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S'))
        geomap.add_child(cm)
         
        # Fullscreen mode
        plugins.Fullscreen(position='topright', force_separate_button=True).add_to(geomap)
         
        # Plot the data
        # geomap.save('folium_contour_temperature_map.html')
        geomap.save('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarRCSMap/'+self.TimeFolderDir.split('/')[-1]+'.html')
        plt.close()
        
# super(AzimuthScanningMeasurement,self).ShowRCS()
    def CalculateAndDrawRefernce(self):
        GlueRawAverage  = np.nanmean(self.GlueRaw,axis=1)
        Noiselevel = np.nanmean(np.array(self.UV7d5mDP).T[-500:,:])
        if Noiselevel<0.1:
            Noiselevel =0.1  
        NoiseLine = np.ones(np.size(self.GlueRaw,0))*self.DepolSNR*Noiselevel
        # print(NoiseLine)
        # import pdb
        # pdb.set_trace()
        Line_1 = LineString(np.column_stack((self.Range[0:1500]/1000,GlueRawAverage[0:1500,])))
        line_2 = LineString(np.column_stack((self.Range[0:1500]/1000,NoiseLine[0:1500,])))
        intersection = Line_1.intersection(line_2)
        # adjust if it is multipoint
        if str(type(intersection)).split('.')[-1].startswith('Mu'):
            intersection = intersection.geoms[0]
        ReferenceHeightFitting = intersection.xy[0][0]*1000
        self.ReferenceIndexFitiing = int(ReferenceHeightFitting/(self.Range[1]-self.Range[0]))

        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/ReferencePoint/')):
               os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/ReferencePoint/'))
    
        with plt.style.context(['science','no-latex']):
            fig, ax = plt.subplots()
            ax.semilogy(self.Range[0:1500]/1000,GlueRawAverage[0:1500])
            ax.semilogy(self.Range[0:1500]/1000,NoiseLine[0:1500,])
            ax.semilogy(*intersection.xy,'ro')
            ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
            ax.set_xlim(0,10)
            ax.set(xlabel='Range [Km]')
            ax.set(ylabel='Amplitude')  
            fig.savefig(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/ReferencePoint/'+self.TimeFolderDir.split('/')[-1]+'.jpg'),dpi=300)
            plt.close()     
    def AeroFernald(self): 
        self.ReferenceIndex = int(self.ReferenceHeight/(self.Range[1]-self.Range[0]))
        # self.ReferenceIndex  = int(self.ReferenceHeight/(self.Range[1]-self.Range[0]))

        GlueRCS =[]
        for i in range (0,np.size(self.GlueRaw,axis=1)):
            GlueRCS.append(self.GlueRaw[:,i]*np.square(self.Range))
        GlueRCS = np.array(GlueRCS).T
        SlopIndex = [self.ReferenceIndexFitiing-50,self.ReferenceIndexFitiing] 
        
        R_zcs  = []
        for i in range(np.size(GlueRCS,1)):
            baseAlt=110                             
            baseLatitude=50.9084                        
            baseLongitude=6.4131
            betaMol=molecule_scatter(baseLatitude,baseLongitude,self.Range*np.sin(math.radians(abs(self.Zenith[i])))+baseAlt,self.DateTime[i])
            AlphaMol = self.Sm*betaMol
            a,b,r=helper_functions.linefit(self.Range[SlopIndex[0]:SlopIndex[1]],np.log(GlueRCS[SlopIndex[0]:SlopIndex[1],i]))
            R_zc= ((((-a)/2-np.nanmean(AlphaMol[SlopIndex[0]:SlopIndex[1]]))/self.Sa)/np.nanmean(betaMol[SlopIndex[0]:SlopIndex[1]]))
            if R_zc <0:
                 R_zc = 0         
            R_zcs.append(R_zc)  
        R_zcMean = np.nanmean(np.array(R_zcs))  
        # print('\n')
        # print(R_zcMean)
        # import pdb
        # pdb.set_trace()
        for i in range(np.size(self.GlueRaw,1)):  
            Data = {'Range':self.Range,
                    'Attitude':self.Range*np.sin(math.radians(abs(self.Zenith[i]))),
                    'Data':self.GlueRaw[:,i],
                    'Date':self.DateTime[i],
                    'ReferenceHeight':SlopIndex[0]*7.5,
                    'Sa': self.Sa,
                    'R_zc':R_zcMean
                    } 
                            # AeroFernaldAngle  =  backward_aero_fernald(Data,self.StationGeoInfo)

            AeroFernaldAngleB  =  backward_aero_fernald(Data,self.StationGeoInfo)
            # AeroFernaldAngleB.setGeographicInformation('Julich')
            # AeroFernaldAngleB.setDataInformation(Data)
            AeroFernaldAngleB()
            BetaAeroB = AeroFernaldAngleB.getAeroBeta()
            
            Data = {'Range':self.Range,
                            'Attitude':self.Range*np.sin(math.radians(abs(self.Zenith[i]))),
                            'Data':self.GlueRaw[:,i],
                            'Date':self.DateTime[i],
                            'ReferenceHeight':SlopIndex[0]*7.5,
                            'UpperReferenceHeight':self.ReferenceHeight,
                            'Sa': self.Sa,
                            'R_zc':R_zcMean
            } 
            # import pdb
            # pdb.set_trace()
            VerticalAeroFernaldAngleF  =  forward_aero_fernald(Data,self.StationGeoInfo)
            # VerticalAeroFernaldAngleF.setGeographicInformation('Karlsruhe')
            # VerticalAeroFernaldAngleF.setDataInformation(VerticalData)
            VerticalAeroFernaldAngleF()
            BetaAeroF = VerticalAeroFernaldAngleF.getAeroBeta()
            # BetaAeroF[:] = np.nan
            BetaAero = np.hstack((BetaAeroB[:SlopIndex[0]],BetaAeroF[SlopIndex[0]:]))
            self.BetaAeros.append(BetaAero)
        self.BetaAeros = np.array(self.BetaAeros).T
        
    def ShowBetaProfiles(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/BetaProfiles/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/BetaProfiles/'))
        # self.ReferenceIndex  = int(self.ReferenceHeight/(self.Range[1]-self.Range[0]))
        BetaAeros = np.where(self.BetaAeros<0,0,self.BetaAeros)
        # BetaAeros = np.where(np.isnan(BetaAeros),0,BetaAeros)
        BetaAeros = np.where(BetaAeros>2e-5,2e-5,BetaAeros)
        with plt.style.context(['science','no-latex']):
              fig, ax = plt.subplots(dpi=200)
              for i in range(0,np.size(BetaAeros,1)):
                  ax.plot(BetaAeros[20:self.ReferenceIndex,i]*1e6,self.Range[20:self.ReferenceIndex]/1000)
              ax.set_ylabel('Height [km]',fontdict={'weight': 'normal', 'size': 15})
              ax.set_xlabel('Backscattering coefficient [$\mathregular{m^-}$$\mathregular{^1}$$\mathregular{Sr^-}$$\mathregular{^1}$]',fontdict={'weight': 'normal', 'size': 15})
              ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
              # ax.legend()
              # ax.set_xlim([0, 5])
              ax.set_ylim([0, self.ReferenceHeight/1000])
              # ax.set_xlim([-1,4])
              plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/BetaProfiles/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
              plt.close()
              
    def ShowBetaPolar(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarBeta/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarBeta/'))
                
        Zenith = np.radians(np.abs(self.Zenith))   
        r, theta = np.meshgrid(self.Range[0:self.ReferenceIndex]/1000,np.radians(np.abs(self.Azimuth)))
        x,y,z = r*np.sin(theta)*np.cos(Zenith[0]),r*np.cos(theta)*np.cos(Zenith[0]),r*np.sin(Zenith[0])
        BetaAeros = self.BetaAeros*1e6
        BetaAeros = np.where(BetaAeros<0,0,BetaAeros)
        BetaAeros = np.where(np.isnan(BetaAeros),0,BetaAeros)
        BetaAeros = np.where(BetaAeros>20,20,BetaAeros)
        # BetaAeros[-1,-1]
        scamap = plt.cm.ScalarMappable(cmap='jet')
        fcolors = scamap.to_rgba(BetaAeros[0:self.ReferenceIndex,:].T)
        # print(np.size(fcolors.T,0))
        # print(np.size(x,0))
        with plt.style.context(['science','no-latex']):
              fig = plt.figure(figsize=(9,9),dpi=120)
              ax = fig.add_subplot(projection='3d')
              ax.plot_surface(x,y,z,facecolors=fcolors,rstride=1,cstride=1,cmap = 'jet')
              cbar=fig.colorbar(scamap,orientation='vertical',fraction=0.03,pad=0.1)
              cbar.set_label('Backscattering coefficient [M$\mathregular{m^-}$$\mathregular{^1}$$\mathregular{Sr^-}$$\mathregular{^1}$]')
              ax.set_xlim(0,10)
              ax.set_ylim(-10,10)
              ax.set_zlim(0,10)
              ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
              ax.set(xlabel='Range [km]')
              ax.set(ylabel='Range [km]')
              ax.set(zlabel='Range [km]')
              ax.set_box_aspect([1,2,1])
              plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarBeta/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
              plt.close()
    def ShowBetaPolarMap(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarBetaMap/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarBetaMap/'))
        Bin_size = 800
        BetaAeros = self.BetaAeros[0:Bin_size,:]*1e6
        BetaAeros = np.where(BetaAeros<0,0,BetaAeros)
        BetaAeros = np.where(np.isnan(BetaAeros),0,BetaAeros)
        BetaAeros = np.where(BetaAeros>20,20,BetaAeros)
        AzimuthHorizon =  np.array(self.Azimuth) - 10
        RangeHorizon = self.Range[0:Bin_size]/1000
        
        RangeHorizon,AzimuthHorizon = np.meshgrid(RangeHorizon,AzimuthHorizon)
        lons = np.ones_like(AzimuthHorizon)
        lats = np.ones_like(AzimuthHorizon)
        for i in range(0,np.size(AzimuthHorizon,0)):
            for j in range(0,np.size(AzimuthHorizon,1)):
                lats[i,j],lons[i,j] = self.convertRangeToLatLon(49.02028888888889,8.336347222222223,RangeHorizon[i,j],AzimuthHorizon[i,j])

        colors = ['#0000ff','#0015ff','#002aff','#0040ff','#0055ff','#006aff','#0080ff','#0095ff',
          '#00aaff','#00bfff','#00d5ff','#00eaff','#00ffff','#00ffea','#00ffd5','#00ffbf', 
          '#00ffAA','#00ff95','#00ff80','#00ff6a','#00ff55','#00ff40','#00ff2A','#00ff15',
          '#00ff00','#17ff00','#2eff00','#46ff00','#5dff00','#74ff00','#8bff00','#a2ff00',
          '#b9ff00','#d1ff00','#e8ff00','#ffff00','#ffea00','#ffd500','#ffbf00','#ff9500',
          '#ffa500','#ff6a00','#ff5500','#ff4000','#ff2A00','#ff1500','#ff0000','#ff0000']

        levels = len(colors)
        cm     = branca.colormap.LinearColormap(colors, vmin=np.nanmin(BetaAeros), vmax=np.nanmax(BetaAeros)).to_step(levels)

        cs = plt.contourf(lons,lats,BetaAeros.T,levels,colors=colors,alpha=0.5,vmin=np.nanmin(BetaAeros), vmax=np.nanmax(BetaAeros))
        geojson = geojsoncontour.contourf_to_geojson(
            contourf=cs,
            min_angle_deg=3.0,
            ndigits=5,
            stroke_width=1,
            fill_opacity=1)
         
        geomap = folium.Map([49.02028888888889,8.336347222222223], zoom_start=14,tiles='Stamen Terrain')
         
        folium.GeoJson(
            geojson,
            style_function=lambda x: {
                'color':     x['properties']['stroke'],
                'weight':    x['properties']['stroke-width'],
                'fillColor': x['properties']['fill'],
                'opacity':   1,
            }).add_to(geomap)
        folium.Marker([49.02028888888889,8.336347222222223], popup="<i>LIDAR Station</i>", tooltip='LIDAR Station').add_to(geomap)
        # Add the colormap to the folium map
        cm.caption = ('Backscattering coefficient [M 1/(m*sr)]'+self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S'))
        geomap.add_child(cm)
         
        # Fullscreen mode
        plugins.Fullscreen(position='topright', force_separate_button=True).add_to(geomap)
         
        # Plot the data
        # geomap.save('folium_contour_temperature_map.html')
        geomap.save('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarBetaMap/'+self.TimeFolderDir.split('/')[-1]+'.html')
        plt.close()
        
    def ShowDepolarizationProfiles(self):
        self.DepoIndex = int(self.ShowDepolHeight/(self.Range[1]-self.Range[0]))
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/DepolarizationProfiles/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/DepolarizationProfiles/'))
        # self.ReferenceIndex  = int(self.ReferenceHeight/(self.Range[1]-self.Range[0]))
    
        with plt.style.context(['science','no-latex']):
              fig, ax = plt.subplots(dpi=200)
              for i in range(0,np.size(self.DepolarizationRatio,1)):
                  ax.plot(self.DepolarizationRatio[20:self.DepoIndex,i]*1e2,self.Range[20:self.DepoIndex]/1000)
              ax.set_ylabel('Height [km]',fontdict={'weight': 'normal', 'size': 15})
              ax.set_xlabel('Depolarization Ratio [%]',fontdict={'weight': 'normal', 'size': 15})
              ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
              # ax.legend()
              # ax.set_xlim([0, 5])
              ax.set_ylim([0, self.DepoIndex/1000])
              # ax.set_xlim([-1,4])
              plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/DepolarizationProfiles/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
              plt.close()
              
    def ShowDepolarizationPolar(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarDepolarization/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarDepolarization/'))
                
        Zenith = np.radians(np.abs(self.Zenith))   
        r, theta = np.meshgrid(self.Range[0:self.ReferenceIndex]/1000,np.radians(np.abs(self.Azimuth)))
        x,y,z = r*np.sin(theta)*np.cos(Zenith[0]),r*np.cos(theta)*np.cos(Zenith[0]),r*np.sin(Zenith[0])
        DepolarizationRatio = np.where(np.isnan(self.DepolarizationRatio),0,self.DepolarizationRatio)
        DepolarizationRatio = DepolarizationRatio*100
        # DepolarizationRatio = np.where(DepolarizationRatio>20,0,DepolarizationRatio)
        DepolarizationRatio = np.where(DepolarizationRatio<0,np.nan,DepolarizationRatio)
        # BetaAeros[-1,-1]
        scamap = plt.cm.ScalarMappable(cmap='jet')
        fcolors = scamap.to_rgba(DepolarizationRatio[0:self.ReferenceIndex,:].T)
        # print(np.size(fcolors.T,0))
        # print(np.size(x,0))
        with plt.style.context(['science','no-latex']):
              fig = plt.figure(figsize=(9,9),dpi=120)
              ax = fig.add_subplot(projection='3d')
              ax.plot_surface(x,y,z,facecolors=fcolors,rstride=1,cstride=1,cmap = 'jet')
              cbar=fig.colorbar(scamap,orientation='vertical',fraction=0.03,pad=0.1)
              cbar.set_label('Volume Depolarization Ratio [%]')
              ax.set_xlim(0,10)
              ax.set_ylim(-10,10)
              ax.set_zlim(0,10)
              ax.set_title(self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S')+' - '+self.DateTime[-1].strftime('%Y-%m-%d %H:%M:%S')+'(UTC)')
              ax.set(xlabel='Range [km]')
              ax.set(ylabel='Range [km]')
              ax.set(zlabel='Range [km]')
              ax.set_box_aspect([1,2,1])
              plt.savefig('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarDepolarization/'+self.TimeFolderDir.split('/')[-1]+'.jpg')
              plt.close()
    def ShowpolarizationPolarMap(self):
        os.chdir(os.path.dirname(__file__))
        if not os.path.exists(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarDepolarizationMap/')):
                os.makedirs(('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarDepolarizationMap/'))
        Bin_size = 800
        DepolarizationRatio = np.where(np.isnan(self.DepolarizationRatio),0,self.DepolarizationRatio)
        DepolarizationRatio = DepolarizationRatio[0:Bin_size,:]*100
        DepolarizationRatio = np.where(DepolarizationRatio<0,np.nan,DepolarizationRatio)
        AzimuthHorizon =  np.array(self.Azimuth) - 10
        RangeHorizon = self.Range[0:Bin_size]/1000
        
        RangeHorizon,AzimuthHorizon = np.meshgrid(RangeHorizon,AzimuthHorizon)
        lons = np.ones_like(AzimuthHorizon)
        lats = np.ones_like(AzimuthHorizon)
        for i in range(0,np.size(AzimuthHorizon,0)):
            for j in range(0,np.size(AzimuthHorizon,1)):
                lats[i,j],lons[i,j] = self.convertRangeToLatLon(49.02028888888889,8.336347222222223,RangeHorizon[i,j],AzimuthHorizon[i,j])

        colors = ['#0000ff','#0015ff','#002aff','#0040ff','#0055ff','#006aff','#0080ff','#0095ff',
          '#00aaff','#00bfff','#00d5ff','#00eaff','#00ffff','#00ffea','#00ffd5','#00ffbf', 
          '#00ffAA','#00ff95','#00ff80','#00ff6a','#00ff55','#00ff40','#00ff2A','#00ff15',
          '#00ff00','#17ff00','#2eff00','#46ff00','#5dff00','#74ff00','#8bff00','#a2ff00',
          '#b9ff00','#d1ff00','#e8ff00','#ffff00','#ffea00','#ffd500','#ffbf00','#ff9500',
          '#ffa500','#ff6a00','#ff5500','#ff4000','#ff2A00','#ff1500','#ff0000','#ff0000']

        levels = len(colors)
        cm     = branca.colormap.LinearColormap(colors, vmin=np.nanmin(DepolarizationRatio), vmax=np.nanmax(DepolarizationRatio)).to_step(levels)

        cs = plt.contourf(lons,lats,DepolarizationRatio.T,levels,colors=colors,alpha=0.5,vmin=np.nanmin(DepolarizationRatio), vmax=np.nanmax(DepolarizationRatio))
        geojson = geojsoncontour.contourf_to_geojson(
            contourf=cs,
            min_angle_deg=3.0,
            ndigits=5,
            stroke_width=1,
            fill_opacity=1)
         
        geomap = folium.Map([49.02028888888889,8.336347222222223], zoom_start=14,tiles='Stamen Terrain')
         
        folium.GeoJson(
            geojson,
            style_function=lambda x: {
                'color':     x['properties']['stroke'],
                'weight':    x['properties']['stroke-width'],
                'fillColor': x['properties']['fill'],
                'opacity':   1,
            }).add_to(geomap)
        folium.Marker([49.02028888888889,8.336347222222223], popup="<i>LIDAR Station</i>", tooltip='LIDAR Station').add_to(geomap)
        # Add the colormap to the folium map
        cm.caption = ('Volume depolarization ratio'+self.DateTime[0].strftime('%Y-%m-%d %H:%M:%S'))
        geomap.add_child(cm)
         
        # Fullscreen mode
        plugins.Fullscreen(position='topright', force_separate_button=True).add_to(geomap)
         
        # Plot the data
        # geomap.save('folium_contour_temperature_map.html')
        geomap.save('../'+self.DateTime[0].strftime('%Y%m%d')+'/Figure/PolarDepolarizationMap/'+self.TimeFolderDir.split('/')[-1]+'.html')
        plt.close()


# DayPath = 'D:/hengheng zhang/raymetrics/Lidar_Data/2018/Scanning_Measurements/07/12'
# ConfigInfo ={'GlueRangeIndex':300,'V_constant':0.0335,'ZenithReferenceHeight':4000,
#               'Sa':40,'R_zc':1.0,'ShowDepolIndex':13333,'DepolSNR':3,'AzimuthRefereceHeight':10000}  
# DayPath = 'D:/hengheng zhang/raymetrics/Lidar_Data/2018/Scanning_Measurements/07/12'
# TimeFolderNames=[]
# for file in os.listdir(DayPath):
#     if file.startswith('AS'):
#         TimeFolderNames.append(file)
# for TimeFoldername in tqdm(TimeFolderNames[5:6]):
#     TimeFolderDir = (DayPath + '/'+TimeFoldername)
#     AzimuthScanningMeasurementI  = AzimuthScanningMeasurement(TimeFolderDir,ConfigInfo)
#     AzimuthScanningMeasurementI.ReadData()
#     # print(AzimuthScanningMeasurementI.BinWidthCheck)
#     if  AzimuthScanningMeasurementI.BinWidthCheck:
#         AzimuthScanningMeasurementI.DataPreProcess()
#     # aa = AzimuthScanningMeasurementI.DataSets
#         AzimuthScanningMeasurementI.OverlapCorrection()
#         AzimuthScanningMeasurementI.CalculateAndDrawRefernce()

#         AzimuthScanningMeasurementI.ShowRCSProfiles()
#         AzimuthScanningMeasurementI.ShowRCSPolar()
#         AzimuthScanningMeasurementI.AeroFernald()
#         AzimuthScanningMeasurementI.ShowBetaProfiles()
#         AzimuthScanningMeasurementI.ShowBetaProfiles()
#         AzimuthScanningMeasurementI.ShowBetaPolar()
#         AzimuthScanningMeasurementI.SaveBeta()
#         AzimuthScanningMeasurementI.DepolarizationCal()
#         AzimuthScanningMeasurementI.ShowDepolarizationProfiles()
#         AzimuthScanningMeasurementI.ShowDepolarizationPolar()
#         AzimuthScanningMeasurementI.SaveDepolarization()

#     # aa = AzimuthScanningMeasurementI.BetaAeros
