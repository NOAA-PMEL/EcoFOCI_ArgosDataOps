#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

import argparse
import os

# parse incoming command line options
parser = argparse.ArgumentParser(description='parse DailyArgosMessage into daily id files')
parser.add_argument('pathname', metavar='pathname', type=str, help='path to .nc file')
parser.add_argument('-all','--all', action="store_true", help='translate all files')
parser.add_argument('-last_n','--last_n', metavar='last_n', type=int, help='translate last {n} files')

args = parser.parse_args()

#get a list of all files to cycle through
all_files = [x for x in os.listdir(args.pathname) if x.endswith('.txt')]
all_files = sorted(all_files)

# only use last file if all files is notspecified
if args.all:
    all_files = all_files
elif args.last_n:
    all_files = all_files[-args.last_n:]
else:
    all_files = [all_files[-1],]

#open file, look for unique id's and write a file for each id
for file_name in all_files:
    d = {}
    id_list = {}
    counter = 0
    with open(args.pathname + file_name) as f:
        for line in f:
            id_list[line.split()[0]] = ''
            d[counter] = {line.split()[0]: line.split()[1:]}
            counter +=1
    
    print "Argos Id's found in file:"
    for ArgosID in id_list.keys():
        print ArgosID
        of = open('DailyArgosMessage_' + ArgosID + '_' + file_name.split('_')[-1],'w')
        for value in d.values():
            if value.keys()[0] == ArgosID:
                print >>of, "\t".join(value.keys() + value.values()[0])
        of.close()
        
