import customtkinter as ctk
import pandas as pd
import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "ChandraPy"))
from ChandraPy import Utilities as utils
from ChandraPy import Download as d
import concurrent.futures
import shutil

def multithreaded_download(df, object_data_dir):
    def process_obs_id(obs_id):
        obs_dir = os.path.join(object_data_dir, obs_id)
        if not os.path.exists(obs_dir):
            print(f"\nDownloading Obs. ID {obs_id}...", end = "")
            try:
                d.download_and_reprocess_obsid(object_data_dir, obs_id)
                print("Done!")
            except Exception as e:
                print("Error", e)
                #shutil.rmtree(obs_dir)
 
    with concurrent.futures.ThreadPoolExecutor(max_workers = 6) as executor:
        futures = [executor.submit(process_obs_id, obs_id) for obs_id in df["Observation ID"]]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result() 
            except Exception as e:
                print(f"\nAn exception occurred during processing: {e}")

def processing():
    object = entries[0].get() 
    data_dir = entries[1].get() 
    obs_id = entries[2].get() 

    os.makedirs(os.path.join(data_dir, object), exist_ok = True)
    object_data_dir = os.path.join(data_dir, object)

    if obs_id == "":
        if not os.path.exists(os.path.join(object_data_dir, f"{object}.csv")):
            print("Retrieving Obs. IDs...", end = "")
            utils.retrieve_obs_ids(object_data_dir, object)
            print("Done!")
        df = pd.read_csv(os.path.join(object_data_dir, f"{object}.csv"), dtype = str)
        multithreaded_download(df, object_data_dir)
        print(f"Data for {object} downloaded successfully!\n")
    else:
        print(f"\nDownloading Obs. ID {obs_id}...", end = "")
        try:
            obs_dir = os.path.join(object_data_dir, obs_id)
            d.download_and_reprocess_obsid(object_data_dir, obs_id)
            print("Done!", end = "")
        except Exception as e:
            print("Error", e, end = "")
            shutil.rmtree(obs_dir)

#GUI
root = ctk.CTk()
ctk.set_appearance_mode("Dark")
root.geometry("600x400")
root.resizable(0, 0)
root.title("Download Chandra Data")

def enable_paste(event):
    event.widget.event_generate("<<Paste>>")

title_label = ctk.CTkLabel(root, text = "Download Chandra Data", font = ("Helvetica", 45), text_color = "white")
title_label.place(relx = 0.5, rely = 0.28, anchor = ctk.CENTER)

labels = [("Object", ""), ("Output Directory", ""), ("Observation ID", "")]
entries = []

start_y = 190
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