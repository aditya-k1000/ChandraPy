import customtkinter as ctk
import pandas as pd
import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "ChandraPy"))
from ChandraPy import Lightcurves as lc
from ChandraPy import Download as d
from ChandraPy import Utilities as utils
import shutil

def processing():
    galaxy = entries[0].get() 
    main_data_dir = entries[1].get() 
    main_source_dir = entries[2].get()
    binsize = entries[3].get()
    source = entries[4].get()
    obs_id = entries[5].get() 

    galaxy_data_dir = os.path.join(main_data_dir, galaxy)
    source_dir = os.path.join(main_source_dir, galaxy, source)
    os.makedirs(galaxy_data_dir, exist_ok = True)
    os.makedirs(source_dir, exist_ok = True)

    print("\033", end = "")

    intro_text = f"Creating light curves for source {source} with bin size of {binsize}s"
    max_length = len(intro_text) + 6 
    bar = "=" * max_length
    print(f"\n{bar}=\n")
    print(f"   {intro_text}")
    print(f"\n{bar}\n")

    if obs_id == "":
        not_processed = 0
        to_remove = []
        utils.retrieve_obs_ids(source_dir, source)
        df = pd.read_csv(os.path.join(source_dir, f"{source}.csv"), dtype = str)
        for i, obs_id in enumerate(df["Observation ID"]):
            obs_dir = os.path.join(source_dir, obs_id)
            data_dir = os.path.join(galaxy_data_dir, obs_id)
            os.makedirs(obs_dir, exist_ok = True)

            if not os.path.exists(os.path.join(data_dir, f"{obs_id}_evt2.fits")):
                print(f"Obs. ID {obs_id} not found, downloading...", end = "")
                d.download_and_reprocess_obsid(galaxy_data_dir, obs_id)
                print("\033[92mDone!\033[0m")

            print(f"({i + 1}/{len(df['Observation ID'])}) Obs. ID {obs_id}...", end = "")

            try:
                utils.save_source_region(obs_dir, data_dir, source)
                processed = lc.lightcurve_generation(obs_dir, data_dir, source, binsize)
                if not processed:
                    not_processed += 1
                    to_remove.append(obs_dir)
                    print("\033[93mEmpty\033[0m")
                else:
                    print("\033[92mDone!\033[0m")
            except Exception as e:
                not_processed += 1
                processed = False
                to_remove.append(obs_dir)
                print(f"\033[91mError, {e}\033[0m")

        for obs_dir in to_remove:
            shutil.rmtree(obs_dir, ignore_errors = True)

        process_text = "Process Complete"
        count_text = f"{len(df['Observation ID']) - not_processed} / {len(df['Observation ID'])} light curves made"
        max_length = max(len(process_text), len(count_text)) + 6
        bar = "=" * max_length

        print(f"\n{bar}\n")
        print(f"   \033[92m{process_text}\033[0m")
        print(f"   {count_text}")
        print(f"\n{bar}\n")
    else:
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
            processed = lc.lightcurve_generation(obs_dir, data_dir, source, binsize)
            if not processed:
                print("\033[93mEmpty\033[0m")
            else:
                print("\033[92mDone!\033[0m")
        except Exception as e:
            processed = False
            print(e)
            print(f"\033[91mError, {e}\033[0m")

        if not processed:
            shutil.rmtree(obs_dir, ignore_errors = True)

#GUI
root = ctk.CTk()
ctk.set_appearance_mode("Dark")
root.geometry("600x400")
root.resizable(0, 0)
root.title("Process One Source")

def enable_paste(event):
    event.widget.event_generate("<<Paste>>")

title_label = ctk.CTkLabel(root, text = "Process One Source", font = ("Helvetica", 45), text_color = "white")
title_label.place(relx = 0.5, rely = 0.14, anchor = ctk.CENTER)
labels = [("Galaxy", ""), ("Data Directory", ""), ("Output Directory", ""), ("Binsize", ), ("Source", ""), ("Observation ID", "")]
entries = []
start_y = 100
spacing = 40

for i, label_value in enumerate(labels):
    label_text, value = label_value
    label = ctk.CTkLabel(root, text = label_text + ":", anchor = "e", width = 150, text_color = "white")
    label.place(x = 5, y = start_y + i * spacing)
    entry = ctk.CTkEntry(root, width = 300, text_color = "white")
    entry.insert(0, value)  
    entry.place(x = 160, y = start_y + i * spacing)
    entries.append(entry)

for entry in entries:
    entry.bind("<Control-v>", enable_paste)

button = ctk.CTkButton(master = root, text = "Start", command = processing, text_color = "white")
button.place(relx = 0.5, rely = 0.9, anchor = ctk.CENTER)
root.focus_force()
root.mainloop() 