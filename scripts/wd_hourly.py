## %

## Script to read in bsp hysplit output, AB obs & BC obs and make it into hourly plots for a day of interest ##
## Reagan McKinney ##
## June 2022 ##


import pandas as pd
from datetime import datetime, timedelta
from netCDF4 import Dataset 
import numpy as np
from pylab import *
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import cartopy.feature as cf
from cartopy.io.shapereader import Reader
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import warnings

from utils.funcs import wdcompliant, plot_func, get_title
from utils.ab_pm import get_ab_obs
from utils.bc_pm import get_bc_obs
from context import img_dir, data_dir

warnings.filterwarnings("ignore")

### User Inputs ###
scheme = "" #choice of ""(control),"wdwet8"(8e-5),"wdNAME"(8.4e-5,0.00036) - will define input file
date = "20190519" #forecast date of interest - will define input file
plot_extent = [-125,-109.99,54,60] #set bounds for plot dependant on region(s) of interest
ab_obs_file = "station_obs_ab_052019-062019.csv" #observational dataset
###################

## Read in files of interest 
filein = f"{data_dir}/output{scheme}/{date}00/hysplit_conc.nc"  #netcdf output from bsp

## Run through functions that makes raw bsp output and obs cf compliant and ready for plotting
nc = wdcompliant(filein)
ab_obs_in = get_ab_obs(ab_obs_file, f"{date}00")
bc_obs_in = get_bc_obs(date)

## Get bsp output variables from newly created cf dataset 
lats = np.squeeze(nc.variables['lat'][:])
lons = np.squeeze(nc.variables['lon'][:])
var = np.squeeze(nc.variables["pm25"][:])[0,:,:]

## Get Alberta observational data from newly created cf dataset
obslats = np.squeeze(ab_obs_in.variables['lat'][:])
obslons = np.squeeze(ab_obs_in.variables['lon'][:])
obspm25 = np.squeeze(ab_obs_in.variables["pm25"][:])

## Get BC observational data from newly created cf dataset
bclats = np.squeeze(bc_obs_in.variables['lat'][:])
bclons = np.squeeze(bc_obs_in.variables['lon'][:])
bcpm25 = np.squeeze(bc_obs_in.variables["pm25"][:])

## Setup figure
fig = plt.figure(figsize=(24,18))

## Setup color map
# cmap = cm.get_cmap('gist_heat_r',20)
# colors = []
# for i in range(cmap.N):
#     rgba = cmap(i)
#     colors.append(matplotlib.colors.rgb2hex(rgba))

## Plot a subpot for all 23 hours of the forecast
for i in range(23):
    im = plot_func(nc,i, plot_extent,fig,lons,lats) ## plots model data and formats the map all pretty with borders etc. 
    plt.scatter(obslons,obslats, c= obspm25[i],marker = 's', alpha=1, s=100,zorder=2,cmap='gist_heat_r',edgecolors='black',vmin=0,vmax=var.max()) ## plots ab observational data
    plt.scatter(bclons,bclats, c= bcpm25[i],marker = 'o', alpha=1, s=100,zorder=2,cmap='gist_heat_r',edgecolors='black',vmin=0,vmax=var.max()) ## plots bc observational data)

plt.subplots_adjust(left=0.125,                                 ## make plot pretty
                    bottom=0.1, 
                    right=1, 
                    top=0.99, 
                    wspace=0.1, 
                    hspace=0)

scheme_name = get_title(scheme)                                       ## set plot title to nice formatting
fig.text(0.83,0.1,f"Bluesky WD PM25 Forecast - {date} - {scheme_name}")    ## set plot identifier - states date and case study of interest in bottom right corner
legend_elements = [Patch(facecolor='peachpuff',edgecolor='darkorange', label='Bluesky Canada Output'),
                   Line2D([0], [0], marker='s', color='black',linestyle='None', label="Alberta Observations",
                          markerfacecolor='peachpuff', markersize=25),
                   Line2D([0], [0], marker='o', color='black',linestyle='None', label="British Columbia Observations",
                          markerfacecolor='peachpuff', markersize=25)]
plt.legend(handles = legend_elements,bbox_to_anchor=(2.20,0.3),loc='lower right',fontsize=18)

cbar_ax = fig.add_axes([1.05, 0.4, 0.025, 0.3])                         ## define colorbar legend placement 
cbar = fig.colorbar(im,cax=cbar_ax)                                     ## add in colorbar legend
cbar.set_label(r'PM 2.5 ($\mu$g $m^{-3}$)', fontsize=18)                ## set colorbar legend title

plt.savefig(                                                            ## save plot as .png named after date and case study 
    str(img_dir)+ f"/wd-{date}-{scheme_name}.png", bbox_inches="tight"
)