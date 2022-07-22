#!/bin/bash

# Script to plot all dates for wet deposition case studies
#
# Reagan McKinney
# 30 May 2022
DATE="20190519" #start of case study
LEN = 7 #length of case study

for i in {1..16} # currently works for all 2019 case studies
do 

    python3 wd_daily.py $DATE $LEN

    DATE=$(DATE -j -v +1d -f "%Y%m%d" $DATE +%Y%m%d)
    echo "nextdate = $DATE"
        
done
exit