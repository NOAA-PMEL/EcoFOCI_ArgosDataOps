# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 06:47:44 2018

Purpose:
  Format results from soap call to clean "traditional" csv archival format.
  Currently only processes csv returned files

"""

import argparse
import pandas as pd
import numpy as np
import datetime

# parse incoming command line options
parser = argparse.ArgumentParser(description='Format ARGOS Soap retrieved files')
parser.add_argument('infile', 
    metavar='infile', 
    type=str,
    help='full path to infile')
parser.add_argument('outfile', 
    metavar='outfile', 
    type=str,
    help='full path to outfile: use pattern - platformId.y{{year}} ')
parser.add_argument('-getactiveids', '--getactiveids',
    action="store_true", 
    help='get active listing of platformIds')
parser.add_argument('-buoyyearfiles', '--buoyyearfiles',
    action="store_true", 
    help='create buoy year files - 28882')
parser.add_argument('-drifteryearfiles', '--drifteryearfiles',
    action="store_true", 
    help='create all drifter year files from activeid listing')

args = parser.parse_args()

df = pd.read_csv(args.infile,sep=';',index_col=False,dtype=object,error_bad_lines=False)


if args.getactiveids:
    gb = df.groupby('platformId')
    print(gb.groups.keys())

if args.buoyyearfiles:
    gb = df.groupby('platformId')

    keep_columns=['platformId','latitude','longitude','bestDate','value'] + ['value.'+str(i) for i in range(1,32)] + ['locationClass']
    try:
      bd = gb.get_group('28882')

      bd_thinned = bd[keep_columns].copy()
      bd_thinned['year'] = bd_thinned.apply(lambda row: str(pd.to_datetime(row['bestDate']).year), axis=1)
      bd_thinned['doy'] = bd_thinned.apply(lambda row: str(pd.to_datetime(row['bestDate']).dayofyear), axis=1)
      bd_thinned['hhmm'] = bd_thinned.apply(lambda row: str(pd.to_datetime(row['bestDate']).hour).zfill(2)+str(pd.to_datetime(row['bestDate']).minute).zfill(2), axis=1)

      out_columns=['platformId','latitude','longitude','year','doy','hhmm','value'] + ['value.'+str(i) for i in range(1,32)] + ['locationClass']
      bd_thinned[out_columns].to_csv(args.outfile,' ',header=False,index=False,na_rep=np.nan,mode='a')
    except:
      print("no 28882 data in this file")


if args.drifteryearfiles:
    gb = df.groupby('platformId')

    keep_columns=['platformId','latitude','longitude','locationDate','value'] + ['value.'+str(i) for i in range(1,7)] + ['locationClass']

    for k in gb.groups.keys():
      if k not in ['28882']:
        print k
        bd = gb.get_group(k)
        bd_thinned = bd[keep_columns].copy()
        bd_thinned['year'] = bd_thinned.apply(lambda row: str(pd.to_datetime(row['locationDate']).year), axis=1)
        bd_thinned['doy'] = bd_thinned.apply(lambda row: str(pd.to_datetime(row['locationDate']).dayofyear), axis=1)
        bd_thinned['hhmm'] = bd_thinned.apply(lambda row: str(pd.to_datetime(row['locationDate']).hour).zfill(2)+str(pd.to_datetime(row['locationDate']).minute).zfill(2), axis=1)

        out_columns=['platformId','latitude','longitude','year','doy','hhmm','value'] + ['value.'+str(i) for i in range(1,7)] + ['locationClass']
        bd_thinned[out_columns].dropna().to_csv(args.outfile + k + '.y2018',' ',header=False,index=False,na_rep=np.nan,mode='a')
