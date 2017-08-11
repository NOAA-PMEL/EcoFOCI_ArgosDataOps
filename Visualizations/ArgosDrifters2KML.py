#!/usr/bin/env

"""
Drifter2KML.py

Generates google earth kml files from eFOCI db and processed .vecdis/.y2014/.asc data

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import argparse
import os
import pymysql
import collections

#Science Stack
import numpy as np
from netCDF4 import Dataset

# Plotting Stack
import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.basemap import Basemap, shiftgrid
import matplotlib.pyplot as plt
import matplotlib as mpl

#user stack
import utilities.ConfigParserLocal as ConfigParserLocal

"""--------------------------------SQL Init----------------------------------------"""

def connect_to_DB(host, user, password, database):
    # Open database connection
    try:
        db = pymysql.connect(host, user, password, database)
    except:
        print "db error"
        
    # prepare a cursor object using cursor() method
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return(db,cursor)

def update_entry(db, cursor, table, drifterID, transdate):
    sql = ("UPDATE {0} SET `LastKnownTransmission`= '{1}' WHERE `ArgosNumber` = '{2}'").format(table, transdate, drifterID)
    print sql
    
    try:
        # Execute the SQL command
        cursor.execute(sql)    
        # Commit your changes in the database
        db.commit()
    except:
        print "Entry failed!!!"
        db.rollback()

def read_drifter_region(db, cursor, table, region):
    sql = ("SELECT * from `{0}` WHERE `DeploymentWaters`= '{1}' order by `lastknowntransmission`").format(table, region)
    
    print sql
    result_dic = {}
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Get column names
        rowid = {}
        counter = 0
        for i in cursor.description:
            rowid[i[0]] = counter
            counter = counter +1 
        #print rowid
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            result_dic[row['id']] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
        return (result_dic)
    except:
        print "Error: unable to fecth data"


def close_DB(db):
    # disconnect from server
    db.close()

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
        output = int(format(int(s1,16),'08b')[6:] + format(int(s2,16),'08b'),2)   
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
"""------------------------------------- KML -----------------------------------------"""
def kmlHeader():
    kml_string = (
            '<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n'
            '<kml:kml xmlns:atom=\'http://www.w3.org/2005/Atom\' xmlns:gx=\'http://www.google.com/kml/ext/2.2\' xmlns:kml=\'http://www.opengis.net/kml/2.2\'>\n'
            '<kml:Document>\n'
            '<name>EcoFOCI</name>\n'
            )
    return kml_string

def kmlStyle():
    kml_string = (
            '        <Style id=\'drifter\'>\n'
            '            <LineStyle>\n'
            '                <color>ffffaa07</color>\n'
            '                <width>2</width>\n'
            '            </LineStyle>\n'
            '            <IconStyle>\n'
            '                <scale>0.5</scale>\n'
            '                <Icon>\n'
            '                    <href>http://maps.google.com/mapfiles/kml/shapes/donut.png</href>\n'
            '                </Icon>\n'
            '            </IconStyle>\n'
            '        </Style>\n'
            '        <Style id=\'ctd\'>\n'
            '            <LineStyle>\n'
            '                <color>b366ff00</color>\n'
            '                <width>2</width>\n'
            '            </LineStyle>\n'
            '            <IconStyle>\n'
            '                <scale>1.2</scale>\n'
            '                <Icon>\n'
            '                    <href>http://www.pmel.noaa.gov/co2/images/hydrographic-cruises-icon.png</href>\n'
            '                </Icon>\n'
            '            </IconStyle>\n'
            '        </Style>\n'
            '        <Style id=\'mooring\'>\n'
            '            <IconStyle>\n'
            '                <scale>1.2</scale>\n'
            '                <Icon>\n'
            '                    <href>http://maps.google.com/mapfiles/kml/shapes/donut.png</href>\n'
            '                </Icon>\n'
            '            </IconStyle>\n'
            '        </Style>\n'
                )
    return kml_string

"""------------------------------------- MAPS -----------------------------------------"""

def etopo5_data():
    """ read in etopo5 topography/bathymetry. """
    file = 'data/etopo5.nc'
    etopodata = Dataset(file)
    
    topoin = etopodata.variables['bath'][:]
    lons = etopodata.variables['X'][:]
    lats = etopodata.variables['Y'][:]
    etopodata.close()
    
    topoin,lons = shiftgrid(0.,topoin,lons,start=False) # -360 -> 0
    
    #lons, lats = np.meshgrid(lons, lats)
    
    return(topoin, lats, lons)


def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return idx
        
"""------------------------------------- Main -----------------------------------------"""

# parse incoming command line options
parser = argparse.ArgumentParser(description='Create KML and png images of active drifters')
parser.add_argument('sourcedir', metavar='sourcedir', type=str, help='path to daily drifter files parsed by ID')
parser.add_argument('idlist', metavar='idlist', type=str, help='full path to file with list of active drifters')
parser.add_argument('--kml', action="store_true", help='output as kml')
parser.add_argument('--png', action="store_true", help='output as png')
parser.add_argument('--svg', action="store_true", help='output as svg')
parser.add_argument('--dk', action="store_true", help='read a d. kachel year file eg .y2014')
parser.add_argument('--all_region', metavar='all_region', type=str, 
    help='output 5day png files for movie generation for specified region (Bering, Arctic, GOA)')
parser.add_argument('--updateDB', action="store_true", help='add last known transmission to database')
parser.add_argument('--all_movie_img', action="store_true", help='process each movie frame for current year')

args = parser.parse_args()
## get list of all files in directory
argos_data_files = [x for x in os.listdir(args.sourcedir) if x.endswith('.txt')]
if args.dk:
    argos_data_files = [x for x in os.listdir(args.sourcedir) if 'y' in x]
argos_data_files = sorted(argos_data_files)

### Generates a kml file for every drifter
file_path = args.sourcedir

with open(args.idlist) as idl:
    activeargosids = {}
    for line in idl:
        activeargosids[line.strip()] = 'isactive'

if args.all_region == 'arctic':
    etopo_levels=[-1000, -100, -50, -25, ]  #chuckchi
else:
    etopo_levels=[-1000, -200, -100, -70, ]  #berring
    
### build kml file
if args.kml:
    
    #cycle though list of provided active argos id's
    for ind, drifterID in enumerate(activeargosids.keys()):
        print "Woring on Argos ID {0}".format(drifterID)
        

        kml_header = kmlHeader()

        kml_style = kmlStyle()

        kml_type = (
            '<Folder>\n'
            '<name>{0}</name>\n'
            '      <Style>\n'
            '    <ListStyle>\n'
            '      <listItemType>checkHideChildren</listItemType>\n'
            '    </ListStyle>\n'
            '  </Style>\n'
            ).format(drifterID)


        kml_footer = (
            '</kml:Document>\n'
            '</kml:kml>\n'
            )
            
        kml = ''
        
        isemptydata = True
        drifter_data = {}
        lastknowntransmission = {}
        for af_id in argos_data_files: #cycle through all available files for an id
            if str(drifterID) in af_id: #active id must be in file name
                drifter_data = read_drifter(file_path + af_id, drifter_data, isemptydata)
                isemptydata = False
                lastknowntransmission[drifterID] = af_id.split('.txt')[0].split('_')[-1]
                

        ### kml content
        # placemarks for each data point
        for dval in drifter_data['DATA']: ## placemarks
            lat = float(dval[1])
            lon = float(dval[2]) * -1.
            drifter_time = sqldate2GEdate(dval[3], dval[4], dval[5])
            if dval[5][0:2] == '12': #only plot 12z data
                kml = kml + (
                   '        <Placemark>\n'
                   '            <TimeStamp>\n'
                   '                <when>{3}</when>\n'
                   '            </TimeStamp>\n'
                   '        <styleUrl>#drifter</styleUrl>\n'
                   '        <Point>\n'
                   '            <coordinates>{1:3.4f},{0:3.4f}</coordinates>\n'
                   '        </Point>\n'
                   '        </Placemark>\n'
                   ).format(lat,lon,drifterID,drifter_time)


        #line for drifter track
        kml = kml + (
        '</Folder>\n'
        '<Placemark>\n'
        '  <name>{0} Track</name>\n'
        '  <LineString>\n'
        '    <tessellate>1</tessellate>\n'
        '    <altitudeMode>absolute</altitudeMode>\n'
        '<coordinates>\n'
        ).format(drifterID)
        
        
        latlon_str = []
        for dval in drifter_data['DATA']: ## placemarks
            lat = float(dval[1])
            lon = float(dval[2]) * -1.
            latlon_str = latlon_str + [str(lon) + ',' + str(lat)]

        kml = kml + ' '.join(latlon_str) + (
        '</coordinates>\n'
        '  </LineString>\n'
        '</Placemark>\n'
        )

        fid = open(('{0}_drifter.kml').format(drifterID), 'wb')
        #fid.write( 'Content-Type: application/vnd.google-earth.kml+xml\n' )
        fid.write( kml_header + kml_style + kml_type + kml + kml_footer )
        fid.close()
        
                
        if args.updateDB:
            print lastknowntransmission
            db_config = ConfigParserLocal.get_config('db_config_drifters.pyini')
            (db,cursor) = connect_to_DB(db_config['host'], db_config['user'], db_config['password'], db_config['database'])
            table = 'drifter_ids'
            update_entry(db, cursor, table, int(lastknowntransmission.keys()[0]), lastknowntransmission.values()[0])
            close_DB(db)
            
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

        if args.dk:
            drifter_data['DATA'] = [x[0].split() for x in drifter_data['DATA']]
            lat = [float(x[0]) for x in drifter_data['DATA']]
            lat = np.array(lat)
            lon = [float(x[1]) for x in drifter_data['DATA']] 
            lon = np.array(lon)
            year = [int(x[2]) for x in drifter_data['DATA']] 
            year = np.array(year)
            doy = [float(x[3]) for x in drifter_data['DATA']] 
            doy = np.array(doy)
        
            sst = [sst_exits(x) for x in drifter_data['DATA']] #helper function sst_exits defined above
            sst = (np.array(sst) * 0.04) - 2.
            
        else:
            lat = [float(x[1]) for x in drifter_data['DATA']]
            lat = np.array(lat)
            lon = [float(x[2]) for x in drifter_data['DATA']] 
            lon = np.array(lon)
            year = [int(x[3]) for x in drifter_data['DATA']] 
            year = np.array(year)
            doy = [float(x[4]) for x in drifter_data['DATA']] 
            doy = np.array(doy)
        
            sst = [sst_exits(x) for x in drifter_data['DATA']] #helper function sst_exits defined above
            sst = (np.array(sst) * 0.04) - 2.
                                        
        ## plot boundaries for topography
        (topoin, elats, elons) = etopo5_data()

        #build regional subset of data
        topoin = topoin[find_nearest(elats,lat.min()-5):find_nearest(elats,lat.max()+5),find_nearest(elons,-1*(lon.max()+5)):find_nearest(elons,-1*(lon.min()-5))]
        elons = elons[find_nearest(elons,-1*(lon.max()+5)):find_nearest(elons,-1*(lon.min()-5))]
        elats = elats[find_nearest(elats,lat.min()-5):find_nearest(elats,lat.max()+5)]

        print "Generating zoomed image"

        #determine regional bounding
        y1 = np.floor(lat.min()-1)
        y2 = np.ceil(lat.max()+1)
        x1 = np.ceil(-1*(lon.max()+2))
        x2 = np.floor(-1*(lon.min()-2))
        
        fig1 = plt.figure(1)
        #Custom adjust of the subplots
        ax = plt.subplot(1,1,1)
        
                
        m = Basemap(resolution='i',projection='merc', llcrnrlat=y1, \
                    urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,\
                    lat_ts=45)
        
        elons, elats = np.meshgrid(elons, elats)
        x, y = m(-1. * lon,lat)
        ex, ey = m(elons, elats)

        m.drawcountries(linewidth=0.5)
        m.drawcoastlines(linewidth=0.5)
        m.drawparallels(np.arange(y1,y2,2.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
        m.drawmeridians(np.arange(x1-20,x2,4.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
        m.fillcontinents(color='white')

    
        m.contourf(ex,ey,topoin, levels=etopo_levels, colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', alpha=.75)
        m.scatter(x,y,20,marker='.', edgecolors='none', c=doy, vmin=0, vmax=365, cmap='jet')
        c = plt.colorbar()
        c.set_label("Julian Day")

        ### convert doy to date information
        datedoy = [datetime.timedelta(d - 1) for d in doy]
        dateyear = [datetime.datetime(d,1,1) for d in year]
        str_date = [(d+dd).strftime('%Y-%m-%d') for d,dd in zip(dateyear,datedoy)]
        xd = np.array([])
        yd = np.array([])
        last_doy = 0
        for i,k in enumerate(str_date):
            if (doy[i] % 7 == 0) and (last_doy != doy[i]):
                str_date[i] = k
                last_doy = doy[i]
                xd = np.hstack((xd,x[i]))
                yd = np.hstack((yd,y[i]))
            else:
                str_date[i] = ''

           
        m.scatter(xd,yd,20,marker='+', color='k')
    
        for str_date_l, xpt, ypt in zip(str_date, x, y):
            plt.text(xpt+10000, ypt+5000, str_date_l,fontsize=5)

 
        f = plt.gcf()
        DefaultSize = f.get_size_inches()
        f.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )
        plt.savefig(drifterID + '_zoom_drifter.png', bbox_inches='tight', dpi=300)
        plt.close()

        
        print "Generating wide image"

        #determine regional bounding
        y1 = np.floor(lat.min()-2.5)
        y2 = np.ceil(lat.max()+2.5)
        x1 = np.ceil(-1*(lon.max()+5))
        x2 = np.floor(-1*(lon.min()-5))
        
        fig2 = plt.figure(2)
        #Custom adjust of the subplots
        ax = plt.subplot(1,1,1)
        
        m = Basemap(resolution='i',projection='merc', llcrnrlat=y1, \
                    urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,\
                    lat_ts=45, lon_0=180)

        #elons, elats = np.meshgrid(elons, elats)
        x, y = m(-1. * lon,lat)
        ex, ey = m(elons, elats)

        m.drawcountries(linewidth=0.5)
        m.drawcoastlines(linewidth=0.5)
        m.drawparallels(np.arange(y1,y2,5.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
        m.drawmeridians(np.arange(x1-20,x2,5.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
        m.fillcontinents(color='white')
    
        m.contourf(ex,ey,topoin, levels=etopo_levels, colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', alpha=.75)
        my_cmap = mpl.cm.get_cmap('bwr')
        my_cmap.set_under('k')
        m.scatter(x,y,20,marker='.', edgecolors='none', c=sst, vmin=-5, vmax=20, cmap='seismic')
        c = plt.colorbar()
        c.set_label("SST")
    
        f = plt.gcf()
        DefaultSize = f.get_size_inches()
        f.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )
        plt.savefig(drifterID + '_wide_drifter.png', bbox_inches='tight', dpi=300)
        plt.close()
        
                
        if args.updateDB:
            print lastknowntransmission
            db_config = ConfigParserLocal.get_config('db_config_drifters.pyini')
            (db,cursor) = connect_to_DB(db_config['host'], db_config['user'], db_config['password'], db_config['database'])
            table = 'drifter_ids'
            update_entry(db, cursor, table, int(lastknowntransmission.keys()[0]), lastknowntransmission.values()[0])
            close_DB(db)
            

if args.all_region and not args.all_movie_img:

    region = args.all_region
    ### Retrieve general deployment region from database of metadata
    db_config = ConfigParserLocal.get_config('db_config_drifters.pyini')
    (db,cursor) = connect_to_DB(db_config['host'], db_config['user'], db_config['password'], db_config['database'])
    table = 'drifter_ids'
    drifterIDs = read_drifter_region(db, cursor, table, region)
    close_DB(db)
    
    date_max = datetime.datetime(1,1,1)
    for ind_num, k in enumerate(drifterIDs.keys()):
        drifterID = drifterIDs[k]['ArgosNumber']
        print "Woring on Argos ID {0}".format(drifterID)
        
        isemptydata = True
        drifter_data = {}
        for af_id in argos_data_files: #cycle through all available files for an id
            if str(drifterID) in af_id: #active id must be in file name
                print af_id
                drifter_data = read_drifter(file_path + af_id, drifter_data, isemptydata)
                isemptydata = False

        lat = [float(x[1]) for x in drifter_data['DATA']]
        lat = np.array(lat)
        lon = [float(x[2]) for x in drifter_data['DATA']] 
        lon = np.array(lon)
        year = [int(x[3]) for x in drifter_data['DATA']] 
        year = np.array(year)
        doy = [float(x[4]) for x in drifter_data['DATA']] 
        doy = np.array(doy)
        
        current_year = datetime.datetime.now().year
        sub_year_ind = (year >= current_year)
        current_doy = datetime.datetime.now().timetuple().tm_yday
        sub_doy_ind = (doy >= current_doy -5.) & ( year >= current_year)
        
        ### Initialize plot area
        ## plot boundaries for topography
        (topoin, elats, elons) = etopo5_data()

        #build regional subset of etopo5 data
        print "Region input is {0}".format(region.lower())
        if region.lower().strip() == 'goa':
            print "Processing as goa"
            topoin = topoin[find_nearest(elats,47):find_nearest(elats,63),find_nearest(elons,-165):find_nearest(elons,-135)]
            elons = elons[find_nearest(elons,-165):find_nearest(elons,-135)]
            elats = elats[find_nearest(elats,47):find_nearest(elats,63)]
            y1 = 47.
            y2 = 63.
            x1 = -165.
            x2 = -135.
        elif region.lower().strip() == 'berring':
            print "Processing as berring"
            topoin = topoin[find_nearest(elats,50):find_nearest(elats,67),find_nearest(elons,-200):find_nearest(elons,-155)]
            elons = elons[find_nearest(elons,-200):find_nearest(elons,-155)]
            elats = elats[find_nearest(elats,50):find_nearest(elats,67)]
            y1 = 50.
            y2 = 67.
            x1 = -200.
            x2 = -155.
        elif region.lower().strip() == 'arctic':
            print "Processing as arctic"
            topoin = topoin[find_nearest(elats,65):find_nearest(elats,77),find_nearest(elons,-180):find_nearest(elons,-150)]
            elons = elons[find_nearest(elons,-180):find_nearest(elons,-150)]
            elats = elats[find_nearest(elats,65):find_nearest(elats,77)]
            y1 = 65.
            y2 = 77.
            x1 = -180.
            x2 = -150.
        else:
            print "Processing as other"
            topoin = topoin[find_nearest(elats,lat.min()-5):find_nearest(elats,lat.max()+5),find_nearest(elons,-1*(lon.max()+5)):find_nearest(elons,-1*(lon.min()-5))]
            elons = elons[find_nearest(elons,-1*(lon.max()+5)):find_nearest(elons,-1*(lon.min()-5))]
            elats = elats[find_nearest(elats,lat.min()-5):find_nearest(elats,lat.max()+5)]
            #determine regional bounding
            y1 = np.floor(lat.min()-1)
            y2 = np.ceil(lat.max()+1)
            x1 = np.ceil(-1*(lon.max()+2))
            x2 = np.floor(-1*(lon.min()-2))

        print "Generating image"
        
        fig1 = plt.figure(1)
        #Custom adjust of the subplots
        ax = plt.subplot(1,1,1)
        plt.hold(True)        
                
        m = Basemap(resolution='i',projection='merc', llcrnrlat=y1, \
                    urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,\
                    lat_ts=45)
        
        elons, elats = np.meshgrid(elons, elats)
        x, y = m(-1. * lon[sub_year_ind],lat[sub_year_ind])
        x_5d, y_5d = m(-1. * lon[sub_doy_ind],lat[sub_doy_ind])
        ex, ey = m(elons, elats)

        if ind_num == 0:
            m.drawcountries(linewidth=0.5)
            m.drawcoastlines(linewidth=0.5)
            m.drawparallels(np.arange(y1,y2,3.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
            m.drawmeridians(np.arange(x1-20,x2,5.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
            m.fillcontinents(color='white')
            m.contourf(ex,ey,topoin, levels=etopo_levels, colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', alpha=.75)
        
        m.scatter(x,y,20,marker='.', c='w', alpha=0.1)
        m.scatter(x_5d,y_5d,20,marker='.', c='r', alpha=0.1, edgecolors='none')


        ### convert doy to date information
        datedoy = [datetime.timedelta(d - 1) for d in doy]
        dateyear = [datetime.datetime(d,1,1) for d in year]
        str_date = [(d+dd) for d,dd in zip(dateyear,datedoy)]

        if np.max(str_date) >= date_max:
            str_date_max = str_date[-1].strftime('%Y-%m-%d')
            date_max = np.max(str_date)
            print "Latest day is {0}".format(date_max) 

    plt.annotate(str_date_max, xy=(0.025, .025), color='k', xycoords='axes fraction', fontsize=16)
 
    f = plt.gcf()
    DefaultSize = f.get_size_inches()
    f.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )
    plt.savefig('images/' + region + '_movie_' + str_date_max + '.png', bbox_inches='tight', dpi=300)
    plt.close()

            
if args.all_region and args.all_movie_img:

    region = args.all_region
    ### Retrieve general deployment region from database of metadata
    db_config = ConfigParserLocal.get_config('db_config_drifters.pyini')
    (db,cursor) = connect_to_DB(db_config['host'], db_config['user'], db_config['password'], db_config['database'])
    table = 'drifter_ids'
    drifterIDs = read_drifter_region(db, cursor, table, region)
    close_DB(db)

    for tdoy in range(0,datetime.datetime.now().timetuple().tm_yday,1):
#    for tdoy in range(274,365,1):

        for ind_num, k in enumerate(drifterIDs.keys()):
            drifterID = drifterIDs[k]['ArgosNumber']
            print "Woring on Argos ID {0}".format(drifterID)
        
            
            current_year = datetime.datetime.now().year
            #current_year = 2015
            file_date = (datetime.timedelta(tdoy - 1) + datetime.datetime(current_year,1,1)).strftime('%Y-%m-%d')
            isemptydata = True
            drifter_data = {}
            print "Stopping on day {0}".format(file_date)

            for af_id in argos_data_files: #cycle through all available files for an id
                if str(drifterID) in af_id: #active id must be in file name
                    print af_id
                    if datetime.datetime.strptime((af_id.split('_')[-1].split('.')[0]),'%Y-%m-%d') >(datetime.timedelta(tdoy - 1) + datetime.datetime(current_year,1,1)) :
                        break
                    else:
                        drifter_data = read_drifter(file_path + af_id, drifter_data, isemptydata)
                        isemptydata = False
            
            
            try:
                lat = [float(x[1]) for x in drifter_data['DATA']]
                lat = np.array(lat)
                lon = [float(x[2]) for x in drifter_data['DATA']] 
                lon = np.array(lon)
                year = [int(x[3]) for x in drifter_data['DATA']] 
                year = np.array(year)
                doy = [float(x[4]) for x in drifter_data['DATA']] 
                doy = np.array(doy)
                sub_year_ind = (year >= current_year)
                sub_doy_ind = (doy >= tdoy -5.) & ( year >= current_year)
                nodata = False
            except:
                nodata = True
                
            ### Initialize plot area
            ## plot boundaries for topography
            (topoin, elats, elons) = etopo5_data()

            #build regional subset of etopo5 data
            print "Region input is {0}".format(region.lower())
            if region.lower().strip() == 'goa':
                print "Processing as goa"
                topoin = topoin[find_nearest(elats,47):find_nearest(elats,63),find_nearest(elons,-165):find_nearest(elons,-135)]
                elons = elons[find_nearest(elons,-165):find_nearest(elons,-135)]
                elats = elats[find_nearest(elats,47):find_nearest(elats,63)]
                y1 = 47.
                y2 = 63.
                x1 = -165.
                x2 = -135.
            elif region.lower().strip() == 'berring':
                print "Processing as berring"
                topoin = topoin[find_nearest(elats,50):find_nearest(elats,67),find_nearest(elons,-200):find_nearest(elons,-155)]
                elons = elons[find_nearest(elons,-200):find_nearest(elons,-155)]
                elats = elats[find_nearest(elats,50):find_nearest(elats,67)]
                y1 = 50.
                y2 = 67.
                x1 = -200.
                x2 = -155.
            elif region.lower().strip() == 'arctic':
                print "Processing as arctic"
                topoin = topoin[find_nearest(elats,65):find_nearest(elats,77),find_nearest(elons,-180):find_nearest(elons,-150)]
                elons = elons[find_nearest(elons,-180):find_nearest(elons,-150)]
                elats = elats[find_nearest(elats,65):find_nearest(elats,77)]
                y1 = 65.
                y2 = 77.
                x1 = -180.
                x2 = -150.
            else:
                print "Processing as other"
                topoin = topoin[find_nearest(elats,lat.min()-5):find_nearest(elats,lat.max()+5),find_nearest(elons,-1*(lon.max()+5)):find_nearest(elons,-1*(lon.min()-5))]
                elons = elons[find_nearest(elons,-1*(lon.max()+5)):find_nearest(elons,-1*(lon.min()-5))]
                elats = elats[find_nearest(elats,lat.min()-5):find_nearest(elats,lat.max()+5)]
                #determine regional bounding
                y1 = np.floor(lat.min()-1)
                y2 = np.ceil(lat.max()+1)
                x1 = np.ceil(-1*(lon.max()+2))
                x2 = np.floor(-1*(lon.min()-2))

            print "Generating image"
    
            fig1 = plt.figure(1)
            #Custom adjust of the subplots
            ax = plt.subplot(1,1,1)
            plt.hold(True)        
            
            m = Basemap(resolution='i',projection='merc', llcrnrlat=y1, \
                        urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,\
                        lat_ts=45)

            elons, elats = np.meshgrid(elons, elats)
            ex, ey = m(elons, elats)
            if nodata is False:    
                x, y = m(-1. * lon[sub_year_ind],lat[sub_year_ind])
                if len(sub_doy_ind) != 0:
                    x_5d, y_5d = m(-1. * lon[sub_doy_ind],lat[sub_doy_ind])

            if ind_num == 0:
                m.drawcountries(linewidth=0.5)
                m.drawcoastlines(linewidth=0.5)
                m.drawparallels(np.arange(y1,y2,3.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
                m.drawmeridians(np.arange(x1-20,x2,5.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
                m.fillcontinents(color='white')
                m.contourf(ex,ey,topoin, levels=etopo_levels, colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', alpha=.75)
    
            if nodata is False:    
                m.scatter(x,y,20,marker='.', c='w', alpha=0.1)
                m.scatter(x_5d,y_5d,20,marker='.', c='r', alpha=0.1, edgecolors='none')


            ### convert doy to date information
            #datedoy = [datetime.timedelta(d - 1) for d in doy]
            #dateyear = [datetime.datetime(d,1,1) for d in year]
            #str_date = [(d+dd).strftime('%Y-%m-%d') for d,dd in zip(dateyear,datedoy)]
            #plt.text(.25,.25,str_date[-1])

        plt.annotate(file_date, xy=(0.025, .025), color='k', xycoords='axes fraction', fontsize=16)

 
        f = plt.gcf()
        DefaultSize = f.get_size_inches()
        f.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )
        plt.savefig('images/' + region + '_movie_' + file_date + '.png', bbox_inches='tight', dpi=300)
        plt.close()
