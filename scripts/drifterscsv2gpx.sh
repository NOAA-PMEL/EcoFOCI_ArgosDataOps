#!/bin/bash

# Purpose:
#       Script to run SCS_shptrack2gpx.py for each file in a directory
#       and output as independant files per day

cruiseyear='2015'

data_dir="/Volumes/WDC_internal/Users/bell/ecoraid/ArgosDataRetrieval/Archive/${cruiseyear}/*"
prog_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_ArgosDataOps/"
out_dir="/Volumes/WDC_internal/Users/bell/scratch/drifters/${cruiseyear}/"

for files in $data_dir
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    echo "processing file: $files"
    python ${prog_dir}ARGOcsv2gpx.py -i ${files}  >> ${out_dir}${outfile}.gpx
done
