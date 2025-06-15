# ChandraPy
ChandraPy is an open-source Python Package that simplifies and speeds up data processing using the Chandra X-Ray Observatory.

## Differences compared to the Lightcurves App
The Lightcurves App (https://github.com/SenatorTreason05/Lightcurves.git) is a compact tool that generates light curves for all sources given in the Chandra Source Catalog within a user-specified region. It's intended to quickly generate all the light curves for a cursory inspection of the sources in that region. It downloads the `regevt3` files provided by the CSC for all these sources, allowing it to generate light curves very quickly and efficiently. However, this approach may not be the most rigorous and accurate method of producing results.

ChandraPy, on the other hand, is a Python Package which gives the user control of all the individual functions for applications in various workflows. It also produces all of its results from raw data reprocessed and extracted locally. In future releases, I plan to add a script which gives a functionality similar to that of the Lightcurves App.

## Installation Prerequisites
Ensure that CIAO is installed on your system, preferably in a conda environment. Install the CALDB as well, following instructions from this thread: https://cxc.cfa.harvard.edu/ciao/download/conda.html. This automatically installs Python in that environment, so there's no need to do that separately.

I'd recommend creating an alias in the `bash_profile`/`bashrc` file to easily initialize it. Further, if you have other software like HEASoft/SAS installed, I'd recommend exporting the `PATH` variable again, as various functions such as `pget` can get messed up. For example, my alias is:
```bash
function ciao() {
	conda activate ciao-4.17
	echo
	echo 'CIAO initialized successfully!' 
	echo
	export PATH="/opt/anaconda3/envs/ciao-4.17/bin:$PATH"
}
```

Further, I'd recommend creating wrappers for HEASoft binaries to avoid requiring its initialization, as that can change some environment variables, interfering with some functions: https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/hwrap.html.

The following Python packages should be installed in that conda environment:
 - NumPy
 - MatPlotLib
 - Pandas
 - AstroPy
 - CustomTkinter (optional, for scripts)

To install them in one go, run `pip install numpy matplotlib pandas astropy customtkinter` from inside the activated conda environment.

## Installation
Download the ZIP file from GitHub, unzip the contents, and begin usage for data analysis!

***Remember to first initialize CIAO conda environment, then run the Python files. Keep the scripts in the same folder as the one where ChandraPy is kept.***

The idea behind ChandraPy is to create a "bank/repository" of data for a given galaxy, and then create light curves using that. This method is faster in the long run, as you can create light curves for any source in a galaxy instantly without having to download new event files each time. It's also more rigorous, as all the data is processed from scratch using first principles, helping ensure the data is as accurate as possible.

## How to use each script
***Remember to initialize the CIAO conda environment before running any function/script included with ChandraPy.***  

Here's how to use each of the scripts included with ChandraPy, and whether it's GUI based or not:
### Download Chandra Data.py (GUI Based, includes multithreading)
   - Opens a GUI Window, with the following options:
     
     - ***Object***: Name of the Galaxy (M33, NGC104, etc.) Don't include any spaces. Further, it's preferred to use a catalog name, not a common name like 47Tuc. However, a common name will also work as long as there are no spaces)
       
     - ***Output Directory***: Absolute path to the directory where the data is to be stored. The data files, such as `evt2` and `asol1` file will be stored in directory `<output_dir>/<object>/<obs_id>`. There should be no spaces in this either
       
     - ***Observation ID*** (optional): The specific Observation ID whose data you wish to download. Leave blank to download them all
   
   - This script will download all data for that Object and that/those Observation ID(s). It will run the `chandra_repro` script to produce reprocessed `level 2` files, and will run barycentric corrections on those. Finally, it will rename the files to have names `<obs_id>_<type>.fits`. These will be stored in directory `<output_dir>/<object>/<obs_id>`. The file types are `asol1`, `bpix1`, `evt2`, `flt2`, `fov1`, `msk1`, `mtl1`, `pbk0`, `stat1`. The DTF file of filetype `dtf1` is also included for HRC corrections due to it requiring Dead-Time Correction

### Process One Source.py (GUI Based, no multithreading)
   - Opens a GUI Window, with the following options:  
     
     - ***Galaxy***: Name of Galaxy/Body in which the source is present (M33, NGC104, etc.) Don't include any spaces. Further, it's preferred to use a catalog name, not a common name like 47Tuc. However, a common name will also work as long as there are no spaces)
       
     - ***Data Directory***: Absolute path to the directory where the data is present in directory `<data_directory>/<galaxy>/<obs_id>`. You can use the same directory you added for `Output Directory` in the `Download Chandra Data` script. In case the data for a particular Observation ID isn't present, then it's downloaded and reprocessed inside this directory as specified in the `Download Chandra Data` script
       
     - ***Output Directory***: Absolute path to the directory where the output data is to be stored. The data will be output to the directory `<output_dir>/<galaxy>/<obs_id>`. The data saved will be:
       - Light Curve with name `<source>_<obs_id>.svg`. It has:
         
         - Postage stamp images in Sky and Detector Coordinates
         - Broadband Binned Count Rate v/s Time light curve
         - Bayesian Blocks Segmented Count Rate v/s Time light curve (separated into various energy bands for ACIS observations)
         - Binned Broadband Counts light curve 
         - Cumulative Counts light curve
         - Binned Hardness Ratio v/s Time light curve
           
       - Region File with name `<source>_<obs_id>.reg` in CIAO format. Can be opened in SAOImage DS9
       - CSV file containing summary data of light curve with name `<source>_<obs_id>.csv`
       - CSV file containing summary of Bayesian Blocks segmentation with name `<source>_<obs_id>_bb.csv`
       
     - ***Binsize***: Binsize to be used for binning light curves (s)
       
     - ***Source***: The source inside the Galaxy/Body whose data is to be processed. Use coordinates in J2000 sexagecimal format (Ex. `J0132546.4+302145.9`)
       
     - ***Observation ID*** (optional): The specific Observation ID whose data you wish to process. Leave blank to process them all. In case the data for a particular Observation ID isn't present, then it's downloaded and reprocessed inside `Data Directory` as specified in the `Download Chandra Data` script
       
     - ***p0 Value*** (optional): Value of p0 to be used when computing Bayesian Blocks segmentation
       
     - ***Likelihood Threshold*** (optional): The likelihood threshold to be used when computing Bayesian Blocks segmentation (can be added as `np.log(1e-3) for ln(0.001)`)
   
   - This script will download all data for that Object and that/those Observation ID(s). It will run the `chandra_repro` script to produce reprocessed `level 2` files, and will run barycentric corrections on those. Finally, it will rename the files to have names `<obs_id>_<type>.fits`. These will be stored in directory `<output_dir>/<object>/<obs_id>`. The file types are `asol1`, `bpix1`, `evt2`, `flt2`, `fov1`, `msk1`, `mtl1`, `pbk0`, `stat1`. The DTF file of filetype `dtf1` is also included for HRC corrections due to it requiring Dead-Time Correction
     
### Process One Source With One Obs. ID.py (Non-GUI Based, no multithreading)
   - The various parameters have to be manually edited in this file using a text editor such as VSCode before running. The parameters are:
  
     - ***`galaxy`***: Name of Galaxy/Body in which the source is present (M33, NGC104, etc.) Don't include any spaces. Further, it's preferred to use a catalog name, not a common name like 47Tuc. However, a common name will also work as long as there are no spaces)
       
     - ***`main_data_dir`***: Absolute path to the directory where the data is present in directory `<main_data_dir>/<galaxy>/<obs_id>`. You can use the same directory you added for `Output Directory` in the `Download Chandra Data` script or for `Data Directory` in the `Process One Source` script. In case the data for a particular Observation ID isn't present, then it's downloaded and reprocessed inside this directory as specified in the `Download Chandra Data` script
       
     - ***`main_source_dir`***: Absolute path to the directory where the output data is to be stored. The data will be output to the directory `<main_source_dir>/<galaxy>/<obs_id>`. The data saved will be:
       - Light Curve with name `<source>_<obs_id>.svg`. It has:
         
         - Postage stamp images in Sky and Detector Coordinates
         - Broadband Binned Count Rate v/s Time light curve
         - Bayesian Blocks Segmented Count Rate v/s Time light curve (separated into various energy bands for ACIS observations)
         - Binned Broadband Counts light curve 
         - Cumulative Counts light curve
         - Binned Hardness Ratio v/s Time light curve
           
       - Region File with name `<source>_<obs_id>.reg` in CIAO format. Can be opened in SAOImage DS9
       - CSV file containing summary data of light curve with name `<source>_<obs_id>.csv`
       - CSV file containing summary of Bayesian Blocks segmentation with name `<source>_<obs_id>_bb.csv`
       
     - ***`binsize`***: Binsize to be used for binning light curves (s)
       
     - ***`source`***: The source inside the Galaxy/Body whose data is to be processed. Use coordinates in J2000 sexagecimal format (Ex. `J0132546.4+302145.9`)
       
     - ***`obs_id`***: The specific Observation ID whose data you wish to process. In case the data for that particular Observation ID isn't present, then it's downloaded and reprocessed inside `main_data_dir` as specified in the `Download Chandra Data` script
       
     - ***`p0`*** (optional): Value of p0 to be used when computing Bayesian Blocks segmentation
       
     - ***`likelihood_threshold`*** (optional): The likelihood threshold to be used when computing Bayesian Blocks segmentation (can be added as `np.log(1e-3) for ln(0.001)`)

To run any of these scripts, open the terminal and, after initializing the CIAO conda environment, run `python <absolute path to script file.`

## Things to watch out for
 - Ensure the CIAO conda environment is initialized before running any function/script included with ChandraPy. Keep all scripts in the same directory as the ChandraPy folder.
 - Ensure all directories provided have no spaces in them
 - Ensure none of the names provided (Galaxy name, Source name) don't have any spaces. Source should be in J2000 sexagecimal format
 - Ensure that Python and the terminal have access and writing privileges to the directories you provide.
 - If creating your own scripts, insert this to the beginning of your file:
  ```python
  import os
  import sys
  sys.path.append(os.getcwd())
  sys.path.append(os.path.join(os.getcwd(), "ChandraPy"))
```
  When this package gets published to PYPI, this won't be required.

## Known issues
 - When using Binsizes that are different than 500s, the positions of the boxes in the light curve `.svg` file aren't aligned properly
 - Some elements in the light curve `.svg` file may not be centered properly

## Future plans
I'll be adding a PDF with a full explanation of all the functions provided with ChandraPy and the logic behind them. I'll also be adding more scripts, improve the layout of the light curve `.svg` file, and provide the user with more controls over the light curve generation.
