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

#Data Key for metocean sensors
Position     Length     Field     
1              8          Strain                     N  (percentage)
9              6          Battery voltage            N * 0.2 + 5
15             10        Sea surface temperature     N * 0.04 – 2.00
25             8         Checksum                    Modulus 256 of sum of previous 3 bytes
32 bytes total     

"""
import argparse
import datetime
import pandas as pd
from io import BytesIO

from io_utils import ConfigParserLocal
from plots import ArgosDrifters

"""-----------------------------------------------------Data Classes----------------------------------------------------------"""

class ARGOS_SERVICE_Drifter(object):
    r"""

    """
    def __init__(self, missing=1e35):
      self.missing = missing

    @staticmethod
    def get_data(filename=None):
        r"""
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments
        """

        fobj = open(filename)
        data = fobj.read()


        buf = data
        return BytesIO(buf.strip())

    @staticmethod
    def parse(fobj):
        r"""

        """
        argo_to_datetime =lambda date: datetime.datetime.strptime(date, '%Y %j %H%M')

        header=['argosid','lat','lon','year','doy','hhmm','s1','s2','s3','s4','s5','s6','s7','s8']
        df = pd.read_csv(fobj,delimiter='\s+',header=0,
          names=header,index_col=False,error_bad_lines=False,
          dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str},
          parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime)

        df['lon']=df['lon'] * -1 #convert to +W

        df.set_index(pd.DatetimeIndex(df['year_doy_hhmm']),inplace=True)
        df.drop('year_doy_hhmm',axis=1,inplace=True)

        return df


    def sst_argos(self,s1,s2):
        try:
            output = int(format(int(s1,16),'08b')[6:] + format(int(s2,16),'08b'),2) 
            output = (output * 0.04) - 2.0   
        except:
            output = self.missing
        return output

    def strain_argos(self,s1,manufacter='MetOcean'):
        try:
          converted_word = int(format(int(s1,16),'08b'),2)
          if manufacter == 'MetOcean':
            output = converted_word
          else:
            output = converted_word / 100.
        except:
          output = self.missing
        return output

    def voltage_argos(self,s1):
        try:
            converted_word = int(format(int(s1,16),'08b')[:6],2)
            output = (converted_word * 0.2) + 5   
        except:
            output = self.missing
        return output

    def checksum_argos(self,s1,s2,s3,s4):
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
            output = self.missing
        return output

class ARGOS_SERVICE_Buoy(object):
    r"""

    """
    def __init__(self, missing=1e35):
      self.missing = missing

    @staticmethod
    def get_data(filename=None):
        r"""
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments
        """

        fobj = open(filename)
        data = fobj.read()


        buf = data
        return BytesIO(buf.strip())

    @staticmethod
    def parse(fobj):
        r"""
          Date,AT,RH,WS,WD,BP,QS,AZ,BV
        """
        argo_to_datetime =lambda date: datetime.datetime.strptime(date, '%Y %j %H%M')

        header=['argosid','lat','lon','year','doy','hhmm','s1','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','s12']
        columns=range(0,18,1)
        df = pd.read_csv(fobj,delimiter='\s+',header=0,
          names=header,index_col=False,usecols=columns,error_bad_lines=False,
          dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str,'s9':str,'s10':str,'s11':str,'s12':str},
          parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime)

        df['lon']=df['lon'] * -1 #convert to +W

        df.set_index(pd.DatetimeIndex(df['year_doy_hhmm']),inplace=True)
        df.drop('year_doy_hhmm',axis=1,inplace=True)

        return df

    def BP(self,s1):
      r"""
        Convert Barometric Pressure
      """
      try:
        output = (int(s1,16) / 0.85 ) + 800
        if (output > 1060) or (output < 940):
          output = self.missing
      except:
        output = self.missing

      return output

    def AT(self,s1,s2):
      r"""
        Convert Air Temperature
      """
      try:
        output = (int((s1+s2),16) / 10. ) - 50.
        if (output > 40) or (output < -20):
          output = self.missing
      except:
        output = self.missing

      return output

    def BV(self,s1):
      r"""
        Convert Battery Voltage
      """
      try:
        output = int(s1,16)
        if (output > 40) or (output < 0):
          output = self.missing
      except:
        output = self.missing

      return output

    def RH(self,s1):
      r"""
        Convert Relative Humidity
      """
      try:
        output = int(s1,16) 
        if (output > 100) or (output <= 0):
          output = self.missing
      except:
        output = self.missing

      return output

    def WS(self,s1,s2):
      r"""
        Convert Wind Speed
      """
      try:
        output = (int(s1+s2,16) / 10. )
        if (output > 50) or (output < 0):
          output = self.missing
      except:
        output = self.missing

      return output

    def WD(self,s1,magnetic_dec=0):
      r"""
        Convert Wind Direction (+magnetic declination correction)
      """
      try:
        output = (int(s1,16) / 0.7083 ) + magnetic_dec
      except:
        output = self.missing

      return output

    def SR(self,s1):
      r"""
        Convert Solar Radiation
      """
      try:
        output = (int(s1,16) / 0.18214 )
        if (output > 1400) or (output < 0):
          output = self.missing
      except:
        output = self.missing

      return output

    def AZ(self,s1):
      r"""
        Convert Azimuth angle
      """
      try:
        output = (int(s1,16) / 0.7083 )
      except:
        output = self.missing
        
      return output



"""---------------------------------------------------------Main--------------------------------------------------------------"""

# parse incoming command line options
parser = argparse.ArgumentParser(description='Read Argos formatted drifterid.yyyy files')
parser.add_argument('sourcefile', metavar='sourcefile', type=str, help='path to yearly drifter files parsed by ID')
parser.add_argument('version', metavar='version', type=str, help='buoy,v1-metocean(pre-2017),v2-vendor(2017)')
parser.add_argument('-csv','--csv', type=str, help='output as csv - full path')
parser.add_argument('-config','--config', type=str, help='read local config file')
parser.add_argument('-plot','--plot', action="store_true", help='plot data')
parser.add_argument('-interpolate','--interpolate', action="store_true", help='interpolate data to hourly')

args = parser.parse_args()


if args.version in ['v1','V1','version1','v1-metocean']:

    atseadata = ARGOS_SERVICE_Drifter()

    df = atseadata.parse(atseadata.get_data(args.sourcefile))
    
    df['strain']= df.apply(lambda row: atseadata.strain_argos(row['s1'],manufacter='MetOcean'), axis=1)
    df['voltage']= df.apply(lambda row: atseadata.voltage_argos(row['s2']), axis=1)
    df['sst']= df.apply(lambda row: atseadata.sst_argos(row['s2'], row['s3']), axis=1)
    df['checksum']= df.apply(lambda row: atseadata.checksum_argos(row['s1'], row['s2'], row['s3'], row['s4']), axis=1)
    df.drop(['s1','s2','s3','s4','s5','s6','s7','s8'], axis=1, inplace=True)

elif args.version in ['v2','V2','version2','v2-vendor(2017)']:
    
    atseadata = ARGOS_SERVICE_Drifter()

    df = atseadata.parse(atseadata.get_data(args.sourcefile))
    
    df['strain']= df.apply(lambda row: atseadata.strain_argos(row['s1']), axis=1)
    df['voltage']= df.apply(lambda row: atseadata.voltage_argos(row['s2']), axis=1)
    df['sst']= df.apply(lambda row: atseadata.sst_argos(row['s2'], row['s3']), axis=1)
    df['checksum']= df.apply(lambda row: atseadata.checksum_argos(row['s1'], row['s2'], row['s3'], row['s4']), axis=1)
    df.drop(['s1','s2','s3','s4','s5','s6','s7','s8'])

elif args.version in ['buoy','met','sfc_package']:
    
    atseadata = ARGOS_SERVICE_Buoy(missing=None)

    df = atseadata.parse(atseadata.get_data(args.sourcefile))

    df['BP']= df.apply(lambda row: atseadata.BP(row['s3']), axis=1)
    df['AT']= df.apply(lambda row: atseadata.AT(row['s4'],row['s5']), axis=1)
    df['BV']= df.apply(lambda row: atseadata.BV(row['s6']), axis=1)
    df['RH']= df.apply(lambda row: atseadata.RH(row['s7']), axis=1)
    df['WS']= df.apply(lambda row: atseadata.WS(row['s8'],row['s9']), axis=1)
    df['WD']= df.apply(lambda row: atseadata.WD(row['s10']), axis=1)
    df['SR']= df.apply(lambda row: atseadata.SR(row['s11']), axis=1)
    df['AZ']= df.apply(lambda row: atseadata.AZ(row['s12']), axis=1)

    df.drop(['s1','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','s12'], axis=1, inplace=True)
    
else:
    print("No recognized argos-pmel version")

if args.config:
  config_settings = ConfigParserLocal.get_config_yaml(args.config)
  df = df.ix[config_settings['Mooring']['StartDate']:config_settings['Mooring']['EndDate']]

if args.interpolate:
  #hourly binned with linear interpolation to fill gaps
  df = df.resample('1H',label='right',closed='right').mean().interpolate(method='linear')

if args.csv:
    df.to_csv(args.csv)

if args.plot:
  driftermap = ArgosDrifters.ArgosPlot(df=df)
  #(ax,fig1) = driftermap.make_map(param='doy')
  (ax,fig1) = driftermap.make_map(param='sst')
  