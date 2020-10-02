"""
Purpose:
  Using SOAP protocol to connect to argo service for drifter and weatherpak data access

Usage:
    python getARGO_SOAP getCsv #gets csv files expected by parser routines
    python getARGO_SOAP getKml #gets google earth kml file

Returns:
    previous days data from ARGO soap server as file data/results.{filetype}
    
Author: S.Bell

History:
  2018-03-14: Make it so either the program number or platform id can be submitted

Note:
    To get an idea of all functions available
    python -mzeep http://ws-argos.clsamerica.com/argosDws/services/DixService?wsdl
"""

import argparse
import datetime
import zeep

# parse incoming command line options
parser = argparse.ArgumentParser(description='Connect to argos.cls SOAP server for FOCI')
parser.add_argument('service', 
    metavar='service', 
    type=str,
    help='getCsv | getObsCsv | getXml | getKml | getXsd')
parser.add_argument('-idMode','--idMode',
    type=str,
    default='programNumber',
    help='programNumber | platformId')
parser.add_argument('-idnumber', '--idnumber',
    type=str,
    default='572',
    help='programNumber: or platformId number desired')
parser.add_argument('-startDate','--startDate',
    type=str,
    default='today',
    help='startDate for retrieval in yyyy-mm-ddThh:mm:ss')
parser.add_argument('-recordlength','--recordlength',
    type=int,
    default=86400,
    help='length of records to retrieve in seconds (default is 86400)')

args = parser.parse_args()

client = zeep.Client('http://ws-argos.clsamerica.com/argosDws/services/DixService?wsdl')

if args.startDate:
  if args.startDate in ['today']:
    startDate = datetime.date.today()-datetime.timedelta(seconds=24*60*60)
    endDate   = datetime.date.today()
  else:
    startDate = datetime.datetime.strptime(args.startDate,'%Y-%m-%dT%H:%M:%S')
    endDate   = startDate + datetime.timedelta(seconds=args.recordlength) 

argodic = {'username':'bparker',
           'password':'invest',
           args.idMode:args.idnumber,
           'period':{'startDate':startDate,'endDate':endDate},
           'mostRecentPassages':True,
           'showHeader':True,
           'displayLocation':True,
           'displayDiagnostic':True,
           'displaySensor':True}

if args.service in ['getCsv']:
    result = client.service.getCsv(**argodic)
    filetype = 'csv'

if args.service in ['getObsCsv']:
    subkeys = ('username', 'password', args.idMode,'period')
    subdict = {x: argodic[x] for x in subkeys if x in argodic}

    result = client.service.getObsCsv(**subdict)
    filetype = 'obs.csv'

    
if args.service in ['getXml']:
    subkeys = ('username', 'password', args.idMode,'period',
               'displayLocation','displayDiagnostic','displaySensor')
    subdict = {x: argodic[x] for x in subkeys if x in argodic}

    result = client.service.getXml(**subdict)
    filetype = 'xml'

if args.service in ['getKml']:
    subkeys = ('username', 'password', args.idMode,'period')
    subdict = {x: argodic[x] for x in subkeys if x in argodic}

    result = client.service.getKml(**subdict)
    filetype = 'kml'

datestr = startDate.strftime('%Y%m%d%H%M%S')+'_'+endDate.strftime('%Y%m%d%H%M%S')
if args.idMode in ['programNumber']:
    with open("data/" + ".".join(['ARGO_'+datestr,filetype]), 'w') as f:
      f.write(result)
elif args.idMode in ['platformId']:
    with open("data/" + ".".join(['ARGO_'+args.idnumber+'_'+datestr,filetype]), 'w') as f:
      f.write(result)
else:
    print("No file written")  