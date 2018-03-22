#!/bin/bash

# Purpose:
#   Script to run ARGOS_service_data_converter.py to retrieve a daily file
#     for the last 20 days (maximum retrieval length).

for i in {0..20}
do
  #startDate="$(date +"%Y-%m-%dT00:00:00" -d "$i day ago")"
  #*nix format
  startDate="$(-v-${i}d  +"%Y-%m-%dT00:00:00")"
  echo "Grabbing $startDate"
  python getARGO_SOAP.py getCsv -startDate $startDate
done