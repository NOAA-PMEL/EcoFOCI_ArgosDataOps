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

"""

import pandas as pd
import datetime


def sst_exits(s1,s2):
    try:
        output = int(bin(int(s1,16))[8:10]+bin(int(s2,16))[2:],2) 
        output = (output * 0.04) - 2.0   
    except:
        output = 1e35
    return output

filein='/Volumes/WDC_internal/Users/bell/Programs/Python/ArgosDataOps/DailyRetrievalRoutines/yearlyArgosID/148276.y2017'
argo_to_datetime =lambda date: datetime.datetime.strptime(date, '%Y %j %H%M')

header=['argosid','lat','lon','year','doy','hhmm','s1','s2','s3','s4','s5','s6','s7','s8']
df = pd.read_csv(filein,delimiter='\s+',header=0,
  names=header,index_col=False,
  dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str},
  parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime)

df.set_index(pd.DatetimeIndex(df['year_doy_hhmm']),inplace=True)
df.drop('year_doy_hhmm',axis=1,inplace=True)

# sst
df['sst']= df.apply(lambda row: sst_exits(row['s1'], row['s2']), axis=1)

dfh = df.resample('1H',closed='right', label='right').mean().interpolate()