from astropy.io import fits
from astropy.table import Table
from ciao_contrib.runtool import dmcoords, dmcopy,  dmkeypar, dmmakereg, dmstat, find_chandra_obsid, psfsize_srcs
import os
import pandas as pd

def retrieve_obs_ids(output_dir, source):
    """Creates a CSV File with column name 'Observation ID' containing all Obs. IDs for that source.

    Args:
        output_dir (str): Absolute path to the directory where the list of Obs. IDs is the be saved.
        source (str): Name of the source.
    """

    data = find_chandra_obsid(source)
    with open("Temp.txt", "w") as file:
        file.write(data)

    df = pd.read_csv(f"Temp.txt", sep = "\s+")
    os.remove("Temp.txt")
    new_columns = list(df.columns[1:]) + ["Unnamed"]
    df.columns = new_columns
    df = df.iloc[:, :-1]
    series = pd.Series(df["obsid"], name = "Observation ID")
    series = series.astype(int).sort_values().astype(str).reset_index(drop = True)
    series.index = series.index + 1
    series.to_csv(os.path.join(output_dir, f"{source}.csv"), index = False)

def name_conv(name):
    """Converts source name from CXC sexagecimal format to J2000 sexagecimal format.

    Args:
        name (str): Name of source in CXC sexagecimal format.

    Returns:
        str: Name of source in J2000 sexagecimal format.
    """

    return name.lstrip("2CXO ")

def instrument_checker(event_file):
    """Returns name of instrument with which observation was taken (ACIS/HRC).

    Args:
        event_file (str): Absolute path to event file.

    Returns:
        str: Which instrument was used to take the observation (ACIS/HRC).
    """

    with fits.open(event_file) as hdul:
        header = hdul[0].header
        instrument = header["INSTRUME"]
    
    return instrument

def psf_radius(obs_dir, event_file, source):
    """Returns PSF corrected radius of the source for given event file. Lower bound of 3.2 for ACIS and 7.5 for HRC, upper bound of 61 for both. Multiplied by 1.5
       to account for off-axis angle.

    Args:
        obs_dir (str): Absolute path to directory where you'll be working out of.
        file (str): Absolute path to event file.
        source (str): Source name in J2000 sexagecimal format.

    Returns:
        float: Radius of region in pixels (physical).
    """

    os.chdir(obs_dir)
    coords = source.split("J")[1]
    sign = "+" if "+" in coords else "-"
    ra_raw, dec_raw = coords.split(sign)
    
    ra = f"{ra_raw[0:2]}:{ra_raw[2:4]}:{ra_raw[4:]}"
    dec = f"{dec_raw[0:2]}:{dec_raw[2:4]}:{dec_raw[4:]}"

    psfsize_srcs.punlearn()
    psfsize_srcs(infile = event_file, pos = f"{ra} {sign}{dec}", outfile = "region.fits", ecf = 0.5, clobber = "yes", verbose = 0)
    with fits.open(os.path.join(obs_dir, "region.fits")) as hdul:
        data = hdul[1].data
        radius = 1.5 * float(data["R"])
    #Can be modified later
    instr = instrument_checker(event_file)
    if instr == "ACIS":
        if radius < 3.2:
            radius = 3.2
    elif instr == "HRC":
        if radius < 7.5:
            radius = 7.5
    if radius > 61:
        radius = 61

    os.remove(os.path.join(obs_dir, "region.fits"))
    
    return radius

def isolate_source_region(obs_dir, data_dir, source, energy_min = 200, energy_max = 8000):
    """Creates an isolated event file for the source.

    Args:
        obs_dir (str): Absolute path to directory where light curves are to be saved, It should have CIAO format region file of name '{Source}_{Obs. ID}.reg'.
        data_dir (str): Absolute path to directory where data is saved. It should have name of Obs. ID, and event file should have name '{Obs. ID}_evt2.fits'.
        source (str): Name of source in J2000 sexagecimal format.
        energy_min (int, optional): Lower bound of energy band (eV). Defaults to 200.
        energy_max (int, optional): Upper bound of energy band (eV). Defaults to 8000.

    Returns:
        tuple(outfile, instrument): Tuple containing absolute path to event file and name of instrument used to take the observation (ACIS/HRC).
    """
    
    obs_id = data_dir.split("/")[-1]
    region_file = os.path.join(obs_dir, f"{source}_{obs_id}.reg")
    event_file = os.path.join(data_dir, f"{obs_id}_evt2.fits")
    outfile = os.path.join(obs_dir, f"{source}_{obs_id}.fits")
    instrument = instrument_checker(event_file)
    dmcopy.punlearn()
    if instrument == "ACIS":
        dmcopy(infile = f"{event_file}[sky=region({region_file})][energy={energy_min}:{energy_max}]", outfile = outfile, clobber = "yes")
    else:
        dmcopy(infile = f"{event_file}[sky=region({region_file})][samp=10:300]", outfile = outfile, clobber = "yes")

    return outfile, instrument

def save_source_region(obs_dir, data_dir, source):
    """Creates region file in CIAO format for the given source.

    Args:
        obs_dir (str): Absolute path to directory where region file is to be saved.
        data_dir (str): Absolute path to directory where data is saved. It should have name of Obs. ID, and event file should have name '{Obs. ID}_evt2.fits'.
        source (str): Name of source, preferably in J2000 sexagecimal format.
    """

    obs_id = data_dir.split("/")[-1]
    fits_file = os.path.join(data_dir, f"{obs_id}_evt2.fits")
    coords = source.split("J")[-1]
    sign = "+" if "+" in coords else "-"
    ra_raw, dec_raw = coords.split(sign)
    
    ra = f"{ra_raw[0:2]}:{ra_raw[2:4]}:{ra_raw[4:]}"
    dec = f"{dec_raw[0:2]}:{dec_raw[2:4]}:{dec_raw[4:]}"
    radius = psf_radius(obs_dir, fits_file, source)
    circle = f"circle({ra},{sign}{dec},{radius})"

    dmmakereg.punlearn()
    dmmakereg(region = circle, outfile = os.path.join(obs_dir, f"{source}_{obs_id}.reg"), kernel = "ascii", wcsfile = fits_file, verbose = 0, clobber = "yes")

    with open(os.path.join(obs_dir, f"{source}_{obs_id}.reg"), "r+") as file:
        last_line = file.readlines()[-1].strip()
        last_line = last_line.replace("Circle", "circle").rstrip("#").replace(" ", "") 
        
        file.seek(0)
        file.truncate()
        file.write(last_line + "\n")

def create_postage_stamps(obs_dir, source, region_event_file, event_file, sky_size = 64, det_size = 64):
    """Generates sky and detector coordinate postage stamps.

    Args:
        obs_dir (str): Absolute path to working folder where region file is to be generated. Folder name should be of the Obs. ID.
        source (str): Name of source, preferably in J2000 sexagecimal format.
        region_event_file (str): Absolute path to the event file for the source.
        event_file (str): Absolute path to the event file.
        sky_size (int, optional): Size of sky-coordinate image. Defaults to 64.
        det_size (int, optional): Size of detector-coordinate image. Defaults to 64.

    Returns:
        tuple(sky_image, detector_image): Tuple containing absolute paths to sky-coordinate and detector-coordinate images.
    """

    obs_id = obs_dir.split("/")[-1]
    sky_image = os.path.join(obs_dir, f"{source}_{obs_id}_skyimg.fits")
    detector_image = os.path.join(obs_dir, f"{source}_{obs_id}_detimg.fits")

    dmstat(infile = f"{region_event_file}[cols x,y]", verbose = 0)
    sky_x_min, sky_y_min = map(float, dmstat.out_min.split(","))
    sky_x_max, sky_y_max = map(float, dmstat.out_max.split(","))
    sky_x_padding = sky_x_max - sky_x_min
    sky_y_padding = sky_y_max - sky_y_min

    sky_x_min -= sky_x_padding
    sky_x_max += sky_x_padding
    sky_y_min -= sky_y_padding
    sky_y_max += sky_y_padding

    sky_bin_size_x = (sky_x_max - sky_x_min) / sky_size
    sky_bin_size_y = (sky_y_max - sky_y_min) / sky_size

    dmcopy.punlearn()
    dmcopy(infile = f"{event_file}[bin x={sky_x_min}:{sky_x_max}:{sky_bin_size_x},"f"y={sky_y_min}:{sky_y_max}:{sky_bin_size_y}]", outfile = sky_image, clobber = "yes")

    with fits.open(sky_image, mode = "append") as hdu:
        bounds_hdu = fits.BinTableHDU(Table({"X_MIN": [sky_x_min], "Y_MIN": [sky_y_min], "X_MAX": [sky_x_max], "Y_MAX": [sky_y_max]}))
        bounds_hdu.header["EXTNAME"] = "BOUNDS"
        hdu.append(bounds_hdu)
        hdu.writeto(sky_image, overwrite = True)

    dmstat(infile = f"{region_event_file}[cols detx,dety]", verbose = 0)
    det_x_min, det_y_min = map(float, dmstat.out_min.split(","))
    det_x_max, det_y_max = map(float, dmstat.out_max.split(","))
    det_x_padding = 5
    det_y_padding = 5

    det_x_min -= det_x_padding
    det_x_max += det_x_padding
    det_y_min -= det_y_padding
    det_y_max += det_y_padding

    det_bin_size_x = (det_x_max - det_x_min) / det_size
    det_bin_size_y = (det_y_max - det_y_min) / det_size

    dmcopy.punlearn()
    dmcopy(infile = f"{event_file}[bin detx={det_x_min}:{det_x_max}:{det_bin_size_x},"f"dety={det_y_min}:{det_y_max}:{det_bin_size_y}]", outfile = detector_image, clobber = "yes")

    with fits.open(detector_image, mode = "append") as hdu:
        bounds_hdu = fits.BinTableHDU(Table({
            "X_MIN": [det_x_min], "Y_MIN": [det_y_min],
            "X_MAX": [det_x_max], "Y_MAX": [det_y_max]
        }))
        bounds_hdu.header["EXTNAME"] = "BOUNDS"
        hdu.append(bounds_hdu)
        hdu.writeto(detector_image, overwrite = True)

    return sky_image, detector_image

def retrieve_obs_info(event_file):
    """Returns basic information about the observation.

    Args:
        event_file (str): Absolute path to the event file.

    Returns:
        tuple(start_time, end_time, off_axis_offset, azimuth, ra, dec): Tuple containing 'TSTART', 'TSTOP', Off-Axis Angle, Azimuth, RA, and Dec.
    """

    dmstat(infile = f"{event_file}[cols ra,dec]")
    ra_0 = dmstat.out_mean.split(",")[0]
    dec_0 = dmstat.out_mean.split(",")[1]
    dmcoords(infile = f"{event_file}", option = "cel", ra = ra_0, dec = dec_0)
    theta_0 = dmcoords.theta
    phi_0 = dmcoords.phi
    start_time = dmkeypar(infile = f"{event_file}", keyword = "TSTART", echo = True)
    end_time = dmkeypar(infile = f"{event_file}", keyword = "TSTOP", echo = True)
    off_axis_offset = round(float(theta_0), 1)
    azimuth = int(phi_0)
    ra = round(float(ra_0), 5)
    dec = round(float(dec_0), 5)

    return start_time, end_time, off_axis_offset, azimuth, ra, dec