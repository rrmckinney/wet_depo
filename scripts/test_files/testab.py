## %

## Script to read in bsp hysplit output and make it into pretty maps ##
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
import warnings

from utils.funcs import plot_func, get_title
from utils.ab_pm import get_ab_obs
from context import img_dir, data_dir

warnings.filterwarnings("ignore")
### User Inputs ###
case_study = "" #choice of ""(control),"wdwet8"(8e-5),"wdNAME"(8.4e-5,0.00036) - will define input file
date = "20190601" #forecast date of interest - will define inout file
plot_extent = [-125,-109.99,54,60] #set bounds for plot dependant on region(s) of interest
ab_obs_file = "station_obs_ab_052019-062019.csv" #observational dataset
###################

## Run through functions that makes raw bsp output and obs cf compliant and ready for plotting
ab_obs_in = get_ab_obs(ab_obs_file, f"{date}00")

## Get Alberta observational data from newly created cf dataset
lats = np.squeeze(ab_obs_in.variables['lat'][:])
lons = np.squeeze(ab_obs_in.variables['lon'][:])
pm25 = np.squeeze(ab_obs_in.variables["pm25"][:])

## Setup figure
fig = plt.figure(figsize=(24,18))
for i in range(23):
    ax = fig.add_subplot(6,4,i+1,projection=ccrs.PlateCarree())
    ## Plot a subpot for all 23 hours of the forecast
    plt.scatter(lons,lats, c=pm25[i], alpha=1,s=4,cmap='hot_r',transform=ccrs.PlateCarree())
    ax.add_feature(cf.BORDERS,linewidth=0.5)                     ## plot international borders
    ax.add_feature(cf.COASTLINE, linewidth=0.5)                  ## plot coastlines
    provs = cf.NaturalEarthFeature(                              ## read in provincial boundaries
                category='cultural',
                name='admin_1_states_provinces_lines',
                scale='50m',
                facecolor='none')
    ax.add_feature(provs, linewidth = 0.5)
    ax.set_extent(plot_extent)                                  ## set plot boundary to zoom in on smoke 
  
plt.subplots_adjust(left=0.125,                                 ## make plot pretty
                    bottom=0.1, 
                    right=1, 
                    top=0.99, 
                    wspace=0.1, 
                    hspace=0)

case_name = get_title(case_study)                               ## set plot title to nice formatting

fig.text(0.9,0.1,f"Bluesky WD PM25 Forecast - {date} - {case_name}")   ## set plot identifier - states date and case study of interest in bottom right corner

plt.savefig(                                                            ## save plot as .png named after date and case study 
    str(img_dir)+ f"/wd-obs-{date}-{case_name}.png", bbox_inches="tight"
)