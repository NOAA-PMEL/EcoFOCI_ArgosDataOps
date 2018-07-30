#!/bin/bash

# Purpose:
#       Script to run SOAP2ArchiveCSV.py for each file in a directory
#       and output as concatenated file - only makes year files but not translated 

year=2018
path="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/data/*.csv"
progdir="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/"

for files in $path
do
    echo "processing file: $files"
	python ${progdir}SOAP2ArchiveCSV.py ${files} -drifteryearfiles
done

