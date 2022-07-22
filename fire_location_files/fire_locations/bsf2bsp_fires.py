#!/usr/bin/env python
# coding: utf-8
#
# Script to convert archived BSF fire_locations.csv for use as input to BSP
# Outputs two files: one with the modelled BSF "growth", i.e., persistence included
#                    one without BSF growth, so in this case run BSP WITH the "growth" module

#Rosie Howard
#17 February 2021

import pandas as pd
import datetime as dt

fires = ["2019051909","2019052009","2019052109","2019052209","2019052309","2019052409","2019052509","2019052609","2019052709","2019052809","2019052909","2019053009","2019053109","2019060109","2019060209","2019060309"]
for i in fires:
    # Read in BSF file that needs converting
    df = pd.read_csv(i+'.csv')
    
    # Split date-time string (this way feels convoluted, but it works;
    # It wasn't obvious how to achieve the semicolon
    # in the utcoffset using the '%z' formatting
    
    date_offset = df["date_time"].str.split("-",n=1,expand=True)
    offset = pd.DataFrame(date_offset[1]) #save utoffset in dataframe
        
    dates = pd.to_datetime(date_offset[0]) #convert dates to correct format
    df_dates = pd.DataFrame(index=dates)
    df_dates.index = df_dates.index.map(lambda x: dt.datetime.strftime(x, '%Y-%m-%dT%H:%M:%S.000'))
    df_dates.reset_index(inplace=True)
        
    # Replace date_time column with correct date_time format
    df["date_time"] = df_dates[0] + '-' +offset[1]
        
    #Use the following file if you want to skip "growth" module in BSP and use what was used for BSF operations
    df.to_csv('BSPinput_fire_locations_BSFgrowth.csv',index=False)
        
    #to run fire 'growth' in BSP, remove all but the first instanc of the fire (i.e., get rid of pesistence as modelled by BSF)
    new_df = df.drop_duplicates(subset=['latitude','longitude'])
        
    # Below, does not work because there are some "sets" of dates that begin with a different date
    #first_datetime = df["date_time"][0]
    #new_df = df[df["date_time"] == first_datetime]
        
    #write to file
    # Use the following file if you want to model "growth in BSP and NOT have what was used for BSF operations
    new_df.to_csv(i+'_noBSFgrowth.csv',index=False)

