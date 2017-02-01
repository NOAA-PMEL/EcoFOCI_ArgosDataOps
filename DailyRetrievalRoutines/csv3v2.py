#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 00:40:29 2014

@author: eckerson
"""

import argparse
import csv
import datetime
import os

# parse incoming command line options
parser = argparse.ArgumentParser(description='translate daily argos csv files and store in local path')
parser.add_argument('pathname', metavar='pathname', type=str, help='path to .nc file')
parser.add_argument('-all','--all', action="store_true", help='translate all files')

args = parser.parse_args()

all_files = [x for x in os.listdir(args.pathname) if x.endswith('.txt')]
all_files = sorted(all_files)

if not args.all:
    all_files = [all_files[-1],]
    
for file_name in all_files:
    f = open(args.pathname + file_name)
    print "Reading file {0}".format(args.pathname + file_name)
    of = open('DailyArgosMessage_' + file_name.split('__')[-1],'w')
    print "Saving file {0}".format('DailyArgosMessage_' + file_name.split('__')[-1])

    ###read argos csv file in, alter format and output to screen
    csv_f = csv.reader(f, delimiter = ';')
    f.readline() 
    for row in csv_f:
        #print row
        if 'soap:Body' in row[0]:
            continue
        elif 'csvResponse xmlns=' in row[0]:
            continue
        elif '<return>"programNumber"' in row[0]:
            continue
        else:
            print row[12], row[6], row[29]
#two matching dates
            if row[12] and row[6] == row[29] and 191 < len(row):         
                print "Case 1"
                #lat lon is given + E, -W -> convert +W 0-360 (181 is -179 E)
                lon = round(float(row[14][:]),3)
                if lon < 0.0:
                    lon = lon * -1.
                else:
                    lon = -1. * (lon - 180.) + 180.
            
                print >>of, row [1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(lon), row[12][:4], str(datetime.datetime.strptime(row[12][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[12][11:13]+row[12][14:16], format(int(float(row[36])), '02x'), format(int(float(row[41])), '02x'),format(int(float(row[46])), '02x'),format(int(float(row[51])), '02x'),format(int(float(row[56])), '02x'),format(int(float(row[61])), '02x'),format(int(float(row[66])), '02x'),format(int(float(row[71])), '02x'),format(int(float(row[76])), '02x'),format(int(float(row[81])), '02x'),format(int(float(row[86])), '02x'),format(int(float(row[91])), '02x'),format(int(float(row[96])), '02x'),format(int(float(row[101])), '02x'),format(int(float(row[106])), '02x'),format(int(float(row[111])), '02x'),format(int(float(row[116])), '02x'),format(int(float(row[121])), '02x'),format(int(float(row[126])), '02x'),format(int(float(row[131])), '02x'),format(int(float(row[136])), '02x'),format(int(float(row[141])), '02x'),format(int(float(row[146])), '02x'),format(int(float(row[151])), '02x'),format(int(float(row[156])), '02x'),format(int(float(row[161])), '02x'),format(int(float(row[166])), '02x'),format(int(float(row[171])), '02x'),format(int(float(row[176])), '02x'),format(int(float(row[181])), '02x'),format(int(float(row[186])), '02x'),format(int(float(row[191])), '02x'),'  '+row[16]+"\n",
            elif row[12] and row[6] == row[29] and 61 < len(row):
                print "Case 2"
                #lat lon is given + E, -W -> convert +W 0-360 (181 is -179 E)
                lon = round(float(row[14][:]),3)
                if lon < 0.0:
                    lon = lon * -1.
                else:
                    lon = -1. * (lon - 180.) + 180.
            
                print >>of, row [1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(lon), row[12][:4], str(datetime.datetime.strptime(row[12][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[12][11:13]+row[12][14:16], format(int(float(row[36])), '02x'), format(int(float(row[41])), '02x'),format(int(float(row[46])), '02x'),format(int(float(row[51])), '02x'),format(int(float(row[56])), '02x'),format(int(float(row[61])), '02x'),format(int(float(row[66])), '02x'),'  '+row[16]+"\n", 
            elif row[12] and row[6] == row[29]:
                print "Case 3"
                #lat lon is given + E, -W -> convert +W 0-360 (181 is -179 E)
                lon = round(float(row[14][:]),3)
                if lon < 0.0:
                    lon = lon * -1.
                else:
                    lon = -1. * (lon - 180.) + 180.
            
                print >>of, row [1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(lon), row[12][:4], str(datetime.datetime.strptime(row[12][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[12][11:13]+row[12][14:16], format(int(float(row[36])), '02x'), format(int(float(row[41])), '02x'),format(int(float(row[46])), '02x'),'  '+row[16]+"\n",  

#only one matching date but third date is in column 26
            elif (row[12] and row[6]) == row[26] and 40 < len(row) < 190:
                print "Case 4"
                try:
                    #lat lon is given + E, -W -> convert +W 0-360 (181 is -179 E)
                    lon = round(float(row[14][:]),3)
                    if lon < 0.0:
                        lon = lon * -1.
                    else:
                        lon = -1. * (lon - 180.) + 180.
            
                    print >>of, row[1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(lon), row[26][:4], str(datetime.datetime.strptime(row[26][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[26][11:13]+row[26][14:16],row[33],row[38],row[43],row[48],'  '+row[16]+"\n", 
                except: #no lon
                    pass

            elif (row[12] and row[6]) == row[26] and 61 < len(row)  < 190:
                print "Case 5"
                try:
                    #lat lon is given + E, -W -> convert +W 0-360 (181 is -179 E)
                    lon = round(float(row[14][:]),3)
                    if lon < 0.0:
                        lon = lon * -1.
                    else:
                        lon = -1. * (lon - 180.) + 180.
            
                    print >>of, row[1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(lon), row[26][:4], str(datetime.datetime.strptime(row[26][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[26][11:13]+row[26][14:16], format(int(float(row[33])), '02x'), format(int(float(row[38])), '02x'),format(int(float(row[43])), '02x'),format(int(float(row[48])), '02x'),format(int(float(row[53])), '02x'),format(int(float(row[58])), '02x'),format(int(float(row[63])), '02x'),'  '+row[16]+"\n", 
                except: #no lon
                    pass
            elif (row[12] and row[6]) == row[26] and 190 < len(row):
                print "Case 6"
                #lat lon is given + E, -W -> convert +W 0-360 (181 is -179 E)
                try:
                    lon = round(float(row[14][:]),3)
                    if lon < 0.0:
                        lon = lon * -1.
                    else:
                        lon = -1. * (lon - 180.) + 180.
                    print >>of, row[1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(lon), row[26][:4], str(datetime.datetime.strptime(row[26][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[26][11:13]+row[26][14:16], row[33], row[38],row[43],row[48],row[53],row[58],row[63],row[68],row[73],row[78],row[83],row[88],row[93],row[98],row[103],row[108],row[113],row[118],row[123],row[128],row[133],row[138],row[143],row[148],row[153],row[158],row[163],row[168],row[173],row[178],row[183],row[188],'  '+row[16]+"\n",
                except:
                    pass
            elif row[12] and row[6] == row[26]:
                print "Case 7"
                try:
                    #lat lon is given + E, -W -> convert +W 0-360 (181 is -179 E)
                    lon = round(float(row[14][:]),3)
                    if lon < 0.0:
                        lon = lon * -1.
                    else:
                        lon = -1. * (lon - 180.) + 180.
                    print >>of, row[1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(lon), row[26][:4], str(datetime.datetime.strptime(row[26][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[26][11:13]+row[26][14:16], format(int(float(row[33])), '02x'), format(int(float(row[38])), '02x'),format(int(float(row[43])), '02x'),'  '+row[16]+"\n",  
                except: #no lon
                    pass
            else:
                print "Case 8"
                pass
                #print "No matching times found in data stream"
                #print "{0}, {1}, {2}".format(row[12], row[6], row[26])

    f.close()
    of.close()

