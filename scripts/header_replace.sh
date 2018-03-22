#!/bin/bash

# Purpose:
#   Replace header line in every file with longest possible

header='"programNumber";"platformId";"platformType";"platformModel";"platformName";"satellite";"bestMsgDate";"duration";"nbMessage";"message120";"bestLevel";"frequency";"locationDate";"latitude";"longitude";"altitude";"locationClass";"gpsSpeed";"gpsHeading";"index";"nopc";"errorRadius";"semiMajor";"semiMinor";"orientation";"hdop";"bestDate";"compression";"formatOrder";"formatName";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr";"order";"name";"valueType";"value";"valueStr"'

for i in `ls -1`
do
  sed -i '' -e "1s/.*/${header}/" $i
done

