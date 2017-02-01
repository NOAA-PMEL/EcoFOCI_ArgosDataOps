#!/usr/bin/env

"""
DrifterVectorPlot.py

Calculates speed and generates quiver plots of drifter U,V components
Provides additional option to output data as a csv / json file for web manipulation

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import argparse
import os
import collections

#Science Stack
import numpy as np
from netCDF4 import Dataset

# Plotting Stack
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import WeekdayLocator, DateFormatter, MonthLocator

#user stack
import utilities.haversine as sphered


"""------------------------------------- Read Drifter ----------------------------------"""

def read_drifter(file_in, datain, isemptydata):
    
    if isemptydata:
        datadic = collections.OrderedDict()
        counter = 0
        datadic['DATA'] = []
    else:
        datadic = collections.OrderedDict()
        datadic['DATA'] = datain['DATA']
        counter = len(datain['DATA'])
        
    with open(file_in, 'r') as f:
        for line in f:
            datadic['DATA'] = datadic['DATA'] + [line.strip().split('\t')]  
            counter +=1
    return datadic

def sst_exits(x):
    try:
        output = int(bin(int(x[7],16))[8:10]+bin(int(x[8],16))[2:],2)    
    except:
        output = -500
    return output

"""------------------------------------- Format-----------------------------------------"""


def sqldate2GEdate(yyyy, doy, hhmm):

    try:
        outstr = datetime.datetime.strptime((yyyy + ' ' + doy + ' ' + hhmm), '%Y %j %H%M').strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        outstr = '0000-00-00T00:00:00Z'
        

    return outstr

"""------------------------------------- MAPS/plots -----------------------------------"""

def uvcurrent_plot(magnitude,heading,datet_stamp):

    magnitude[magnitude >= 1000] = 0
    
    u_comp = [np.cos(np.deg2rad(d))*s for s, d in zip(magnitude,heading)]
    v_comp = [np.sin(np.deg2rad(d))*s for s, d in zip(magnitude,heading)]
    date_stamp = [s.toordinal() + s.second/86400. + s.minute/1440. + s.hour /24. for s in datet_stamp]
    
    u_comp = np.array(u_comp) /100.
    v_comp = np.array(v_comp) /100.
    magnitude = magnitude /100.
    
    # Plot quiver
    fig1 = plt.figure(1)
    ax1 = plt.subplot(2,1,1)
    ax2 = plt.subplot(2,1,2)

    maxmag = max(magnitude) 
    ax1.set_ylim(-maxmag, maxmag)
    fill1 = ax1.fill_between(date_stamp, magnitude, 0, color='k', alpha=0.1)

    # Fake 'box' to be able to insert a legend for 'Magnitude'
    p = ax1.add_patch(plt.Rectangle((1,1),1,1,fc='k',alpha=0.1))
    leg1 = ax1.legend([p], ["Current magnitude [m/s]"],loc='lower right')
    leg1._drawFrame=False

    # 1D Quiver plot
    q = ax1.quiver(date_stamp,0,(u_comp ),\
                   (v_comp ),
                   color='r',
                   units='y',
                   scale_units='y',
                   scale = 1,
                   headlength=1,
                   headaxislength=1,
                   width=0.01,
                   alpha=0.50)
    qk = plt.quiverkey(q,.2, 0.05, 0.2,
                   r'$.2 \frac{cm}{s}$',
                   labelpos='W',
                   fontproperties={'weight': 'bold'})

    # Plot u and v components
    ax1.axes.get_xaxis().set_visible(False)
    ax1.set_xlim(min(date_stamp),max(date_stamp)+0.5)
    ax1.set_ylabel("Velocity (cm/s)")
    ax2.plot(date_stamp, v_comp , 'b-')
    ax2.plot(date_stamp, u_comp , 'g-')
    ax2.set_xlim(min(date_stamp),max(date_stamp)+0.5)
    ax2.set_ylabel("Velocity (cm/s)")

    ax2.xaxis.set_major_locator(WeekdayLocator(interval=1))
    ax2.xaxis.set_minor_locator(WeekdayLocator())
    ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    fig1.autofmt_xdate()    
    # Set legend location - See: http://matplotlib.org/users/legend_guide.html#legend-location
    leg2 = plt.legend(['v','u'],loc='upper left')
    leg2._drawFrame=False
    f = plt.gcf()
    DefaultSize = f.get_size_inches()
    f.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

    return (fig1, plt)


def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return idx
        
"""------------------------------------- Main -----------------------------------------"""

# parse incoming command line options
parser = argparse.ArgumentParser(description='Create KML and png images of active drifters')
parser.add_argument('sourcedir', metavar='sourcedir', type=str, help='path to daily drifter files parsed by ID')
parser.add_argument('idlist', metavar='idlist', type=str, help='full path to file with list of active drifters')
parser.add_argument('--png', action="store_true", help='output as png')
parser.add_argument('--svg', action="store_true", help='output as svg')
parser.add_argument('--csv', action="store_true", help='output as csv for web')

args = parser.parse_args()
## get list of all files in directory
argos_data_files = [x for x in os.listdir(args.sourcedir) if x.endswith('.txt')]
argos_data_files = sorted(argos_data_files)

file_path = args.sourcedir

with open(args.idlist) as idl:
    activeargosids = {}
    for line in idl:
        activeargosids[line.strip()] = 'isactive'

   
            
### Basemap Visualization
if args.png or args.svg:

   #cycle though list of provided active argos id's
    for ind, drifterID in enumerate(activeargosids.keys()):
        print "Woring on Argos ID {0}".format(drifterID)
        
        isemptydata = True
        drifter_data = {}
        lastknowntransmission = {}
        for af_id in argos_data_files: #cycle through all available files for an id
            if str(drifterID) in af_id: #active id must be in file name
                print af_id
                drifter_data = read_drifter(file_path + af_id, drifter_data, isemptydata)
                isemptydata = False
                lastknowntransmission[drifterID] = af_id.split('.txt')[0].split('_')[-1]

        lat = [float(x[1]) for x in drifter_data['DATA']]
        lat = np.array(lat)
        lon = [float(x[2]) for x in drifter_data['DATA']] 
        lon = np.array(lon)
        year = [datetime.datetime.strptime((x[3]),'%Y') for x in drifter_data['DATA']] 
        doy = [datetime.timedelta(float(x[4])-1) for x in drifter_data['DATA']] 
        fracday = [datetime.timedelta(float(x[5][:2])/24.) + datetime.timedelta(float(x[5][2:])/(60.*24.)) for x in drifter_data['DATA']] 

        sst = [sst_exits(x) for x in drifter_data['DATA']] #helper function sst_exits defined above
        sst = (np.array(sst) * 0.04) - 2.
                    
        sample_date = [a + b + c for a, b, c in zip(fracday, doy, year)]
        
        #calculate distance between two points
        #destination = [np.float(row['D']),np.float(row['C'])]
        location_pair = zip(lat,lon)
        
        Distance2Station = [0]
        TimeElapsedSeconds = [0]
        SpeedCMS = [0]
        Bearing = [0]
        
        for n, site in enumerate(location_pair):
            if n==0:
                origin = site
            else:
                Distance2Station = Distance2Station + [sphered.distance(origin,site) ]
                TimeElapsedSeconds = TimeElapsedSeconds + [(sample_date[n] - sample_date[n-1])]
                Bearing = Bearing + [sphered.bearing(origin,site)]
                if TimeElapsedSeconds[n].seconds != 0:
                    SpeedCMS = SpeedCMS + [(Distance2Station[n] * 100000.) / TimeElapsedSeconds[n].seconds]
                else:
                    SpeedCMS = SpeedCMS + [1e35]
                
                origin = site
        
        SpeedCMS = np.array(SpeedCMS)
        
        (fig1,plt) = uvcurrent_plot(SpeedCMS,Bearing,sample_date)

        plt.savefig(drifterID + '_vel.png', bbox_inches='tight', dpi=300)
        plt.close()

        ### temperature timeseries
        date_stamp = np.array([s.toordinal() + s.second/86400. + s.minute/1440. + s.hour /24. for s in sample_date])
        fig = plt.figure(2)

        ax2 = plt.subplot2grid((3, 1), (1, 0), colspan=1, rowspan=3)
        p2 = ax2.plot(sample_date, sst,'k.', markersize=2)
        ax2.set_ylim([sst[sst != 1e35].min()-0.5,sst[sst != 1e35].max()+0.5])
        ax2.set_xlim([date_stamp.min(),date_stamp.max()])
        plt.ylabel('SST')
        ax2.xaxis.set_major_locator(MonthLocator(interval=2))
        ax2.xaxis.set_minor_locator(MonthLocator())
        ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m'))

        fig.autofmt_xdate()
        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )
        plt.savefig(drifterID + '_temp.png', bbox_inches='tight', dpi=300)
        plt.close()

if args.csv:
   #cycle though list of provided active argos id's
    for ind, drifterID in enumerate(activeargosids.keys()):
        print "Woring on Argos ID {0}".format(drifterID)
        
        isemptydata = True
        drifter_data = {}
        lastknowntransmission = {}
        for af_id in argos_data_files: #cycle through all available files for an id
            if str(drifterID) in af_id: #active id must be in file name
                print af_id
                drifter_data = read_drifter(file_path + af_id, drifter_data, isemptydata)
                isemptydata = False
                lastknowntransmission[drifterID] = af_id.split('.txt')[0].split('_')[-1]

        lat = [float(x[1]) for x in drifter_data['DATA']]
        lat = np.array(lat)
        lon = [float(x[2]) for x in drifter_data['DATA']] 
        lon = np.array(lon)
        year = [datetime.datetime.strptime((x[3]),'%Y') for x in drifter_data['DATA']] 
        doy = [datetime.timedelta(float(x[4])-1) for x in drifter_data['DATA']] 
        fracday = [datetime.timedelta(float(x[5][:2])/24.) + datetime.timedelta(float(x[5][2:])/(60.*24.)) for x in drifter_data['DATA']] 

        sst = [sst_exits(x) for x in drifter_data['DATA']] #helper function sst_exits defined above
        sst = (np.array(sst) * 0.04) - 2.
                    
        sample_date = [a + b + c for a, b, c in zip(fracday, doy, year)]
        
        #calculate distance between two points
        #destination = [np.float(row['D']),np.float(row['C'])]
        location_pair = zip(lat,lon)
        
        Distance2Station = [0]
        TimeElapsedSeconds = [0]
        SpeedCMS = [0]
        Bearing = [0]
        
        for n, site in enumerate(location_pair):
            if n==0:
                origin = site
            else:
                Distance2Station = Distance2Station + [sphered.distance(origin,site) ]
                TimeElapsedSeconds = TimeElapsedSeconds + [(sample_date[n] - sample_date[n-1])]
                Bearing = Bearing + [sphered.bearing(origin,site)]
                if TimeElapsedSeconds[n].seconds != 0:
                    SpeedCMS = SpeedCMS + [(Distance2Station[n] * 100000.) / TimeElapsedSeconds[n].seconds]
                else:
                    SpeedCMS = SpeedCMS + [1e35]
                
                origin = site
        
        SpeedCMS = np.array(SpeedCMS)
        date_stamp = np.array([s.toordinal() + s.second/86400. + s.minute/1440. + s.hour /24. for s in sample_date])

        of = open(drifterID +'_temp.csv','w')    
        of.write("Date,SST\n")
        
        for ind,val in enumerate(sst):
            of.write(("{0},{1}\n").format(sample_date[ind],sst[ind]))
        
        of.close()
