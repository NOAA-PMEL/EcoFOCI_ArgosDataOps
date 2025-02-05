# Argo Service data acquistion and processing for EcoFOCI

To retrieve and archive data from the Argo service.  Used primarily for drogued drifters and peggy near-realtime wpak data

***Note: Currently Plots are Broken as basemap needs to be upgraded to cartopy***

***Written/Tested for:***

- python >=3.8 **tested**
- currently Basemap is deprecated and conversion to cartopy for plots is in progress

## Example procedures

**To obtain all data from program 572 (EcoFOCI) since a specified date**

`python getARGO_SOAP.py getCsv -startDate 2018-03-03T00:00:00`

will output csv from the 3rd of march for a default length of one day

`python getARGO_SOAP.py getCsv -startDate 2018-03-03T00:00:00 -recordlength 43200`

will output csv data from the 3rd of march for half a day

`python getARGO_SOAP.py getCsv`

will output csv data for the entire 24 hours of the last full day (so if you run it at any point on the 5th of March, it will retrieve all of the 4th of March)

## Convert Soap Retrievals to Archive Format

From csv files obtaind via getARGO_SOAP.py there are two pathways:
- clean and archive.  Using SOAP2ArchiveCSV.py you can generate clean csv files for archive and later usage.  No hex conversion has happened at this point, just removal of unnecessary head/column id's and partitioning of data into files based on argo transmitter id.
- process and convert.  Using ARGOS_service_data_converter.py will allow the various types of datastreams to have their hex information converted into science values.

## Additional Routines
- ARGOcsv2gpx.py takes the SOAP2ArchiveCSV.py csv files and creates gpx files for GIS software
- ARGOS_service_data_converter.py -nc will make netcdf files of the SOAP2ArchiveCSV.py - builds yearly csv files (or yearly files like Kachel and Benny's old routine).  This routine appends to existing text by default.

***There is no routine that converts raw SOAP data straight to usable output***


## Notes About Argos Location Classes
Taken from the Argos website:  [https://www.argos-system.org/support-and-help/faq-localisation-argos/](https://www.argos-system.org/support-and-help/faq-localisation-argos/)

Description of Location Classes:
-classes 0, 1, 2, 3 indicate that the location was obtained with 4 messages or more and provides the accuracy estimation,
-class A indicates that the location was obtained with 3 messages,
-class B indicates that the location was obtained with 2 messages,
-class G indicates that the location is a GPS fix obtained by a GPS receiver attached to the platform. The accuracy is better than 100 meters.
-class Z indicates that the location process failed.

Accurace of Doppler Locations:

-Class 3: better than 250 m radius
-Class 2: better than 500 m radius
-Class 1: better than 1500 m radius
-Class 0: over 1500 m radius

################

Legal Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration (NOAA),
or the United States Department of Commerce (DOC). All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use.
Any claims against the DOC or DOC bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law.
Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise,
does not constitute or imply their endorsement, recommendation, or favoring by the DOC. The DOC seal and logo, or the seal and logo of a DOC bureau,
shall not be used in any manner to imply endorsement of any commercial product or activity by the DOC or the United States Government.
