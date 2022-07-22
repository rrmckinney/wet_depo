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

from utils.funcs import wdcompliant, plot_func, get_title

from context import img_dir, data_dir

warnings.filterwarnings("ignore")
### User Inputs ###
case_study = "" #choice of ""(control),"wdwet8"(8e-5),"wdNAME"(8.4e-5,0.00036) - will define input file
date = "20190601" #forecast date of interest - will define inout file
plot_extent = [-125,-109.99,54,60] #set bounds for plot dependant on region(s) of interest
###################

## Read in files of interest 
filein = f"{data_dir}/output{case_study}/{date}00/hysplit_conc.nc"  #netcdf output from bsp

## Run through function that makes raw bsp output cf compliant and ready for plotting
nc = wdcompliant(filein)

## Get variables from newly created cf dataset 
lats = np.squeeze(nc.variables['lat'][:])
lons = np.squeeze(nc.variables['lon'][:])
var = np.squeeze(nc.variables["pm25"][:])[0,:,:]

## Setup figure
fig = plt.figure(figsize=(24,18))

## Plot a subpot for all 23 hours of the forecast
for i in range(23):
    im=plot_func(nc,i, plot_extent,fig,lons,lats)
    
plt.subplots_adjust(left=0.125,                                 ## make plot pretty
                    bottom=0.1, 
                    right=1, 
                    top=0.99, 
                    wspace=0.1, 
                    hspace=0)

case_name = get_title(case_study)                               ## set plot title to nice formatting

fig.text(0.9,0.1,f"Bluesky WD PM25 Forecast - {date} - {case_name}")   ## set plot identifier - states date and case study of interest in bottom right corner
cbar_ax = fig.add_axes([1.05, 0.4, 0.025, 0.3])                         ## define colorbar legend placement 
cbar = fig.colorbar(im,cax=cbar_ax)                                     ## add in colorbar legend
cbar.set_label(r'PM 2.5 ($\mu$g $m^{-3}$)', fontsize=18)                ## set colorbar legend title

plt.savefig(                                                            ## save plot as .png named after date and case study 
    str(img_dir)+ f"/wd-{date}-{case_name}.png", bbox_inches="tight"
)