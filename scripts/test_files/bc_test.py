import pandas as pd
from datetime import datetime, timedelta
from netCDF4 import Dataset 
import numpy as np


from context import bc_dir

obsdat = pd.read_csv(f"{bc_dir}/bc_obc_20190519.csv")

print(obsdat)