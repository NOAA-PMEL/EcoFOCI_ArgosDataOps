#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 06:47:44 2018

Purpose:
  Using SOAP protocol to connect to argo service for drifter and weatherpak data access

Usage:
    python getARGO_SOAP getCsv #gets csv files expected by parser routines
    python getARGO_SOAP getKml #gets google earth kml file

Returns:
    previous days data from ARGO soap server as file data/results.{filetype}
    
Author: S.Bell

Note:
    To get an idea of all functions available
    python -mzeep http://ws-argos.clsamerica.com/argosDws/services/DixService?wsdl
"""

import argparse
import zeep
import datetime

# parse incoming command line options
parser = argparse.ArgumentParser(description='Connect to argos.cls SOAP server for FOCI')
parser.add_argument('service', metavar='service', type=str,
                    help='getCsv | getObsCsv | getXml | getKml | getXsd')

args = parser.parse_args()

client = zeep.Client('http://ws-argos.clsamerica.com/argosDws/services/DixService?wsdl')

argodic = {'username':'bparker',
           'password':'invest',
           'programNumber':'572',
           'period':{'startDate':datetime.date.today()-datetime.timedelta(seconds=24*60*60),'endDate':datetime.date.today()},
           'mostRecentPassages':True,
           'showHeader':True,
           'displayLocation':True,
           'displayDiagnostic':True,
           'displaySensor':True}

if args.service in ['getCsv']:
    result = client.service.getCsv(**argodic)
    filetype = 'csv'

if args.service in ['getObsCsv']:
    subkeys = ('username', 'password', 'programNumber','period')
    subdict = {x: argodic[x] for x in subkeys if x in argodic}

    result = client.service.getObsCsv(**subdict)
    filetype = 'obs.csv'

    
if args.service in ['getXml']:
    subkeys = ('username', 'password', 'programNumber','period',
               'displayLocation','displayDiagnostic','displaySensor')
    subdict = {x: argodic[x] for x in subkeys if x in argodic}

    result = client.service.getXml(**subdict)
    filetype = 'xml'

if args.service in ['getKml']:
    subkeys = ('username', 'password', 'programNumber','period')
    subdict = {x: argodic[x] for x in subkeys if x in argodic}

    result = client.service.getKml(**subdict)
    filetype = 'kml'

datetime.date.today().strftime('%Y%m%d')
with open("data/" + ".".join(['ARGO_'+datestr,filetype]), 'w') as f:
    f.write(result)