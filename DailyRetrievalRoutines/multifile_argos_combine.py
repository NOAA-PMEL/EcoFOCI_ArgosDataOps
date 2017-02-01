#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed June 16 2015

multiple files are retrieved daily - combine into one daily file

@author: bell
"""

import argparse
import datetime
import os

# parse incoming command line options
parser = argparse.ArgumentParser(description='MultiFile Combine')
parser.add_argument('pathname', metavar='pathname', type=str, help='path to data file')
parser.add_argument('--manual_combine', nargs='+', type=str, help='list files to concat')

args = parser.parse_args()

### list and sort all files in input directory
all_files = [x for x in os.listdir(args.pathname) if x.endswith('.txt') and ('README' not in x) ]
all_files = sorted(all_files)

if not args.manual_combine:
    all_files = all_files[-2:]
else:
    all_files = args.manual_combine

output_file = args.pathname + all_files[0].split('.')[0] + '.txt'
first_file = True

print "Working with {0}".format(all_files)

if not os.path.isfile(output_file) or (os.path.getsize(output_file) == 0):
    print "Saving to {0}".format(output_file)
    with open(output_file, 'w') as outfile:
        for fname in all_files:
            first_line = True
            with open(args.pathname + fname) as infile:
                for line in infile:
                    if first_file:
                        outfile.write(line)
                    else:
                        if first_line:
                            first_line = False
                            continue
                        else:
                            outfile.write(line)
                
            first_file = False
