#!/bin/bash

# Purpose:
#       Script to run ARGOS_service_data_converter.py for each year file in a directory
#       and output as independant netcdf file

year=2018
path="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/data/year_archive/*.y${year}"
buoyfile="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/scripts/v2_buoy_ids.csv"

for files in $path
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}

	if [[ "$outfile" =~ $(echo ^\($(paste -sd'|' ${buoyfile})\)$) ]]; then
		#version2 buoys
	    echo "processing file: $files"
		python ARGOS_service_data_converter.py ${files} v2 -nc data/${files}.nc
	else
		#metocean buoys - id's listed in a seperate file
	    echo "processing file: $files"
		python ARGOS_service_data_converter.py ${files} v1 -nc data/${files}.nc
	fi

done
