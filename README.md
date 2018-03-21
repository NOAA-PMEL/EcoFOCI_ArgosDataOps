## Argo Service data acquistion and processing for EcoFOCI

To retrieve and archive data from the Argo service.  Used primarily for drogued drifters and peggy near-realtime wpak data

### Example procedures

**To obtain all data from program 572 (EcoFOCI) since a specified date**

`python getARGO_SOAP.py getCsv -startDate 2018-03-03T00:00:00`

will output csv from the 3rd of march for a default length of one day

`python getARGO_SOAP.py getCsv -startDate 2018-03-03T00:00:00 -recordlength 43200 `

will output csv data from the 3rd of march for half a day

`python getARGO_SOAP.py getCsv`

will output csv data for the entire 24 hours of the last full day (so if you run it at any point on the 5th of March, it will retrieve all of the 4th of March)

################

Legal Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration (NOAA), or the United States Department of Commerce (DOC). All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. Any claims against the DOC or DOC bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation, or favoring by the DOC. The DOC seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by the DOC or the United States Government.