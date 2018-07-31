#!/bin/bash

# Purpose:
#       Script to run ARGOS_service_data_converter.py for each year file in a directory
#       and output as independant netcdf file
#
# Be sure to use an appropriate environment (ARGODrifters-py36 or ARGODrifters)

year=2018
path="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/data/year_archive/*.y${year}"
v2file="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/scripts/v2_buoy_ids.csv"
buoyfile="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/scripts/mooring_ids.csv"

for files in $path
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    echo $outfile
    if [ -s ${files} ]; then
		if [[ "$outfile" =~ $(echo ^\($(paste -sd'|' ${v2file})\)$) ]]; then
			#version2 buoys - id's listed in a seperate file
		    echo "processing v2 drifter file: $files"
			python ARGOS_service_data_converter.py ${files} v2 -nc data/${outfile}.nc
		elif [[ "$outfile" =~ $(echo ^\($(paste -sd'|' ${buoyfile})\)$) ]]; then
			#buoy - id's listed in a seperate file
		    echo "processing mooring buoy file: $files"
			#python ARGOS_service_data_converter.py ${files} buoy -nc data/${outfile}.nc
		else
			#metocean buoys 
		    echo "processing v1(metocean) drifter file: $files"
			python ARGOS_service_data_converter.py ${files} v1 -nc data/${outfile}.nc
		fi
	fi
done
