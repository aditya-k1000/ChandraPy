import numpy as np
import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "ChandraPy"))
from ChandraPy import Lightcurves as lc
from ChandraPy import Download as d
from ChandraPy import Utilities as utils
import shutil

#Adjust these values to your preference
galaxy = ""
main_data_dir = ""
main_source_dir = ""
binsize = 500 
source = ""
obs_id = ""
p0 = 5
likelihood_threshold = np.log(1e-4)

galaxy_data_dir = os.path.join(main_data_dir, galaxy)
source_dir = os.path.join(main_source_dir, galaxy, source)
os.makedirs(galaxy_data_dir, exist_ok = True)

print("\033", end = "")

intro_text = f"Creating light curves for source {source} with bin size of {binsize}s"
max_length = len(intro_text) + 6 
bar = "=" * max_length
print(f"\n{bar}=\n")
print(f"   {intro_text}")
print(f"\n{bar}\n")

obs_dir = os.path.join(source_dir, obs_id)
data_dir = os.path.join(galaxy_data_dir, obs_id)
os.makedirs(obs_dir, exist_ok = True)

if not os.path.exists(os.path.join(data_dir, f"{obs_id}_evt2.fits")):
    print(f"Obs. ID {obs_id} not found, downloading...", end = "")
    d.download_and_reprocess_obsid(galaxy_data_dir, obs_id)
    print("\033[92mDone!\033[0m")

print(f"Obs. ID {obs_id}...", end = "")

try:
    utils.save_source_region(obs_dir, data_dir, source)
    processed = lc.lightcurve_generation(obs_dir, data_dir, source, binsize, p0, likelihood_threshold)
    if not processed:
        print("\033[93mEmpty\033[0m\n")
    else:
        print("\033[92mDone!\033[0m\n")
except Exception as e:
    processed = False
    print(e)
    print(f"\033[91mError, {e}\033[0m")

if not processed:
    shutil.rmtree(obs_dir, ignore_errors = True)
    