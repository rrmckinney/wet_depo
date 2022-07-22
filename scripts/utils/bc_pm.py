## This script reads in BC PM2.5 Data and converts it to plotable format ##
## BC data found at: https://envistaweb.env.gov.bc.ca/ ##
## *Script designed for bsp wet deposition project ##
## Reagan McKinney
## June 2022


import pandas as pd
from datetime import datetime, timedelta
from netCDF4 import Dataset 
import numpy as np


from context import bc_dir

def get_bc_obs(date):
    ## Define Observation files
    obsin = f"{bc_dir}/bc_obc_{date}.csv"
    latlonin = f"{bc_dir}/bc_lat_lon.csv"

    ## Read in observation data
    obsdat = pd.read_csv(obsin)
    latlon = pd.read_csv(latlonin)

    ## Get datetime information from file 
    filestart = obsdat.iloc[3,0]+" "+obsdat.iloc[3,1]
    filestart = datetime.strptime(filestart,"%m/%d/%Y %H:%M AM")-timedelta(hours=1)

    print(f"obs start: {filestart}")

    ## Read in lat/lon and name from header and save to new dataframe
    names, lats, lons = [], [], []
    for i in range (len(obsdat.columns)-3):
        iname = obsdat.iloc[0][i+2]
        ilat = latlon.iloc[i+1,1]
        ilon = latlon.iloc[i+1,2]
        names.append(iname)
        lats.append(ilat)
        lons.append(ilon)

    ## Get pm25 data
    pm25dat = obsdat.iloc[3:26,3:]
  
    ## Create cf compliant netcdf output
    obs_bc = Dataset('obs_bc.nc','w',diskless=True)
    site = obs_bc.createDimension('site',len(names))
    time = obs_bc.createDimension('time',23)

    ## Create empty variables to fill with data
    obs_bc.title = "Observational PM2.5 Data from British Columbia"
    lat = obs_bc.createVariable('lat',np.float32,('site',))
    lat.units = 'degrees_north'
    lat.long_name = 'latitude'
    lon = obs_bc.createVariable('lon',np.float32,('site',))
    lon.units = "degrees_east"
    lon_long_name = 'longitude'
    time = obs_bc.createVariable('time',np.float32,('time',))
    time.long_name = f"hours since: {date}"
    pm25 = obs_bc.createVariable('pm25',np.float32,('time','site'))
    pm25.units = 'ug m^-3'
    pm25.standard_name = "particulate matter < 2.5"

    ## write data to empty variables

    lat[:] = [float(x) for x in lats]
    lon[:] = [float(x) for x in lons]
    pm25[:] = pm25dat
        
    print("-- Wrote data, obs shape is now ", pm25.shape)
    print("-- Min/Max values:",np.nanmin( pm25[:]), np.nanmax(pm25[:]))

    return obs_bc