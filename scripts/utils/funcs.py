## Functions for wet deposition project plotting ##
## (1) read in hysplit ncataset and make it cf compliant
## (2) define a title for plots depending on case study
## (3) plot map and newly formatted hourly bsp hysplit output
## (4) plot daily summed bsp hysplit output on map
## Reagan McKinney ##
## June 2022 ##

import pandas as pd
from datetime import datetime, timedelta
from netCDF4 import Dataset 
import numpy as np
import matplotlib.pyplot as plt
import cartopy.feature as cf
from cartopy.io.shapereader import Reader
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

def wdcompliant(filein):
    """

        Converts Hysplit dataset to be cf compliant.

        Also, reformats julian datatime to standard datetime and creates LAT LONG arrays of the model domain.

    """
    # read in dataset
    nc = Dataset(filein)

    # get pm2.5 data 
    pm25dat = nc.variables['PM25'][:] 

    # get time flags 
    tflag = nc.variables["TFLAG"][0:-1]

    # get first time index *only works for 00Z initialization
    hysplit_start = str(tflag[0,0,0])+"0"+str(tflag[0,0,1])

    # convert from julian datetime to standard datetime
    start = datetime.strptime(hysplit_start,"%Y%j%H%M%S").strftime("%Y%m%d%H%M%S")
    print(f"start: {start}")

    # get last time index  and convert from julian to standard datetime with if statement
    hysplit_stop = str(tflag[-1,0,0])+str(tflag[-1,0,1])

    if len(hysplit_stop)<13:
        stop = datetime.strptime(hysplit_stop,"%Y%j%H").strftime("%Y%m%d%H%M%S")
    else:
        stop = datetime.strptime(hysplit_stop,"%Y%j%H%M%S").strftime("%Y%m%d%H%M%S")
    print(f"stop: {stop}")

    # create new datetime numpy array wih one hour frequency
    date_range = pd.date_range(start,stop,freq="1H")

    # get x corrdinate dimensions and create an array
    xnum = len(nc.dimensions["COL"])
    dx = nc.getncattr("XCELL")
    xorig = nc.getncattr("XORIG")
    x = np.arange(0,xnum)

    # get y corrdinate dimensions and create an array
    ynum = len(nc.dimensions["ROW"])
    dy = nc.getncattr("XCELL")
    yorig = nc.getncattr("YORIG")
    y = np.arange(0,ynum)

    # create lat/long 2D arrays based on x,y coordinate
    X = np.arange(0,xnum)*dx+xorig
    Y = np.arange(0,ynum)*dy+yorig

    # get z coordinate dimensions and create an array
    Z = np.array(nc.getncattr("VGLVLS")[:-1])
    z = np.arange(0,len(Z))

    # create new CF compliant dataset 
    #create empty dataset with preferred dimensions
    nc_cf = Dataset('nc_cf.nc',  'w', diskless = True)
    lat = nc_cf.createDimension('lat',ynum)
    lon= nc_cf.createDimension('lon',xnum)
    alt = nc_cf.createDimension('alt',len(Z))
    time = nc_cf.createDimension('time',None)

    # create empty variables to fill with data
    nc_cf.title = 'Bluesky Canada WD PM25 Forecast'
    lat = nc_cf.createVariable('lat',np.float32,('lat',))
    lat.units = 'degrees_north'
    lat.long_name = 'latitude'
    lon = nc_cf.createVariable('lon',np.float32,('lon',))
    lon.units = "degrees_east"
    lon_long_name = 'longitude'
    alt = nc_cf.createVariable('alt',np.float32,('alt',))
    time = nc_cf.createVariable('time','S10',('time',))
    time_units = f"hours since: {start}"
    time.long_name = "time"
    pm25 = nc_cf.createVariable('pm25',np.float32,('time','lat','lon', 'alt'))
    pm25.units = 'ug m^-3'
    pm25.standard_name = "particulate matter < 2.5"

    #write data to empty variables *assumes 24hr forecasts only!
    ntimes = 24

    lat[:] = Y
    lon[:] = X
    start = datetime.strptime(start,"%Y%m%d%H%M%S") - timedelta(hours=1)
    for b in range(ntimes):
        time[b] = str(start)
        start = start + timedelta(hours=1)
    alt[:] = Z
    pm25[:,:,:,:] = pm25dat

    print("-- Wrote data, pm25.shape is now ", pm25.shape)
    print("-- Min/Max values:", pm25[:,:,:,:].min(), pm25[:,:,:,:].max())

    return nc_cf

## set title of plot based on casestudy chosen 
def get_title(scheme):
    if scheme == "":                  
        scheme = "Control"
    elif scheme == "wdwet8":
        scheme = "Hysplit Default"
    elif scheme == "wdNAME":
        scheme = "NAME experiment"
    return scheme

## Plot the cf compliant netcdf data on a map - i defines the forecast hour
def plot_func(nc,i, plot_extent,fig,lons,lats):
    var = np.squeeze(nc.variables["pm25"][:])[i,:,:]             ## read in pm25 data for each hour
    ax = fig.add_subplot(6,4,i+1,projection=ccrs.PlateCarree())
    ## line where plotting of pm25 data happens for each hour
    im = ax.contourf(lons,lats,var,levels = 100,zorder=-1,cmap='gist_heat_r')   ## set colormap as "im" variable so can define global colorbar later
    ax.add_feature(cf.BORDERS,linewidth=0.5)                     ## plot international borders
    ax.add_feature(cf.COASTLINE, linewidth=0.5)                  ## plot coastlines
    provs = cf.NaturalEarthFeature(                              ## read in provincial boundaries
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='50m',
            facecolor='none')
 
    ax.autoscale(False)
    ax.add_feature(provs, linewidth = 0.5)                      ## plot in provincial boundaries
    ax.set_extent(plot_extent)                                  ## set plot boundary to zoom in on smoke 
    # ax.set_aspect('equal')                                      ## make plot pretty
    plt.title(f"Time: {i+1}:00:00")                             ## set title as forecats time
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,   ## the next "gl" lines create the lat/lon grid on the plots
        linewidth=0.5, color='gray', alpha=1, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_left = False
    gl.xlines = True
    gl.xlocator = mticker.FixedLocator([-120, -115])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 8, 'color': 'gray'}
    gl.ylabel_style = {'size': 8, 'color': 'gray'}
    return im

# Plot the cf compliant netcdf daily data on a map 
def plot_day(ncpm,i,date, plot_extent,fig,lons,lats):
    var = ncpm          ## read in pm25 data for each hour
    ax = fig.add_subplot(6,4,i+1,projection=ccrs.PlateCarree())
    ## line where plotting of pm25 data happens for each hour
    im = ax.contourf(lons,lats,var,levels = 100,zorder=-1,cmap='gist_heat_r')   ## set colormap as "im" variable so can define global colorbar later
    ax.add_feature(cf.BORDERS,linewidth=0.5)                     ## plot international borders
    ax.add_feature(cf.COASTLINE, linewidth=0.5)                  ## plot coastlines
    provs = cf.NaturalEarthFeature(                              ## read in provincial boundaries
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='50m',
            facecolor='none')
 
    ax.autoscale(False)
    ax.add_feature(provs, linewidth = 0.5)                      ## plot in provincial boundaries
    ax.set_extent(plot_extent)                                  ## set plot boundary to zoom in on smoke 
    # ax.set_aspect('equal')                                      ## make plot pretty
    plt.title(f"{date}")                             ## set title as forecats time
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,   ## the next "gl" lines create the lat/lon grid on the plots
        linewidth=0.5, color='gray', alpha=1, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_left = False
    gl.xlines = True
    gl.xlocator = mticker.FixedLocator([-120, -115])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 8, 'color': 'gray'}
    gl.ylabel_style = {'size': 8, 'color': 'gray'}
    return im