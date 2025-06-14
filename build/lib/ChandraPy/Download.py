from ciao_contrib.runtool import axbary, chandra_repro, dmhedit, dmkeypar
import gzip
import os
import shutil
import subprocess

def download_and_reprocess_obsid(data_dir, obs_id):
    """Downloads and reprocesses the data for a given Chandra Obs. ID.

    Args:
        data_dir (str): Absolute path to directory where data is saved.
        obs_id (str): The Obs. ID Number.
    """
    
    obs_id = str(obs_id)
    os.chdir(data_dir)
    subprocess.run(["download_chandra_obsid", obs_id, "-q"])
    obs_dir = os.path.join(os.getcwd(), obs_id)
    primary_dir = os.path.join(obs_dir, "primary")
    secondary_dir = os.path.join(obs_dir, "secondary")
    repro_dir = os.path.join(obs_dir, "repro")

    chandra_repro(obs_dir, clobber = "yes")

    names = {"repro_evt2.fits": f"{obs_id}_evt2.fits",
            "repro_bpix1.fits": f"{obs_id}_bpix1.fits",
            "repro_flt2.fits": f"{obs_id}_flt2.fits",
            "repro_fov1.fits": f"{obs_id}_fov1.fits",
            "asol1.fits": f"{obs_id}_asol1.fits",
            "pbk0.fits": f"{obs_id}_pbk0.fits",
            "stat1.fits": f"{obs_id}_stat1.fits",
            "mtl1.fits": f"{obs_id}_mtl1.fits",
            "msk1.fits": f"{obs_id}_msk1.fits",
            "dtf1.fits": f"{obs_id}_dtf1.fits"
            }

    for file in os.listdir(primary_dir):
        if "orbit" in file:
            old = os.path.join(primary_dir, file)
            new = os.path.join(obs_dir, file)
            os.rename(old, new)

            unzipped_path = new[:-3]
            with gzip.open(new, "rb") as f_in:
                with open(unzipped_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            os.remove(new)

    for file in os.listdir(repro_dir):
        old_path = os.path.join(repro_dir, file)
        new_path = os.path.join(obs_dir, file)
        shutil.move(old_path, new_path)

    shutil.rmtree(primary_dir)
    shutil.rmtree(secondary_dir)
    shutil.rmtree(repro_dir)

    for file in os.listdir(obs_dir):
        for key, name in names.items():
            if key in file:
                os.rename(os.path.join(obs_dir, file), os.path.join(obs_dir, name))

    event_file = os.path.join(obs_dir, f"{obs_id}_evt2.fits")
    bary_event_file = os.path.join(obs_dir, f"{obs_id}_evt2_bary.fits")
    asol_file = os.path.join(obs_dir, f"{obs_id}_asol1.fits")
    bary_asol_file = os.path.join(obs_dir, f"{obs_id}_asol1_bary.fits")
    stat_file = os.path.join(obs_dir, f"{obs_id}_stat1.fits")
    bary_stat_file = os.path.join(obs_dir, f"{obs_id}_stat1_bary.fits")
    tstart = float(dmkeypar(infile = event_file, keyword = "TSTART", echo = True))
    start_time = 0
    orbit_file = "1"

    for file in os.listdir(obs_dir):
        if "orbit" in file and file.endswith("fits"):
            current_orbit_file = os.path.join(obs_dir, file)
            time = float(dmkeypar(infile = current_orbit_file, keyword = "TSTART", echo = True))
            if time <= tstart and time > start_time:
                start_time = time
                orbit_file = current_orbit_file

    ra = dmkeypar(infile = event_file, keyword = "RA_TARG", echo = True)
    dec = dmkeypar(infile = event_file, keyword = "DEC_TARG", echo = True)

    axbary.punlearn()
    axbary(infile = event_file, orbitfile = orbit_file, outfile = bary_event_file, ra = ra, dec = dec, clobber = "yes")
    os.rename(bary_event_file, event_file)

    axbary.punlearn()
    axbary(infile = asol_file, orbitfile = orbit_file, outfile = bary_asol_file, ra = ra, dec = dec, clobber = "yes")
    os.rename(bary_asol_file, asol_file)

    if os.path.exists(stat_file):
        axbary.punlearn()
        axbary(infile = stat_file, orbitfile = orbit_file, outfile = bary_stat_file, ra = ra, dec = dec, clobber = "yes")
        os.rename(bary_stat_file, stat_file)

    dmhedit(infile = event_file, operation = "add", key = "ASOLFILE", value = f"{obs_id}_asol1.fits")

    for file in os.listdir(obs_dir):
        file_path = os.path.join(obs_dir, file)
        if file not in names.values() and os.path.isfile(file_path):
            os.remove(file_path)