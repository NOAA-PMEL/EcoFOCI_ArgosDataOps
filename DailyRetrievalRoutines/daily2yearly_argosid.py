#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed June 16 2015

multiple files are retrieved daily - combine into one daily file

@author: bell
"""

import argparse
import os

# parse incoming command line options
parser = argparse.ArgumentParser(description='Create Yearly files for each ID from daily files')
parser.add_argument('-i','--input_path', metavar='input_path', type=str, help='path to data file')
parser.add_argument('-o','--output_path', metavar='output_path', type=str, help='output path to data file')
parser.add_argument('-y','--year',metavar='year', type=str, help='year to concatenate')

args = parser.parse_args()

### list and sort all files in input directory
all_files = [x for x in os.listdir(args.input_path) if x.endswith('.txt') and (args.year in x) ]
all_files = sorted(all_files)

argosID = {}
for onefile in all_files:
    argosID[onefile.split('_')[1]] = onefile.split('_')[1]+'.y'+args.year
    
for uniqueID in argosID.keys():
    print "Seeking and concatenating ArgosID: {0}".format(uniqueID)    
    oneIDfiles = [x for x in all_files if (uniqueID in x)]

    output_file = args.output_path + argosID[uniqueID]
    print "Outputting to {0}".format(output_file)

    if not os.path.isfile(output_file) or (os.path.getsize(output_file) == 0):

        with open(output_file, 'w') as outfile:
            for fname in oneIDfiles:
                with open(args.input_path + fname) as infile:
                    for line in infile:
                        outfile.write(line)
                
