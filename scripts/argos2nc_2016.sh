#!/bin/bash

# Purpose:
#       Script to run ARGOS_service_data_converter.py for each file in a directory
#       and output as independant file

year=2016
path="/Volumes/WDC_internal/Users/bell/ecoraid/ArgosDataRetrieval/Archive/${year}/"
#metocean buoys
argosID="122537 122540 122541 122542 136860 136861 136863 \
136864 136865 136866 136867 136868 136869 136872 136873 \
136874 148276 148277 148279 151636"

for files in $argosID
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    echo "processing file: $files"
	python ARGOS_service_data_converter.py ${path}${files}.y${year} v1 -nc data/${files}.y${year}.nc
done

