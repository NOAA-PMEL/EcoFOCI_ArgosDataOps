#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 16:00:10 2019

@author: strausz
"""

import pandas as pd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
#import cartopy.feature as cfeature
import cmocean
#for calculating distance
from haversine import haversine
import argparse
from datetime import datetime
import numpy as np
import re
from erddapy import ERDDAP
import mysql.connector
import cartopy.feature as cfeature



parser = argparse.ArgumentParser(description='Plot drifter track on map')
parser.add_argument('-if','--infile', nargs=1, type=str, 
                    help='full path to input file')
parser.add_argument('-p', '--plot', nargs='+', type=str, 
                    help="make plot of 'sst', 'strain', or 'speed', alternately zoom in with 'zoom' and place occasional date with 'date', add origin beginning with 'origin'")
parser.add_argument('-f', '--file', nargs='?', type=str,
                    help="output csv file of data, use 'final' for archival format")
parser.add_argument('-i', '--ice', action="store_true",
                    help="add ice concentration as last field and output file, requires speed and hour to be selected")
parser.add_argument('-ph', '--phyllis', action="store_true",
                    help="output format for phyllis friendly processing")
parser.add_argument('-e', '--erddap', nargs='+',
                    help="get directly from akutan erddap server, requires argos id followed by desired years")
parser.add_argument('-H', '--hour', action="store_true",
                    help="resample all data to even hour and interpolate")
parser.add_argument('-s', '--speed', action="store_true",
                    help="add speed column")
parser.add_argument('-V', '--vecdis', action="store_true",
                    help="import a vecdis file as input")
parser.add_argument('-l', '--legacy', nargs='?',
                    help="file has legacy format from ecofoci website, if file contains ice concentraion, add 'i'")
parser.add_argument('-c', '--cut', nargs='*',
                    type=lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S"),
                    help="date span in format '2019-01-01T00:00:00 2019-01-01T00:00:01' also works with only beginning date and if no date is given it will try using the drifter database")
parser.add_argument('-de', '--despike', action="store_true",
                     help="Do some simple despiking of sst")
args=parser.parse_args()


#the following is info needed for adding the ice concentration 
latfile='/home/makushin/strausz/ecofoci_github/EcoFOCI_ssmi_ice/psn25lats_v3.dat'
lonfile='/home/makushin/strausz/ecofoci_github/EcoFOCI_ssmi_ice/psn25lons_v3.dat'
#locations of ice files
bootstrap = '/home/akutan/strausz/ssmi_ice/data/bootstrap/'
nrt = '/home/akutan/strausz/ssmi_ice/data/nrt/'
#latest available bootstrap year will need to be changed as new data comes in
boot_year = 2018

if args.infile:
    filename=args.infile[0]
else:
    filename=''
def decode_datafile(filename):
    #determine if it's nrt or bootstrap from filename prefix
    #note that we remove path first if it exists
    prefix = filename.split('/')[-1:][0][:2] 
    icefile = open(filename, 'rb')
    
    if prefix == 'nt':
        #remove the header
        icefile.seek(300)
        ice = np.fromfile(icefile,dtype=np.uint8)
        ice[ice >= 253] = 0
        ice = ice/2.5
    elif prefix == 'bt':
        ice = np.fromfile(icefile,dtype=np.uint16)
        ice = ice/10.
        ice[ice == 110] = 0 #110 is land
        ice[ice == 120] = 100 #120 is polar hole
    else: 
        ice=np.nan
    
    icefile.close()
    
    return ice;

def decode_latlon(filename):
    latlon_file = open(filename, 'rb')
    output = np.fromfile(latlon_file,dtype='<i4')
    output = output/100000.0
    #output = int(output * 1000)/1000 #sets decimal place at 3 without rounding
    latlon_file.close()
    return output;

def get_ice(data, df_ice):
    #
    df_ice['dist'] = df_ice.apply(lambda x: haversine((data.latitude, data.longitude), (x.latitude, x.longitude)), axis=1)
    nearest_ice = df_ice.loc[df_ice.dist.idxmin()].ice_conc
    return nearest_ice
    
def lon_360(lon):
    if lon < 0:
        return 360 + lon
    else:
        return lon

def get_extents(df, zoom=False):
    #first convert all longitudes to 0-360
    df['lon2'] = df.longitude.apply(lambda x: x + 360 if x < 0 else x)
    if zoom:    
        nlat = df.latitude.max() + .5
        slat = df.latitude.min() - .5
        wlon = df.lon2.min() - .5
        elon = df.lon2.max() + .5
    else:
        nlat = df.latitude.max() + 3
        slat = df.latitude.min() - 3
        wlon = df.lon2.min() - 5
        elon = df.lon2.max() + 5
    extents = [wlon, elon, slat, nlat]
    return extents

def plot_variable(dfin, var, filename, zoom=False):
    proj = ccrs.LambertConformal(central_longitude=-165, central_latitude=60)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection=proj)
    #ax = plt.axes(projection=proj)
    ax.add_feature(cfeature.LAND.with_scale('50m'))
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
    if var == 'speed' :
        vmin, vmax, cmap = 0, 120, cmocean.cm.speed
    elif var == 'sst':
        vmin, vmax, cmap = -2, 20, cmocean.cm.thermal
    elif var == 'strain':
        vmin, vmax, cmap = 0, 20, cmocean.cm.haline
    elif var == 'ice_concentration':
        vmin, vmax, cmap = 0, 100, cmocean.cm.ice
    plotted = ax.scatter(dfin['longitude'], dfin['latitude'], s=10, c=dfin[var], transform=ccrs.PlateCarree(), 
               cmap=cmap, vmin=vmin, vmax=vmax )
    plt.colorbar(plotted)
    #ax.plot(dfin['longitude'], dfin['latitude'], transform=ccrs.PlateCarree())
    
    if args.legacy:
        trajectory_id=re.search(r'(\d{5,})', filename).group(0)
        trajectory_id=trajectory_id + '_sigrid_processing'
    else:
        trajectory_id = str(dfin.trajectory_id[0])
    
    if zoom:
        ax.set_extent(get_extents(dfin, zoom))
        filename = trajectory_id + "_" + var + "_zoomed.png"
        title = trajectory_id + " Zoomed " + var
        
    else:
        ax.set_extent(get_extents(dfin))
        filename = trajectory_id + "_" + var + ".png"
        title = trajectory_id + " " + var
        
    
    
    ax.set_title(title)
    
    return fig, ax, filename

def trim_data(df, delta_t):
    
    if len(delta_t) == 0:
        try:
            print("Trying to set start time from database .....")
            drifter_db = mysql.connector.connect(user='viewer', host='127.0.0.1', 
                                         database='ecofoci_drifters')
            cursor = drifter_db.cursor()
            argos_id = str(df.trajectory_id[0])
            query_string = "select releasedate from drifter_ids where argosnumber=" + argos_id        
            #was originally like this, not sure why I had the "isactive" in there 
            #query_string = "select releasedate from drifter_ids where argosnumber=" + argos_id + " and isactive='Y'"
            #print(query_string)
            query = (query_string)
            cursor.execute(query)
    
            results = cursor.fetchone()
            
            start = results[0].strftime('%Y-%m-%d %H:%M:%S')
            drifter_db.close()
            print("Drifter",argos_id,"start time is",start)
            #return df[start:]
            return df.loc[start:]
        except:
             print("Database not available!")
    elif len(delta_t) == 1:
        start = delta_t[0].strftime('%Y-%m-%d %H:%M:%S')
        return df.loc[start:]
    elif len(delta_t) == 2:
        start = delta_t[0].strftime('%Y-%m-%d %H:%M:%S')
        end = delta_t[1].strftime('%Y-%m-%d %H:%M:%S')
        return df.loc[start:end]
    else:
        quit("Too many cut arguments!")
    

def speed(df):
       df['time'] = df.index
       df['next_lat'] = df.latitude.shift(-1)
       df['next_lon'] = df.longitude.shift(-1)
       #then calculate distance between points with the haversine function
       df['dist'] = df.apply(lambda x: haversine((x.latitude, x.longitude), (x.next_lat, x.next_lon)), axis=1)
       df['dist_U'] = df.apply(lambda x: haversine((x.latitude, x.longitude), (x.latitude, x.next_lon)), axis=1)
       df['dist_V'] = df.apply(lambda x: haversine((x.latitude, x.longitude), (x.next_lat, x.longitude)), axis=1)
       
       #next shift up the 'dist' column
       df.dist.shift()
       #now calculate the time difference
       
       df['time2'] = df.time.shift(-1)
       #make the time_delta
       df['time_delta'] = df.time2 - df.time
       #now make new column of seconds
       df['seconds'] = df.time_delta.dt.total_seconds()
       #now calculate speed in cm/s
       df['speed'] = df.dist * 100000 / df.seconds
       df['U'] = df.dist_U * 100000 / df.seconds
       df['V'] = df.dist_V * 100000 / df.seconds
       df['speed_check'] = (df.U**2 + df.V**2)**(1/2)
       #df['trajectory_id'] = df.trajectory_id.astype(int)
       #now calculate bearing btw the two points using formula found on 
       #http://www.movable-type.co.uk/scripts/latlong.html
       df['bearing'] = np.degrees(np.arctan2(np.sin(np.radians(df.next_lon - df.longitude) 
                                         * np.cos(np.radians(df.next_lat))),
                                  np.cos(np.radians(df.latitude))*np.sin(np.radians(df.next_lat))
                                  -np.sin(np.radians(df.latitude)) * np.cos(np.radians(df.next_lat))
                                  * np.cos(np.radians(df.next_lon - df.longitude))))
       df['bearing'] = (df.bearing + 360) % 360
       return df
def hour(df):
    df_hour=df.resample('H').mean()
    
    #use linear interpolation to fill in gaps
    df_hour.interpolate(inplace=True, limit=12)
    return df_hour
    
def ice(df):
    df['lon_360'] = df.apply(lambda x: lon_360(x.longitude), axis=1)
    df['datetime'] = df.index
    df.dropna(inplace=True)
    df['trajectory_id']=df_hour.trajectory_id.astype(int)
    # df_hour['latitude']=df_hour.latitude.round(decimals=3)
    # df_hour['longitude']=df_hour.longitude.round(decimals=3)
    # df_hour['voltage']=df_hour.voltage.round(decimals=2)
    # df_hour['sst']=df_hour.sst.round(decimals=2)
    # df_hour['strain']=df_hour.strain.round(decimals=2)
    #now group by doy
    #add blank ice column
    df['ice_concentration'] = ''
    ice_conc = []
    groups = df.groupby(df.index.dayofyear)
    for name, group in df.groupby(df.index.dayofyear):
        #print(name)
        #print(group.latitude)
        date = group.iloc[0].datetime.strftime("%Y%m%d")
        if group.iloc[0].datetime.year <= boot_year:
            ice_file = bootstrap + str(group.iloc[0].datetime.year) + "/" + "bt_" + date + "_f17_v3.1_n.bin"
        else:
            ice_file = nrt + "nt_" + date + "_f18_nrt_n.bin"
        print("opening file: " + ice_file)
        wlon = group.lon_360.min() - .3
        elon = group.lon_360.max() + .3
        nlat = group.latitude.max() + .3
        slat = group.latitude.min() - .3
        data_ice={'latitude':decode_latlon(latfile), 'longitude':decode_latlon(lonfile),
          'ice_conc':decode_datafile(ice_file)}
        df_ice=pd.DataFrame(data_ice)
        df_ice.dropna(inplace=True)
    
        df_ice['lon_360'] = df_ice.apply(lambda x: lon_360(x.longitude), axis=1)
        df_ice_chopped = df_ice[(df_ice.latitude < nlat) & (df_ice.latitude > slat) & (df_ice.lon_360 > wlon) & (df_ice.lon_360 < elon)]
        ice_conc = ice_conc + group.apply(lambda x: get_ice(x, df_ice_chopped), axis=1).to_list()
                
        
        #print("the ice concentration is: "+ice_concentration)
        #df_ice_chopped['dist'] = df_ice_chopped.apply(lambda x: haversine((data.latitude, data.longitude), (x.latitude, x.longitude)), axis=1)
    df['ice_concentration'] = ice_conc
    # df=df.drop(['lon_360', 'datetime'], axis=1)
    # df_out = df_hour[['trajectory_id','latitude','longitude','sst','strain','voltage','speed','ice_concentration']]
    # df_out = df_out.round({'latitude':3, 'longitude':3,'sst':2,'strain':1,'voltage':1,'speed':1, 'ice_concentration':1})
    # outfile = str(df_hour.trajectory_id[0]) + "_with_ice.csv"
    # df_out.to_csv(outfile)
    return df

def despike(df):
    #create empty df
    
    df['sst_pass1'] = df.sst
    df['sst_pass2'] = df.sst
    #group by day first
    #grouped = df.groupby(df.index.date)
    #group by given number of rows
    #first drop obvious spikes
    df_orig = df
    numrows = 50
    pass1_array = np.arange(len(df)) // 50
    pass2_array = pass1_array[25:]
    last_group = len(df) // 50
    end_array = np.arange(25)*0+last_group
    pass2_array = np.append(pass2_array, end_array)
    pd.set_option('display.max.row', None)
    def remove_spikes(df, array, var):
        #first remove obvious spikes
        df.loc[(df[var] > 18) | (df[var] < -2.6), var] = np.nan
        df_ds = pd.DataFrame()
        grouped = df.groupby(array)
        
        argos_id = str(df.trajectory_id[0])
        
        f = open(argos_id + "_despiked_" + var + ".log", 'w')
        for name, group in grouped:
            f.write("Standard deviation for SST: ")
            f.write(str(round(group[var].std(),3))+"\n")
            f.write("Mean of SST: ") 
            f.write(str(round(group[var].mean(),3))+"\n")
            
            #try using loc to set to nan
            #ie df.loc[df.sst>10, 'sst']=np.nan
            upper = group[var].mean() + group[var].std()*2
            lower = group[var].mean() - group[var].std()*2
            f.write("Removed any values > " + str(round(upper, 3)) + " or < "
                    + str(round(lower, 3)) + "\n")
            group.loc[(group[var] > upper) | (group[var] < lower), var] = np.nan
            #print(group[['sst', 'sst_orig']])
            f.write("Number of spikes removed: ")
            f.write(str(group[var].isna().sum())+"\n")
            f.write(group[['sst', var]].to_string())
            f.write("\n----------------------------------------------------\n")
            #despiked = group[(group.sst < group.sst.mean() + group.sst.std()*3) & (group.sst > group.sst.mean() - group.sst.std()*3) ]
            df_ds = pd.concat([df_ds, group])
            #df_ds = pd.concat(group[(group.sst < group.sst.mean() + group.sst.std()*2) & (group.sst > group.sst.mean() - group.sst.std()*2) ])   
        pd.set_option('display.max.row', 10)
        f.write("Total Number of spikes removed: ")
        f.write(str(df_ds.sst.isna().sum()))
        f.close()
        return df_ds
    df_ds = remove_spikes(df, pass1_array, 'sst_pass1')
    df_ds = remove_spikes(df_ds, pass2_array, 'sst_pass2')
    df_ds['sst_combined'] = df_ds['sst_pass1'].combine_first(df_ds["sst_pass2"])
    #reorder columns so the print nicely
    df_ds = df_ds[['trajectory_id', 'latitude', 'longitude', 'strain', 'voltage', 'sst', 'sst_pass1', 'sst_pass2', 'sst_combined']]
    argos_id = str(df.trajectory_id[0])
    f = open(argos_id + "_despiked_full_.log", 'w')
    f.write(df_ds.to_string())
    f.close()
    pd.set_option('display.max.row', 10)
    return df_ds

if args.erddap:
    drifter_years = args.erddap[1:]
    argos_id = args.erddap[0]
    e = ERDDAP( 
    server = 'http://ecofoci-field.pmel.noaa.gov:8082/erddap',
    protocol = 'tabledap',)

    e.response = 'csv'
    #e.dataset_id = drifter_year + '_Argos_Drifters_NRT'
    #use this until we can get location quality back into older years
    #currently it is only in erddap for 2020 and newer
    #if int(drifter_years[0]) >= 2020:
    e.variables = ['trajectory_id','strain', 'voltage', 'time', 'latitude', 'sst',
                       'longitude', 'location_quality']
    #else:
    #    e.variables = ['trajectory_id','strain', 'voltage', 'time', 'latitude', 'sst',
    #                   'longitude']

    e.constraints = {'trajectory_id=':argos_id}
    df_years={}
    for year in drifter_years:
        e.dataset_id = year + '_Argos_Drifters_NRT'        
        df = e.to_pandas(index_col='time (UTC)',
                parse_dates=True,
                skiprows=(1,)  # units information can be dropped.
                )
        df.columns = [x[1].split()[0] for x in enumerate(df.columns)]
        df_years[year]=df
    df = pd.concat(df_years.values())
    #get rid of timezone info
    df = df.tz_localize(None)
    # # names = ['trajectory_id','strain','voltage','datetime','latitude','sst','longitude']
    # # df=pd.read_csv(filename, skiprows=1, header=0, names=names, parse_dates=[3])
    # # #df['longitude'] = df.longitude - 360
    # df['datetime'] = df.datetime.dt.tz_localize(None) #to remove timezone info
    # df.set_index(['datetime'], inplace=True)
    #df['longitude'] = df.longitude.apply(lambda x: x+360 if x<0 else x)
elif args.legacy:
    if args.legacy == 'i':
        names = ['latitude', 'longitude', 'year', 'day', 'time', 'strain', 
             'voltage', 'sst', 'quality', 'ice']
    else:
        names = ['latitude', 'longitude', 'year', 'day', 'time', 'strain', 
             'voltage', 'sst', 'quality']
    dtypes = {'year':str, 'day':str, 'time':str}
    dateparser = lambda x: pd.datetime.strptime(x, "%Y %j %H%M")
    df=pd.read_csv(filename, sep=r'\s+', skiprows=28, header=0, names=names,
                   dtype=dtypes, parse_dates={'datetime':[2,3,4]},
                   date_parser=dateparser)
    #to make W longitude negative and E positive
    df['longitude'] = df.longitude.apply(lambda x: x*-1+360 if x >= 180 else x * -1)
    df.set_index(['datetime'], inplace=True)
    trajectory_id=re.search(r'(\d{5,})', filename).group(0)
    df['trajectory_id']=trajectory_id

elif args.vecdis:
    names = ['year','day','time','latitude','longitude', 'speed', 'direction', 'U', 'V']
    dtypes = {'year':str, 'day':str, 'time':str}
    dateparser = lambda x: pd.datetime.strptime(x, "%Y%j%H%M")
    df=pd.read_csv(filename, sep=r'\s+', skiprows=2, header=0, names=names,
                   dtype=dtypes)
    #to make W longitude negative and E positive
    df['time'] = df.time.str.zfill(4)
    df['datetime'] = pd.to_datetime((df.year+df.day+df.time), format="%Y%j%H%M")
    df['longitude'] = df.longitude.apply(lambda x: x*-1+360 if x >= 180 else x * -1)
    df.set_index(['datetime'], inplace=True)
    trajectory_id=re.search(r'(\d{5,})', filename).group(0)
    df['trajectory_id']=trajectory_id
    df['speed2'] =(df.U**2 + df.V**2)**(1/2)
    #calculate overall speed
    
else:
    df = pd.read_csv(filename)
    
    df['datetime'] = pd.to_datetime(df['year_doy_hhmm'], format='%Y-%m-%d %H:%M:%S')
    df['datetime'] = df.datetime.dt.tz_localize(None) #to remove timezone info
    
    df.set_index(['datetime'], inplace=True)
    df.drop(columns=['year_doy_hhmm','year_doy_hhmm.1'], inplace=True)
    df['longitude'] = df.longitude * -1

if args.cut or args.cut == []:
    df = trim_data(df, args.cut)

if args.despike:
    df = despike(df)

if args.hour: #resample data to on an even hour
    df_hour = hour(df) 
    
if args.ice:
    #requires df_hour
    df_ice = ice(df_hour)

if args.speed: #now calculate distance for drifter speed calculation
    #requires df_hour
    df_speed = speed(df_hour)
#now can do plotting stuff if selected


if args.plot:
    if 'zoom' in args.plot:
        fig, ax, plot_file = plot_variable(df, args.plot[0], filename, 'zoom')
    else:
        fig, ax, plot_file = plot_variable(df, args.plot[0], filename)
#    ax.scatter(df_hour['longitude'], df_hour['latitude'], s=10, c=df_hour.speed, transform=ccrs.PlateCarree(), 
#               cmap=cmocean.cm.speed, vmin=0, vmax=120 )
    if 'date' in args.plot:
        df_week = df.resample('W').last()
        #df_week = pd.concat([df_week, df.tail(1)])
        df_week['date'] = df_week.index.strftime("%m/%d")
        df_week.apply(lambda x: ax.text(x.longitude,x.latitude,'  '+x.date, transform=ccrs.PlateCarree()), axis=1)
        df_week.apply(lambda x: ax.plot(x.longitude,x.latitude, 'r^', transform=ccrs.PlateCarree()), axis=1)
    
    if "origin" in args.plot:
        ax.plot(df.iloc[0:1].longitude, df.iloc[0:1].latitude, 'rX', transform=ccrs.PlateCarree())      		
    fig.savefig(plot_file)

if args.file:
    if args.file=='final':
        if args.ice:
            df_out = df_speed[['trajectory_id','latitude','longitude','sst','sst_combined','strain','voltage','speed','U','V','ice_concentration']]
            df_out = df_out.round({'latitude':3, 'longitude':3,'sst':2,'sst_combined':2,'strain':1,'voltage':1,'speed':1,'U':1,'V':1,'ice_concentration':1})
            outfile = str(df_out.trajectory_id[0]) + '_final_ice_added.csv'
        else:
            df_out = df_speed[['trajectory_id','latitude','longitude','sst','sst_combined','strain','voltage','speed','U','V']]
            df_out = df_out.round({'latitude':3, 'longitude':3,'sst':2,'sst_combined':2,'strain':1,'voltage':1,'speed':1,'U':1,'V':1})
            outfile = str(df_out.trajectory_id[0]) + '_final.csv'
        df_out.rename(columns={'sst_combined':'sst_despiked'},inplace=True)
        df_out.rename(columns={'sst':'sst_raw'},inplace=True)
    # if args.hour:
        # df_out = df_hour
        #df_out = df[['trajectory_id','latitude','longitude','sst','strain','voltage','speed']]
        #df_out = df_out.round({'latitude':3, 'longitude':3,'sst':2,'strain':1,'voltage':1,'speed':1})
    else:
        df_out = df
    
    # if args.cut:
        # outfile = str(df_out.trajectory_id[0]) + '_trimmed.csv'
    # else:
        # outfile = str(df_out.trajectory_id[0]) + '_reformatted.csv'
    df_out.to_csv(outfile)


if args.phyllis:
    df_hour['doy'] = df_hour.index.strftime('%j')
    df_hour['hour'] = df_hour.index.strftime('%H')
    df_hour['minute'] = df_hour.index.strftime('%M')
    df_phy = df_hour[['doy','hour','minute','latitude','longitude']]
    df_phy['longitude'] = df_phy.longitude * -1
    df_phy = df_phy.round({'latitude':3,'longitude':3})
    outfile = str(df_hour.trajectory_id[0]) + '_for_phyllis.csv'
    df_phy.to_csv(outfile, sep=" ", index=False)
    

    
