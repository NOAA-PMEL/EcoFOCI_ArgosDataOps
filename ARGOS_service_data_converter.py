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

Uses cleaned id.year datafiles with format as follows for wpak
028882 47.683 -122.265 2018 066 0220 02 0A BE 02 4E 0E 31 00 10 EA 02 C0 BE 02 5E 0E 2E 00 0C ED 05 C0 BE 02 68 0E 2A 00 13 E5 38 C0   1
and for a drifter
136866 61.424 -171.133 2018 001 0007 09 C4 40 0D A4 6D 49   3


 History:
 --------
 2020-06-25: add location quality flag data to output of drifter stream
 2018-10-01: add geojson output option
 2018-09-05: Dont write empty dataframes to netcdf
 2018-07-30: Merge the get and parse functions... buffered or streamin not translating well. (programmer limitation)
 2018-03-20: Buoy wpak transmitted data has three consecutive hours included.  Use 
    this data to fill gaps when no location lock was completed.  Option is added as
    "buoy_3hr" to the version flag
 2018-03-13: Ingest two starter characters that represent time (hour and minute) 
    and output seconds since midnight.
 2018-03-12: Add netcdf output option
 2024-12-04: Modify pandas date_parse to be pandas 2.X compliant
 2024-12-09: Swap Xarray for lowerlevel NetCDF creation

 Compatibility:
 ==============
 python >=3.9 **tested**

"""
import argparse
import sys
import pandas as pd
import numpy as np
import xarray as xa
from datetime import datetime, timezone
from netCDF4 import date2num, num2date


# User Stack
import io_utils.EcoFOCI_netCDF_write as EcF_write
import io_utils.ConfigParserLocal as ConfigParserLocal

from io_utils import ConfigParserLocal

"""-----------------------------------------------------Data Classes----------------------------------------------------------"""


class ARGOS_SERVICE_Beacon(object):
    r"""

    """

    def __init__(self, missing=1e35):
        self.missing = missing

    @staticmethod
    def get_data(fobj=None):
        r"""
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        """

        header = [
            "argosid",
            "latitude",
            "longitude",
            "year",
            "doy",
            "hhmm",
            "s1",
            "s2",
            "s3",
            "s4",
        ]
        df = pd.read_csv(
            fobj,
            delimiter=r"\s+",
            header=None,
            names=header,
            index_col=False,
            on_bad_lines='warn',
            dtype={
                "year": str,
                "doy": str,
                "hhmm": str,
                "s1": str,
                "s2": str,
                "s3": str,
                "s4": str,
            },
        )
        #pad hhmm and doy with 0's
        df["doy"] = df["doy"].str.zfill(3)
        df["hhmm"] = df["hhmm"].str.zfill(4)

        df["year_doy_hhmm"] = pd.to_datetime(arg=df.pop("year").str.cat(df.pop("doy")).str.cat(df.pop("hhmm")),
                                             format="%Y%j%H%M")
        df["longitude"] = df["longitude"] * -1  # convert to +W
        df["longitude"] = df.longitude.round(3)
        df["latitude"] = df.latitude.round(3)

        df.set_index(pd.DatetimeIndex(df["year_doy_hhmm"]), inplace=True)
        # df.drop('year_doy_hhmm',axis=1,inplace=True)

        return df

class ARGOS_SERVICE_Drifter(object):
    r"""

    """

    def __init__(self, missing=1e35):
        self.missing = missing

    @staticmethod
    def get_data(fobj=None):
        r"""
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        """

        header = [
            "argosid",
            "latitude",
            "longitude",
            "year",
            "doy",
            "hhmm",
            "s1",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
        ]
        df = pd.read_csv(
            fobj,
            delimiter=r"\s+",
            header=None,
            names=header,
            index_col=False,
            on_bad_lines='warn',
            dtype={
                "year": str,
                "doy": str,
                "hhmm": str,
                "s1": str,
                "s2": str,
                "s3": str,
                "s4": str,
                "s5": str,
                "s6": str,
                "s7": str,
                "s8": str,
            },
        )
        #pad hhmm and doy with 0's
        df["doy"] = df["doy"].str.zfill(3)
        df["hhmm"] = df["hhmm"].str.zfill(4)

        df["year_doy_hhmm"] = pd.to_datetime(arg=df.pop("year").str.cat(df.pop("doy")).str.cat(df.pop("hhmm")),
                                             format="%Y%j%H%M")
        df["longitude"] = df["longitude"] * -1  # convert to +W
        df["longitude"] = df.longitude.round(3)
        df["latitude"] = df.latitude.round(3)

        df.set_index(pd.DatetimeIndex(df["year_doy_hhmm"]), inplace=True)
        # df.drop('year_doy_hhmm',axis=1,inplace=True)

        return df

    def sst_argos(self, s1, s2):
        try:
            output = int(format(int(s1, 16), "08b")[6:] + format(int(s2, 16), "08b"), 2)
            output = (output * 0.04) - 2.0
        except:
            output = self.missing
        return output

    def strain_argos(self, s1, manufacter="MetOcean"):
        try:
            converted_word = int(format(int(s1, 16), "08b"), 2)
            if manufacter == "MetOcean":
                output = converted_word
            else:
                output = converted_word / 100.0
        except:
            output = self.missing
        return output

    def voltage_argos(self, s1):
        try:
            converted_word = int(format(int(s1, 16), "08b")[:6], 2)
            output = (converted_word * 0.2) + 5
        except:
            output = self.missing
        return output

    def checksum_argos(self, s1, s2, s3, s4):
        try:
            converted_word = (
                int(format(int(s1, 16), "08b"), 2)
                + int(format(int(s2, 16), "08b"), 2)
                + int(format(int(s3, 16), "08b"), 2)
            )
            checksum_test = converted_word % 256
            if checksum_test == int(format(int(s4, 16), "08b"), 2):
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
    def get_data(fobj=None, time="current"):
        r"""
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        Parse the WPAK data which has three sample points reported at each transmission.

        time='current' will only return the most recent data point for each transmission
        time='1hr' will only return the sample point from one hour prior
        time='2hr' will only return the sample point from two hours prior
        
        concatenate the three independant calls and you will have the most populated data set.
        
        Date,AT,RH,WS,WD,BP,QS,AZ,BV
        """

        header = [
            "argosid",
            "latitude",
            "longitude",
            "year",
            "doy",
            "hhmm",
            "s1",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
            "s9",
            "s10",
            "s11",
            "s12",
        ]
        dtype = {
            "year": str,
            "doy": str,
            "hhmm": str,
            "s1": str,
            "s2": str,
            "s3": str,
            "s4": str,
            "s5": str,
            "s6": str,
            "s7": str,
            "s8": str,
            "s9": str,
            "s10": str,
            "s11": str,
            "s12": str,
        }

        if time in ["current"]:
            columns = range(0, 18, 1)
        elif time in ["1hr"]:
            columns = [0, 1, 2, 3, 4, 5, 6, 7, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        elif time in ["2hr"]:
            columns = [0, 1, 2, 3, 4, 5, 6, 7, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]

        df = pd.read_csv(
            fobj,
            delimiter=r"\s+",
            header=None,
            names=header,
            index_col=False,
            usecols=columns,
            on_bad_lines='warn',
            dtype=dtype,
        )
        #pad hhmm and doy with 0's
        df["doy"] = df["doy"].str.zfill(3)
        df["hhmm"] = df["hhmm"].str.zfill(4)

        df["year_doy_hhmm"] = pd.to_datetime(arg=df.pop("year").str.cat(df.pop("doy")).str.cat(df.pop("hhmm")),
                                             format="%Y%j%H%M")
        df["longitude"] = df["longitude"] * -1  # convert to +W

        df.set_index(pd.DatetimeIndex(df["year_doy_hhmm"]), inplace=True)
        # df.drop('year_doy_hhmm',axis=1,inplace=True)

        return df

    def time(self, s1, s2):
        r"""
        Convert two hex words which represent hour and min into seconds since midnight
      """
        try:
            output = (int(s1, 16) * 3600) + (int(s2, 16))
        except:
            output = self.missing

        return output

    def BP(self, s1):
        r"""
        Convert Barometric Pressure
      """
        try:
            output = (int(s1, 16) / 0.85) + 800
            if (output > 1060) or (output < 940):
                output = self.missing
        except:
            output = self.missing

        return output

    def AT(self, s1, s2):
        r"""
        Convert Air Temperature
      """
        try:
            output = (int((s1 + s2), 16) / 10.0) - 50.0
            if (output > 40) or (output < -20):
                output = self.missing
        except:
            output = self.missing

        return output

    def BV(self, s1):
        r"""
        Convert Battery Voltage
      """
        try:
            output = int(s1, 16)
            if (output > 40) or (output < 0):
                output = self.missing
        except:
            output = self.missing

        return output

    def RH(self, s1):
        r"""
        Convert Relative Humidity
      """
        try:
            output = int(s1, 16)
            if (output > 100) or (output <= 0):
                output = self.missing
        except:
            output = self.missing

        return output

    def WS(self, s1, s2):
        r"""
        Convert Wind Speed
      """
        try:
            output = int(s1 + s2, 16) / 10.0
            if (output > 50) or (output < 0):
                output = self.missing
        except:
            output = self.missing

        return output

    def WD(self, s1, magnetic_dec=0):
        r"""
        Convert Wind Direction (+magnetic declination correction)
      """
        try:
            output = (int(s1, 16) / 0.7083) + magnetic_dec
        except:
            output = self.missing

        return output

    def SR(self, s1):
        r"""
        Convert Solar Radiation
      """
        try:
            output = int(s1, 16) / 0.18214
            if (output > 1400) or (output < 0):
                output = self.missing
        except:
            output = self.missing

        return output

    def AZ(self, s1):
        r"""
        Convert Azimuth angle
      """
        try:
            output = int(s1, 16) / 0.7083
        except:
            output = self.missing

        return output


def pandas2netcdf(df=None, ofile="data.nc",isxa=True):

    if df.empty:
        return
    else:
        if isxa:
            EPIC_VARS_yaml = ConfigParserLocal.get_config(
                "config_files/drifters.yaml", "yaml"
            )

            df = df.reset_index()
            df.index = df.reset_index().index.rename('record_number')
            xdf = df.rename(columns={'year_doy_hhmm':'time'}).to_xarray()           

            #rename variables and add attributes
            drop_missing = True

            for var in EPIC_VARS_yaml.keys():
                try:
                    xdf[var].attrs = EPIC_VARS_yaml[var]
                except (ValueError, KeyError):
                    if drop_missing:
                        try:
                            xdf = xdf.drop_vars(var)
                        except (ValueError, KeyError):
                            pass
                    else:
                        pass
            
            #xarray casting issue?
            for var in xdf.variables:
                if xdf[var].dtype == 'float64':
                    xdf[var] = xdf[var].astype('float32')

            #global attributes
            xdf.attrs["CREATION_DATE"] = datetime.now(timezone.utc).strftime("%B %d, %Y %H:%M UTC")
            xdf.attrs["INST_TYPE"] = ''
            xdf.attrs["DATA_CMNT"] = ''
            xdf.attrs["NC_FILE_GENERATOR"] = 'Generated with Xarray' 
            xdf.attrs["WATER_DEPTH"] = ''
            xdf.attrs["MOORING"] = ''
            xdf.attrs["WATER_MASS"] = ''
            xdf.attrs["EXPERIMENT"] = ''
            xdf.attrs["PROJECT"] = ''
            xdf.attrs["SERIAL_NUMBER"] = ''
            xdf.attrs['History']="File Created from ARGSOS Drifter Data."

            xdf.to_netcdf(ofile,
                        format='NETCDF4',
                        encoding={'time':{'units':'days since 1900-01-01'}})
        else:
            df["time"] = [
                date2num(x[1], "hours since 1900-01-01T00:00:00Z")
                for x in enumerate(df.index)
            ]

            EPIC_VARS_dict = ConfigParserLocal.get_config(
                "config_files/drifters.yaml", "yaml"
            )

            # create new netcdf file
            ncinstance = EcF_write.NetCDF_Create_Profile_Ragged1D(savefile=ofile)
            ncinstance.file_create()
            ncinstance.sbeglobal_atts(
                raw_data_file="", History="File Created from ARGSOS Drifter Data."
            )
            ncinstance.dimension_init(recnum_len=len(df))
            ncinstance.variable_init(EPIC_VARS_dict)
            ncinstance.add_coord_data(recnum=range(1, len(df) + 1))
            ncinstance.add_data(
                EPIC_VARS_dict, data_dic=df, missing_values=np.nan, pandas=True
            )
            ncinstance.close()


"""--------------------- Main ----------------------------------------------"""

# parse incoming command line options
parser = argparse.ArgumentParser(
    description="Read Argos formatted drifterid.yyyy files"
)
parser.add_argument(
    "sourcefile",
    metavar="sourcefile",
    type=str,
    help="path to yearly drifter files parsed by ID",
)
parser.add_argument(
    "version",
    metavar="version",
    type=str,
    help="beacon,buoy,buoy_3hr,v1-(pre-2017),v2-(post-2017)",
)
parser.add_argument("-csv", "--csv", type=str, help="output as csv - full path")
parser.add_argument(
    "-geojson", "--geojson", type=str, help="output as geojson - full path"
)
parser.add_argument("-nc", "--netcdf", type=str, help="output as netcdf - full path")
parser.add_argument("-config", "--config", type=str, help="read local config file")

parser.add_argument(
    "-interpolate",
    "--interpolate",
    action="store_true",
    help="interpolate data to hourly",
)
parser.add_argument(
    "-keepna_loc",
    "--keepna_loc",
    action="store_true",
    help="keep data with missing location fixes",
)

args = parser.parse_args()


if args.version in ["beacon"]:

    atseadata = ARGOS_SERVICE_Beacon()

    df = atseadata.get_data(args.sourcefile)

    df["location_quality"] = df["s2"]

    df.drop_duplicates(
        subset=["year_doy_hhmm", "latitude", "longitude"], keep="last", inplace=True
    )
    df.drop(['year_doy_hhmm',"s1", "s2", "s3", "s4"], axis=1, inplace=True)

elif args.version in ["v1", "V1", "version1", "v1-metocean"]:
    atseadata = ARGOS_SERVICE_Drifter()

    df = atseadata.get_data(args.sourcefile)

    df["strain"] = df.apply(
        lambda row: atseadata.strain_argos(row["s1"], manufacter="MetOcean"), axis=1
    )
    df["voltage"] = df.apply(lambda row: atseadata.voltage_argos(row["s2"]), axis=1)
    df["sst"] = df.apply(lambda row: atseadata.sst_argos(row["s2"], row["s3"]), axis=1)
    df["checksum"] = df.apply(
        lambda row: atseadata.checksum_argos(
            row["s1"], row["s2"], row["s3"], row["s4"]
        ),
        axis=1,
    )
    df["location_quality"] = df["s8"]
    df["location_quality"] = pd.to_numeric(df["location_quality"], errors="coerce")

    df.drop(df.index[~df["checksum"]], inplace=True)
    df.drop_duplicates(subset="year_doy_hhmm", keep="last", inplace=True)

    df.drop(["checksum","year_doy_hhmm","s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"], axis=1, inplace=True)

elif args.version in ["v2", "V2", "version2", "v2-vendor(2017)"]:

    atseadata = ARGOS_SERVICE_Drifter()

    df = atseadata.get_data(args.sourcefile)

    df["strain"] = df.apply(lambda row: atseadata.strain_argos(row["s1"]), axis=1)
    df["voltage"] = df.apply(lambda row: atseadata.voltage_argos(row["s2"]), axis=1)
    df["sst"] = df.apply(lambda row: atseadata.sst_argos(row["s2"], row["s3"]), axis=1)
    df["checksum"] = df.apply(
        lambda row: atseadata.checksum_argos(
            row["s1"], row["s2"], row["s3"], row["s4"]
        ),
        axis=1,
    )
    df["location_quality"] = df["s8"]
    df["location_quality"] = pd.to_numeric(df["location_quality"], errors="coerce")

    try:
        df.drop(df.index[~df["checksum"]], inplace=True)
    except TypeError:
        pass

    df.drop_duplicates(
        subset=["year_doy_hhmm", "latitude", "longitude"], keep="last", inplace=True
    )
    df.drop(["checksum","year_doy_hhmm","s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"], axis=1, inplace=True)

elif args.version in ["buoy", "met", "sfc_package"]:

    atseadata = ARGOS_SERVICE_Buoy(missing=None)

    df = atseadata.get_data(args.sourcefile)

    df["seconds"] = df.apply(lambda row: atseadata.time(row["s1"], row["s2"]), axis=1)
    df["sampletime"] = [
        index.floor("D") + datetime.timedelta(seconds=row["seconds"])
        for index, row in df.iterrows()
    ]
    df["BP"] = df.apply(lambda row: atseadata.BP(row["s3"]), axis=1)
    df["AT"] = df.apply(lambda row: atseadata.AT(row["s4"], row["s5"]), axis=1)
    df["BV"] = df.apply(lambda row: atseadata.BV(row["s6"]), axis=1)
    df["RH"] = df.apply(lambda row: atseadata.RH(row["s7"]), axis=1)
    df["WS"] = df.apply(lambda row: atseadata.WS(row["s8"], row["s9"]), axis=1)
    df["WD"] = df.apply(lambda row: atseadata.WD(row["s10"]), axis=1)
    df["SR"] = df.apply(lambda row: atseadata.SR(row["s11"]), axis=1)
    df["AZ"] = df.apply(lambda row: atseadata.AZ(row["s12"]), axis=1)

    # Uses sample time instead of transmit/location time
    df.drop((df[df["seconds"] > 86400]).index, inplace=True)
    df.set_index(df["sampletime"], inplace=True)
    # df.drop_duplicates(subset=['year_doy_hhmm','latitude','longitude'],keep='last',inplace=True)

    if not args.keepna_loc:
        df.dropna(subset=["latitude", "longitude"], how="any", inplace=True)
    df.drop(
        [
            "sampletime",
            "seconds",
            "s1",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
            "s9",
            "s10",
            "s11",
            "s12",
        ],
        axis=1,
        inplace=True,
    )

elif args.version in ["buoy_3hr"]:

    atseadata = ARGOS_SERVICE_Buoy(missing=None)

    df0 = atseadata.get_data(args.sourcefile, "current")

    # current sample
    df0["seconds"] = df0.apply(lambda row: atseadata.time(row["s1"], row["s2"]), axis=1)
    df0["sampletime"] = [
        index.floor("D") + datetime.timedelta(seconds=row["seconds"])
        for index, row in df0.iterrows()
    ]
    df0["BP"] = df0.apply(lambda row: atseadata.BP(row["s3"]), axis=1)
    df0["AT"] = df0.apply(lambda row: atseadata.AT(row["s4"], row["s5"]), axis=1)
    df0["BV"] = df0.apply(lambda row: atseadata.BV(row["s6"]), axis=1)
    df0["RH"] = df0.apply(lambda row: atseadata.RH(row["s7"]), axis=1)
    df0["WS"] = df0.apply(lambda row: atseadata.WS(row["s8"], row["s9"]), axis=1)
    df0["WD"] = df0.apply(lambda row: atseadata.WD(row["s10"]), axis=1)
    df0["SR"] = df0.apply(lambda row: atseadata.SR(row["s11"]), axis=1)
    df0["AZ"] = df0.apply(lambda row: atseadata.AZ(row["s12"]), axis=1)

    # Uses sample time instead of transmit/location time
    df0.drop((df0[df0["seconds"] > 86400]).index, inplace=True)
    df0.set_index(df0["sampletime"], inplace=True)

    if not args.keepna_loc:
        df0.dropna(subset=["latitude", "longitude"], how="any", inplace=True)

    # sample -1hr
    df1 = atseadata.get_data(args.sourcefile, "1hr")

    df1["seconds"] = df1.apply(lambda row: atseadata.time(row["s1"], row["s2"]), axis=1)
    df1["sampletime"] = [
        index.floor("D") + datetime.timedelta(seconds=(row["seconds"] - 3600))
        for index, row in df1.iterrows()
    ]
    df1["BP"] = df1.apply(lambda row: atseadata.BP(row["s3"]), axis=1)
    df1["AT"] = df1.apply(lambda row: atseadata.AT(row["s4"], row["s5"]), axis=1)
    df1["BV"] = df1.apply(lambda row: atseadata.BV(row["s6"]), axis=1)
    df1["RH"] = df1.apply(lambda row: atseadata.RH(row["s7"]), axis=1)
    df1["WS"] = df1.apply(lambda row: atseadata.WS(row["s8"], row["s9"]), axis=1)
    df1["WD"] = df1.apply(lambda row: atseadata.WD(row["s10"]), axis=1)
    df1["SR"] = df1.apply(lambda row: atseadata.SR(row["s11"]), axis=1)
    df1["AZ"] = df1.apply(lambda row: atseadata.AZ(row["s12"]), axis=1)

    # Uses sample time instead of transmit/location time
    df1.drop((df1[df1["seconds"] > 86400]).index, inplace=True)
    df1.set_index(df1["sampletime"], inplace=True)

    if not args.keepna_loc:
        df1.dropna(subset=["latitude", "longitude"], how="any", inplace=True)

    # sample -2hr
    df2 = atseadata.get_data(args.sourcefile, "2hr")

    df2["seconds"] = df2.apply(lambda row: atseadata.time(row["s1"], row["s2"]), axis=1)
    df2["sampletime"] = [
        index.floor("D") + datetime.timedelta(seconds=(row["seconds"] - 7200))
        for index, row in df2.iterrows()
    ]
    df2["BP"] = df2.apply(lambda row: atseadata.BP(row["s3"]), axis=1)
    df2["AT"] = df2.apply(lambda row: atseadata.AT(row["s4"], row["s5"]), axis=1)
    df2["BV"] = df2.apply(lambda row: atseadata.BV(row["s6"]), axis=1)
    df2["RH"] = df2.apply(lambda row: atseadata.RH(row["s7"]), axis=1)
    df2["WS"] = df2.apply(lambda row: atseadata.WS(row["s8"], row["s9"]), axis=1)
    df2["WD"] = df2.apply(lambda row: atseadata.WD(row["s10"]), axis=1)
    df2["SR"] = df2.apply(lambda row: atseadata.SR(row["s11"]), axis=1)
    df2["AZ"] = df2.apply(lambda row: atseadata.AZ(row["s12"]), axis=1)

    # Uses sample time instead of transmit/location time
    df2.drop((df2[df2["seconds"] > 86400]).index, inplace=True)
    df2.set_index(df2["sampletime"], inplace=True)

    if not args.keepna_loc:
        df2.dropna(subset=["latitude", "longitude"], how="any", inplace=True)

    df0.drop(
        [
            "sampletime",
            "seconds",
            "s1",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
            "s9",
            "s10",
            "s11",
            "s12",
        ],
        axis=1,
        inplace=True,
    )
    df1.drop(
        [
            "sampletime",
            "seconds",
            "s1",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
            "s9",
            "s10",
            "s11",
            "s12",
        ],
        axis=1,
        inplace=True,
    )
    df2.drop(
        [
            "sampletime",
            "seconds",
            "s1",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
            "s9",
            "s10",
            "s11",
            "s12",
        ],
        axis=1,
        inplace=True,
    )

    # merge the three dataframes
    df = pd.concat([df0, df1, df2])

else:
    print("No recognized argos-pmel version")
    sys.exit()

if args.config:
    config_settings = ConfigParserLocal.get_config(args.config, "yaml")
    print(
        "Constraining data to {start}-{end}".format(
            start=config_settings["Mooring"]["StartDate"],
            end=config_settings["Mooring"]["EndDate"],
        )
    )
    df = df.loc[
        config_settings["Mooring"]["StartDate"] : config_settings["Mooring"]["EndDate"]
    ]

if args.interpolate:
    # hourly binned with linear interpolation to fill gaps
    df = (
        df.resample("1H", label="right", closed="right")
        .mean()
        .interpolate(method="linear")
    )

"""------------------------ output options----------------------"""
if args.csv and (not args.version in ["beacon","buoy_3hr", "buoy", "met", "sfc_package"]):
    df["longitude"] = df.longitude.apply(lambda x: "%.3f" % x)
    df["latitude"] = df.latitude.apply(lambda x: "%.3f" % x)
    df["sst"] = df.sst.apply(lambda x: "%.2f" % x)
    df["strain"] = df.strain.apply(lambda x: "%.1f" % x)
    df["voltage"] = df.voltage.apply(lambda x: "%.1f" % x)
    df.to_csv(args.csv)
else:
    df.to_csv(args.csv)

if args.geojson:
    """
        GeoJSON format example:
        {
          "type": "FeatureCollection",
          "features": [
            {
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [102.0, 0.6]
              },
              "properties": {
                "prop0": "value0"
              }
            },
            {
              "type": "Feature",
              "geometry": {
                "type": "LineString",
                "coordinates": [
                  [102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]
                ]
              },
              "properties": {
                "prop1": 0.0,
                "prop0": "value0"
              }
            },
            {
              "type": "Feature",
              "geometry": {
                "type": "Polygon",
                "coordinates": [
                  [
                    [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
                    [100.0, 0.0]
                  ]
                ]
              },
              "properties": {
                "prop1": {
                  "this": "that"
                },
                "prop0": "value0"
              }
            }
          ]
        }"""

    print("Generating .geojson as single points per cast")
    geojson_header = "{\n" '"type": "FeatureCollection",\n' '"features": [\n'
    geojson_Features = ""

    count = 0
    for ind, row in df.iterrows():

        geojson_Features = geojson_Features + (
            "{{\n"
            '"type": "Feature",\n'
            '"id": {ArgosID},\n'
            '"geometry": {{\n'
            '"type": "Point",\n'
            '"coordinates": '
            "[{lon},{lat}]"
            "}},\n"
            '"properties": {{\n'
            '"datetime": "{timeprint}"'
            "}}\n"
        ).format(
            lat=row["latitude"],
            lon=(-1 * row["longitude"]),
            ArgosID=row["argosid"],
            timeprint=row["year_doy_hhmm"],
        )

        if count != len(df) - 1:
            geojson_Features = geojson_Features + "}\n, "
            count += 1

    geojson_tail = "}\n" "]\n" "}\n"

    fid = open(args.geojson, "w")
    fid.write(geojson_header + geojson_Features + geojson_tail)
    fid.close()


if args.netcdf:
    pandas2netcdf(df=df, ofile=args.netcdf)

