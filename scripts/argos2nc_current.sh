#!/bin/bash

# Purpose:
#       Script to run ARGOS_service_data_converter.py for each file in a directory
#       and output as independant file

year=2018
path="/Volumes/WDC_internal/Users/bell/ecoraid/ArgosDataRetrieval/Archive/${year}/"
#metocean buoys
argosID="122542 136863 136866 136867 136868 136869 148276"

for files in $argosID
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    echo "processing file: $files"
	python ARGOS_service_data_converter.py ${path}${files}.y${year} v1 -nc data/${files}.y${year}.nc
done

#version2 buoys
argosID="145474"

for files in $argosID
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    echo "processing file: $files"
	python ARGOS_service_data_converter.py ${path}${files}.y${year} v2 -nc data/${files}.y${year}.nc
done
