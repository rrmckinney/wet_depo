## This script reads in AB PM2.5 Data and converts it to plotable format ##
## Data from: https://airdata.alberta.ca/reporting/Download/OneParameter ##
## Script designed for bsp wet deposition project ##
## Reagan McKinney
## June 2022

import pandas as pd
from datetime import datetime, timedelta
from netCDF4 import Dataset 
import numpy as np



from context import data_dir


def get_ab_obs(file_name, date):
    ## Define Observation files
    obsin = f"{data_dir}/{file_name}"

    ## Define headers in file
    headers = np.linspace(6,16,11)
    headers = [int(x) for x in headers]

    ## Read in observation data
    obsdat = pd.read_csv(obsin, header=headers)

    ## Get datetime information from file 
    filestart = obsdat.iloc[0,0]
    filestart = datetime.strptime(filestart,"%m/%d/%Y %H:%M:%S")-timedelta(hours=1)

    ## Get time of interest to start from 
    date = datetime.strptime(date,"%Y%m%d%H")
    duration = date - filestart
    start = (duration.days)*24
    end = (duration.days+1)*24-1
    dt = filestart = obsdat.iloc[start,0]
    
    print(f"obs start: {filestart}")
    
    ## Read in lat/lon and name from header and save to new dataframe
    names, lats, lons = [], [], []
    for i in range (len(obsdat.columns)-3):
        iname = obsdat.columns[i+3][0][13:]
        ilat = obsdat.columns[i+3][3][17:]
        ilon = obsdat.columns[i+3][4][19:]
        names.append(iname)
        lats.append(ilat)
        lons.append(ilon)

    ## Get pm25 data
    pm25dat = obsdat.iloc[start:end:,2:]
    ## Create cf compliant netcdf output
    obs_ab = Dataset('obs_ab.nc','w',diskless=True)
    site = obs_ab.createDimension('site',len(names))
    time = obs_ab.createDimension('time',23)

    ## Create empty variables to fill with data
    obs_ab.title = "Observational PM2.5 Data from Alberta"
    lat = obs_ab.createVariable('lat',np.float32,('site',))
    lat.units = 'degrees_north'
    lat.long_name = 'latitude'
    lon = obs_ab.createVariable('lon',np.float32,('site',))
    lon.units = "degrees_east"
    lon_long_name = 'longitude'
    time = obs_ab.createVariable('time',np.float32,('time',))
    time.long_name = f"hours since: {dt}"
    pm25 = obs_ab.createVariable('pm25',np.float32,('time','site'))
    pm25.units = 'ug m^-3'
    pm25.standard_name = "particulate matter < 2.5"

    ## write data to empty variables
    
    lat[:] = [float(x) for x in lats]
    lon[:] = [float(x) for x in lons]
    pm25[:] = pm25dat.iloc[:,1:]
     
    print("-- Wrote data, obs shape is now ", pm25.shape)
    print("-- Min/Max values:",np.nanmin( pm25[:]), np.nanmax(pm25[:]))
    
    return obs_ab