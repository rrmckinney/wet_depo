""" 
Define the ptah to important folders with having to install anything:
just:                                       import context
then the path for the data directory is:    context.data_dir
"""

import sys
import site
from pathlib import Path

path = Path(__file__).resolve() #this file
this_dir = path.parent # this folder
notebooks_dir = this_dir
root_dir = notebooks_dir.parents[0]
data_dir = root_dir / Path("data")
bc_dir = data_dir / Path("bc_obs")
img_dir = root_dir / Path("img")
