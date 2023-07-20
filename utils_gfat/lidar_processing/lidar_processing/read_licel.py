# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 13:14:48 2021

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function：

"""
import numpy as np
# import FunctionModel
from datetime import datetime 
# import FunctionModel
import logging
import utils_gfat.lidar_processing.lidar_processing.helper_functions as helper_functions

c = 299792458.0 

logger = logging.getLogger(__name__)
#%% define parameter 
licel_file_header_format = ['filename',
                                'start_date start_time end_date end_time altitude longitude latitude zenith_angle azimuth_angle',
                                # Appart from Site that is read manually
                                'LS1 rate_1 LS2 rate_2 number_of_datasets', ]
licel_file_channel_format = 'active analog_photon laser_used number_of_datapoints 1 HV bin_width wavelength d1 d2 d3 d4 ADCbits number_of_shots discriminator ID'

#%% define function 
def match_lines(f1, f2):
        # TODO: Change this to regex?
        list1 = f1.split()
        list2 = f2.split()
        combined = list(zip(list2, list1))
        combined = dict(combined)
        return combined
    
def read_second_header_line(f):
    """ Read the second line of a licel file. """
    raw_info = {}

    second_line = f.readline().decode()
    site_name = second_line.split('/')[0][:-2]
    clean_site_name = site_name.strip()
    raw_info['site'] = clean_site_name
    raw_info.update(match_lines(second_line[len(clean_site_name) + 1:], licel_file_header_format[1]))
    return raw_info
    

def read_rest_of_header(f):
    """ Read the rest of the header lines, after line 2. """
    # Read third line
    third_line = f.readline().decode()
    if len(third_line.split()) == 7: 
        third_line = f.readline().decode()
    # print(len(Forth_line.split()))

    raw_dict = match_lines(third_line, licel_file_header_format[2])
    return raw_dict
# FilePath = 'RM2121214.561377'
def read_licel(FilePath):
    raw_info = {}
    channel_info = []
    RawData = {}
    with open(FilePath, 'rb') as f:
        first_line = f.readline().decode().strip()
        raw_info['Filename'] = first_line
        raw_info.update(read_second_header_line(f))
        raw_info.update(read_rest_of_header(f))
        start_string = '%s %s' % (raw_info['start_date'], raw_info['start_time'])
        stop_string = '%s %s' % (raw_info['end_date'], raw_info['end_time'])
        date_format = '%d/%m/%Y %H:%M:%S'
        # According to pytz docs, timezones do not work with default datetime constructor.
        start_time = datetime.strptime(start_string, date_format)
        stop_time = datetime.strptime(stop_string, date_format)
        ShootsNumber = int(raw_info['LS1'])
        StationGeoInfo = {'altitude':float(raw_info['altitude']),
                          'longitude':float(raw_info['longitude']),
                          'latitude':float(raw_info['latitude'])}

        ScanningAngle =(float(raw_info['zenith_angle']),float(raw_info['azimuth_angle']))  
        for c1 in range(int(raw_info['number_of_datasets'])):
            channel_line = f.readline().decode()
            channel_info.append(match_lines(channel_line,licel_file_channel_format))
      
            
        # Check the complete header is read
        f.readline()
        channel_info = channel_info[:-1]
        VarName = []
        # check binwith  == 7.5
        BinWidthCheck = True
        for channel_no, current_channel_info in enumerate(channel_info):
            # print(channel_no)
            # print(current_channel_info['number_of_datapoints'])
            raw_data = np.fromfile(f, 'i4', int(current_channel_info['number_of_datapoints']))
            a = np.fromfile(f, 'b', 1)
            b = np.fromfile(f, 'b', 1)
            if (a[0] != 13) | (b[0] != 10):
                logger.warning("No end of line found after record. File could be corrupt: %s" % FilePath)
                logger.warning('a: {0}, b: {1}.'.format(a, b))
            # print(current_channel_info['bin_width'])
            VarName.append(helper_functions.data_type(int(current_channel_info['wavelength'].split('.')[0]),
                                                          float(current_channel_info['bin_width']),
                                                          int(current_channel_info['analog_photon']),
                                                          current_channel_info['wavelength'].split('.')[1]))
            # print(VarName[channel_no])
            
          
            # duration = (stop_time - start_time).seconds
            
            number_of_shots = int(current_channel_info['number_of_shots'])
            bin_width = float(current_channel_info['bin_width'])
            # print(bin_width)
            BinWidthCheck = (bin_width == 7.5) and BinWidthCheck
            
            adcbits = int(current_channel_info['ADCbits'])
            discriminator = float(current_channel_info['discriminator'])
            
            norm = raw_data / float(number_of_shots)
            ADCrange = discriminator*1000  # Discriminator value already in mV
            if VarName[channel_no][-2] == 'A':
                channel_data = norm * ADCrange / (
                                (2 ** adcbits) - 1)  # Licel LabView code has a bug (does not account -1).
                channel_data = channel_data[9:]
            else:
                Bintime = 2*bin_width/c
                channel_data = norm/(Bintime*1e6) # convertion to MHZ
                channel_data = channel_data[0:-9]
            channel_data = np.vstack((np.arange(1,len(channel_data)+1)*7.5,channel_data)).T
            RawData.update({VarName[channel_no]:{'Data':channel_data}})
        RawData.update({'DateTime':stop_time,'ScanningAngle':ScanningAngle,
                        'shoots':ShootsNumber,'StationGeoInfo':StationGeoInfo,
                        'BinWithCheck':BinWidthCheck})
        # print(BinWidthCheck)
        return RawData