#!/bin/bash

# Purpose:
#       Script to run ARGOS_service_data_converter.py for each year file in a directory
#       and output as independant netcdf file

year=2018
path="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/data/year_archive/"

for files in $path
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}

	if [[ "$outfile" =~ $(echo ^\($(paste -sd'|' ${path}/scripts/v2_buoy_ids.csv)\)$) ]]; then
		#version2 buoys
	    echo "processing file: $files"
		python ARGOS_service_data_converter.py ${path}${files}.y${year} v2 -nc data/${files}.y${year}.nc
	else
		#metocean buoys
	    echo "processing file: $files"
		python ARGOS_service_data_converter.py ${path}${files}.y${year} v1 -nc data/${files}.y${year}.nc
	fi

done
