"""
 ARGOcsv2gpx.py

 History:
 --------

"""

#System Stack
import datetime
import argparse

#science stack
import pandas as pd

#User Stack
from io_utils import ConfigParserLocal


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2017, 04, 12)
__modified__ = datetime.datetime(2017, 04, 12)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'gpx', 'shiptrack'


"""------------------------------- MAIN------------------------------------------------"""

parser = argparse.ArgumentParser(description='Convert Argo id.yyyy csv to .gpx files')
parser.add_argument('-i','--input', type=str, help='path to data files')
parser.add_argument('-o','--output', type=str, help='path to save files')

args = parser.parse_args()

print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<gpx version=\"1.0\" creator=\"nmea_conv\"\nxmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns=\"http://www.topografix.com/GPX/1/0\"\nxsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd\">\n")
if args.input:
	print("<trk>")
	print("<name>{0}</name>").format(args.input)
	print("<trkseg>")
	data = pd.read_csv(args.input, header=None, sep='\s+',dtype=str, error_bad_lines=False)
	for i, row in data.iterrows():
		lat = row[1]
		if float(row[2]) > 0:
			lon = -180. - (180 - float(row[2]))
		else:
			lon = row[2]
		timestamp = (pd.to_datetime(row[3]+' '+row[4]+' '+row[5], format='%Y %j %H%M')).to_pydatetime().isoformat()
		print('<trkpt lat="{lat}" lon="{lon}"><ele>0.0</ele><time>{time}Z</time></trkpt>').format(lat=lat,lon=lon,time=timestamp)

print("</trkseg>\n</trk>\n</gpx>\n")