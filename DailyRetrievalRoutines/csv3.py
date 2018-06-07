#!/usr/local/anaconda/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 00:40:29 2014

@author: eckerson
"""


import sys
file_name = sys.argv[1]


import csv
import datetime



f = open(file_name)


csv_f = csv.reader(f, delimiter = ';')

f.readline() 
for row in csv_f:
    if row[12] and row[6] == row[29] and 191 < len(row):         
        print row [1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(round(float(row[14][1:]),3)), row[12][:4], str(datetime.datetime.strptime(row[12][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[12][11:13]+row[12][14:16], format(int(float(row[36])), '02x'), format(int(float(row[41])), '02x'),format(int(float(row[46])), '02x'),format(int(float(row[51])), '02x'),format(int(float(row[56])), '02x'),format(int(float(row[61])), '02x'),format(int(float(row[66])), '02x'),format(int(float(row[71])), '02x'),format(int(float(row[76])), '02x'),format(int(float(row[81])), '02x'),format(int(float(row[86])), '02x'),format(int(float(row[91])), '02x'),format(int(float(row[96])), '02x'),format(int(float(row[101])), '02x'),format(int(float(row[106])), '02x'),format(int(float(row[111])), '02x'),format(int(float(row[116])), '02x'),format(int(float(row[121])), '02x'),format(int(float(row[126])), '02x'),format(int(float(row[131])), '02x'),format(int(float(row[136])), '02x'),format(int(float(row[141])), '02x'),format(int(float(row[146])), '02x'),format(int(float(row[151])), '02x'),format(int(float(row[156])), '02x'),format(int(float(row[161])), '02x'),format(int(float(row[166])), '02x'),format(int(float(row[171])), '02x'),format(int(float(row[176])), '02x'),format(int(float(row[181])), '02x'),format(int(float(row[186])), '02x'),format(int(float(row[191])), '02x'),'  '+row[16]+"\n",
    elif row[12] and row[6] == row[29] and 61 < len(row):
        print row [1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(round(float(row[14][1:]),3)), row[12][:4], str(datetime.datetime.strptime(row[12][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[12][11:13]+row[12][14:16], format(int(float(row[36])), '02x'), format(int(float(row[41])), '02x'),format(int(float(row[46])), '02x'),format(int(float(row[51])), '02x'),format(int(float(row[56])), '02x'),format(int(float(row[61])), '02x'),format(int(float(row[66])), '02x'),'  '+row[16]+"\n", 
    elif row[12] and row[6] == row[29]:
        print row [1], "{:.3f}".format(round(float(row[13]),3)), "{:.3f}".format(round(float(row[14][1:]),3)), row[12][:4], str(datetime.datetime.strptime(row[12][:-5],'%Y-%m-%dT%H:%M:%S').timetuple().tm_yday).zfill(3), row[12][11:13]+row[12][14:16], format(int(float(row[36])), '02x'), format(int(float(row[41])), '02x'),format(int(float(row[46])), '02x'),'  '+row[16]+"\n",  

f.close()

