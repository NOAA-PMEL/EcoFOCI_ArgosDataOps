#!/usr/bin/env

"""
yearly2json.py

 convert yearly {argosid.year} files to geojson format
  
"""

#System Stack
import json
import argparse
import datetime

#Science Stack
import pandas as pd

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2010, 03, 14)
__modified__ = datetime.datetime(2016, 03, 14)
__version__  = "1.0.0"
__status__   = "Development"

"----------------------------------------------------------------------------------------"

parser = argparse.ArgumentParser(description='example processing')
parser.add_argument('DataPath', metavar='DataPath', type=str, help='full path to file')
parser.add_argument('ArgosID', metavar='ArgosID', type=str, help='ArgosID number')
args = parser.parse_args()

data = pd.read_csv(args.DataPath,'\t',header=None,\
	names=['ArgosID','Lat','Lon','Year','DOY','hhmm','s1','s2','s3','s4','s5','s6','s7','s8'])

"""
GeoJSON format example:
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [102.0, 0.6]
      },
      "properties": {
        "prop0": "value0"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]
        ]
      },
      "properties": {
        "prop1": 0.0,
        "prop0": "value0"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
            [100.0, 0.0]
          ]
        ]
      },
      "properties": {
        "prop1": {
          "this": "that"
        },
        "prop0": "value0"
      }
    }
  ]
}"""

print "Generating .geojson as multipoint collection"
geojson_header = (
    '{\n'
    '"type": "FeatureCollection",\n'
    '"features": [\n'
    )
geojson_Features_pt1 = ((
    '{{\n'
    '"type": "Feature",\n'
    '"id": {0},\n'
    '"geometry": {{\n'
    '"type": "MultiPoint",\n'
    '"coordinates": [').format(args.ArgosID))

geojson_positions = ''

for i,r in data.iterrows():
	geojson_positions = geojson_positions + ('[{1},{0}],').format(r['Lat'],r['Lon'])

geojson_Features_pt2 = ((
    ']}},\n'
    '"properties": {{\n'
    '"ArgosID": "{0}"'
    '}}\n').format(args.ArgosID))
    
geojson_Features_pt2 = geojson_Features_pt2 + '}\n, '

geojson_tail = (
    '}\n'
    ']\n'
    '}\n'
    )
  
fid = open('data/' + args.ArgosID + '.geo.json', 'wb')
fid.write( geojson_header + geojson_Features_pt1 + geojson_positions + geojson_Features_pt2 + geojson_tail )
fid.close()