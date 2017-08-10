# -*- coding: utf-8 -*-
"""

Created on Wed Feb  1 12:27:42 2017

@author: bell

Discussion:  
-----------

For drifter data (and many other datasets)... there are multiple ways to put on a fixed time grid:

downsample (either through decimation or averaging)
	decimation: ignores all sub timestep features.  Good for slowly varying data.
	averaging: smooths sub timestep features.  Valid at midpoint of data period

upsample (interpolate then average/decimate or average/decimate then interpolate)

--
#Data Key for non-metocean sensors
Position     Length     Field     
1              8          Strain                     N / 100  (percentage)
9              6          Battery voltage            N * 0.2 + 5
15             10        Sea surface temperature     N * 0.04 – 2.00
25             8         Checksum                    Modulus 256 of sum of previous 3 bytes
32 bytes total     

"""
import argparse
import pandas as pd
import datetime


def sst_argos(s1,s2):
    try:
        output = int(format(int(s1,16),'08b')[6:] + format(int(s2,16),'08b'),2) 
        output = (output * 0.04) - 2.0   
    except:
        output = 1e35
    return output

def strain_argos(s1):
    try:
      converted_word = int(format(int(s1,16),'08b'),2)
      output = converted_word / 100.
    except:
      output = 1e35
    return output

def voltage_argos(s1):
    try:
        converted_word = int(format(int(s1,16),'08b')[:6],2)
        output = (converted_word * 0.2) + 5   
    except:
        output = 1e35
    return output

def checksum_argos(s1,s2,s3,s4):
    try:
        converted_word = int(format(int(s1,16),'08b'),2) + \
                         int(format(int(s2,16),'08b'),2) + \
                         int(format(int(s3,16),'08b'),2)
        checksum_test = converted_word % 256 
        if  checksum_test == int(format(int(s4,16),'08b'),2):
          output = True
        else:
          output = False
    except:
        output = 1e35
    return output

"""---------------------------------------------------------Main--------------------------------------------------------------"""
filein='/Users/bell/ecoraid/ArgosDataRetrieval/Archive/2017/139910.y2017'
argo_to_datetime =lambda date: datetime.datetime.strptime(date, '%Y %j %H%M')

header=['argosid','lat','lon','year','doy','hhmm','s1','s2','s3','s4','s5','s6','s7','s8']
df = pd.read_csv(filein,delimiter='\s+',header=0,
  names=header,index_col=False,
  dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str},
  parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime)

df.set_index(pd.DatetimeIndex(df['year_doy_hhmm']),inplace=True)
df.drop('year_doy_hhmm',axis=1,inplace=True)

# sst
df['strain']= df.apply(lambda row: strain_argos(row['s1']), axis=1)
# sst
df['voltage']= df.apply(lambda row: voltage_argos(row['s2']), axis=1)
# sst
df['sst']= df.apply(lambda row: sst_argos(row['s2'], row['s3']), axis=1)
# sst
df['checksum']= df.apply(lambda row: checksum_argos(row['s1'], row['s2'], row['s3'], row['s4']), axis=1)

