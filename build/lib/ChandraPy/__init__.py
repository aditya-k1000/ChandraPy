import pandas as pd

#Regular light curve plotting 
#Naming conventions
names = {"Broadband": "b",
         "Ultrasoft": "us", 
         "Soft": "s", 
         "Medium": "m", 
         "Hard": "h"
         }

#Energy band minimums
bands_min = {"b": 200.,
             "us": 200.,
             "s": 500.,
             "m": 1200.,
             "h": 2000.
             }

#Energy band maximums
bands_max = {"b": 8000.,
             "us": 500.,
             "s": 1200.,
             "m": 2000.,
             "h": 8000.
             }

#Plot colors
colors = {"b": "black",
          "us": "brown",
          "s": "red",
          "m": "green",
          "h": "blue"
             }

#Plot text
text = {"b": "Broadband (0.2 - 8 keV)",
        "us": "Ultrasoft (0.2 - 0.5 keV)",
        "s": "Soft (0.5 - 1.2 keV)",
        "m": "Medium (1.2 - 2 keV)",
        "h": "Hard (2 - 8 keV)"
             }

#Summary info file for plotting
values = pd.DataFrame({
    "Band": list(names.keys()),
    "Identifier": list(names.values()),
    "Energy Min": [bands_min[identifier] for identifier in names.values()],
    "Energy Max": [bands_max[identifier] for identifier in names.values()],
    "Color": [colors[identifier] for identifier in names.values()],
    "Text": [text[identifier] for identifier in names.values()]
}) 

#Hardness ratio plotting
#Hardness Ratios
hr = {
    r"$\frac{M - S}{M + S}$": "m-s",
    r"$\frac{H - S}{H + S}$": "h-s",
    r"$\frac{S - (M + H)}{S + (M + H)}$": "s-m-h",
    r"$\frac{(S + U) - (H + M)}{(S + U) + (H + M)}$": "h-m-s-u" #Flip later
}

#Hardness Ratio Colors
hr_colors = {"m-s": "gold",
             "h-s": "lightskyblue",
             "s-m-h": "green",
             "h-m-s-u": "purple"
             }

hr_values = pd.DataFrame({
    "Formula": list(hr.keys()),
    "Identifier": list(hr.values()),
    "Color": [hr_colors[identifier] for identifier in hr.values()]
})

order = ["Bin", "Time", "Broadband Count Rate", "Ultrasoft Count Rate", "Soft Count Rate", "Medium Count Rate", "Hard Count Rate", "Count Rate Error", "Broadband Counts", "Ultrasoft Counts", "Soft Counts", "Medium Counts", "Hard Counts"]