#!/bin/bash

# Purpose:
#       Script to run SOAP2ArchiveCSV.py for each file in a directory
#       and output as independant file
# merge files together later with a cat... use pandas to remove duplicates

year=2018
path="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/"
files="data/raw_data/*.csv"
#metocean buoys
#['148276', '136863', '145474', '122531', '136868', '136866', '136867', '28882']
argosID="148276 136863 122531 136868 136866 136867"

: '
for files in $argosID
for id in $argosID
do
   	for fid in ${path}${files}
   	do
	    echo "processing file: ${id} - ${fid}"
		python SOAP2ArchiveCSV.py ${fid} --drifteryearfiles ${path}data/${files}.${id}.y${year} 
	done
done
#version2 buoys
argosID="145474"

for files in $argosID
for id in $argosID
do
   	for fid in ${path}${files}
   	do
	    echo "processing file: ${id} - ${fid}"
		python SOAP2ArchiveCSV.py ${fid} --drifteryearfiles ${path}data/${files}.${id}.y${year} 
	done
done
'
#Mooring/Peggy Buoy
argosID="028882"

for id in $argosID
do
   	for fid in ${path}${files}
   	do
	    echo "processing file: ${id} - ${fid}"
		python SOAP2ArchiveCSV.py ${fid} --buoyyearid ${path}data/${files}.${id}.y${year} 
	done
done
