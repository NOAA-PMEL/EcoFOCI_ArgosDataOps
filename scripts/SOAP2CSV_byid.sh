#!/bin/bash

# Purpose:
#       Script to run SOAP2ArchiveCSV.py for each file in a directory
#       and output as concatenated file - only makes year files but not translated 

year=2018
path="/home/pavlof/bell/Programs/Python/EcoFOCI_ArgosDataOps/data/raw_data/"

for files in $argosID
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    echo "processing file: $files"
	python SOAP2ArchiveCSV.py ${path}${files} -drifteryearfiles
done

