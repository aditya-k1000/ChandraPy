from astropy.io import fits
from astropy.stats import histogram
from astropy.table import Table
from ChandraPy import hr_values
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import warnings

def cumulative_counts_plotter(plt, times, make_xlabel = False):
    """Create a Cumulative Counts Plot.

    Args:
        plt (matplotlib.axes._axes.Axes/matplotlib.figure.Figure): MatPlotLib layer on which to plot data.
        times (numpy.ndarray): Array of photon arrival times (s), typically 'time' column of event list, all values should be subtracted by 'tstart'.
        make_xlabel (bool, optional): Whether to write the x-axis label or not. Defaults to False.
    """

    plt.plot(times, np.arange(1, len(times) + 1), color = "magenta")
    if make_xlabel:
        plt.xlabel("Time (ks)", fontsize = 10)
    plt.ylabel("Cumulative Counts (cts)", fontsize = 10)
    plt.grid(True, which = "both", linestyle = "--", linewidth = 0.5)
    plt.tick_params(axis = "both", which = "major", labelsize = 10)

def rate_plotter(plt, times, count_rates, color = "black", errors = None, timedel = None, make_xlabel = False, text = None, dashed = False):
    """Create a step plot of Count Rate v/s Time

    Args:
        plt (matplotlib.axes._axes.Axes/matplotlib.figure.Figure): MatPlotLib layer on which to plot data
        times (numpy.ndarray): Array of photon arrival times (s), typically 'time' column of event list, all values should be subtracted by 'tstart'
        count_rates (numpy.ndarray): Array of count rates (cts/s)
        color (str, optional): Color of the plot. Defaults to 'black'
        errors (numpy.ndarray, optional): Array of count rate errors (cts/s). Defaults to None
        timedel (float, optional): Value of 'TIMEDEL' in event file header. Defaults to None
        make_xlabel (bool, optional): Whether to write the x-axis label or not. Defaults to False
        text (str, optional): The text to add as the label of the plot. Defaults to None
        dashed (bool, optional): Whether to make the plot a dashed line or not. Defaults to False
    """

    if timedel is not None:
        count_rates *= timedel

    if dashed:
        plt.step(times, count_rates, color, where = "post", linestyle = "dotted", label = text)
    else:
        if errors is not None:
            plt.errorbar(times, count_rates, yerr = errors, fmt = "o", color = "black", ecolor = "black", elinewidth = 0.75, capsize = 2, capthick = 0.75, markersize = 4)
            plt.plot(times, np.convolve(count_rates, np.ones(3) / 3, mode = "same"), color = "red")
        else:
            plt.step(times, count_rates, color, where = "post", label = text)

    if make_xlabel:
        plt.xlabel("Time (ks)", fontsize = 10)
    if timedel is not None:
        plt.ylabel(f"Count Rate over {(times[-1] - times[-2]) * 1000:.2f}s bins (cts/frame)", fontsize = 10)
    else:
        plt.ylabel(f"Count Rate over {(times[-1] - times[-2]) * 1000:.2f}s bins (cts/s)", fontsize = 10)
    plt.grid(True, which = "both", linestyle = "--", linewidth = 0.5)
    plt.tick_params(axis = "both", which = "major", labelsize = 10)

def counts_plotter(plt, times, counts, color = "magenta", make_xlabel = False, text = None, dashed = False):
    """Create a step plot of Counts v/s Time

    Args:
        plt (matplotlib.axes._axes.Axes/matplotlib.figure.Figure): MatPlotLib layer on which to plot data
        times (numpy.ndarray): Array of photon arrival times (s), typically 'time' column of event list, all values should be subtracted by 'tstart'
        counts (numpy.ndarray): Array of photon counts (cts)
        color (str, optional): Color of the plot. Defaults to 'magenta'
        make_xlabel (bool, optional): Whether to write the x-axis label or not. Defaults to False
        text (str, optional): The text to add as the label of the plot. Defaults to None
        dashed (bool, optional): Whether to make the plot a dashed line or not. Defaults to False
    """

    if dashed:
        plt.step(times, counts, color, where = "post", linestyle = "dotted", label = text)
    else:
        plt.step(times, counts, color, where = "post", label = text)

    if make_xlabel:
        plt.xlabel("Time (ks)", fontsize = 10)
    plt.ylabel(f"Counts over {(times[-1] - times[-2]) * 1000:.2f}s bins (cts)", fontsize = 10)
    plt.grid(True, which = "both", linestyle = "--", linewidth = 0.5)
    plt.tick_params(axis = "both", which = "major", labelsize = 10)

def hr_plotter(plt, lc_file, tstart, make_xlabel = True):
    """Creates a step plot of various Hardness Ratios v/s Time

    Args:
        plt (matplotlib.axes._axes.Axes/matplotlib.figure.Figure): MatPlotLib layer on which to plot data
        lc_file (str): Absolute path to CSV output file with columns 'Ultrasoft Count Rate', 'Soft Count Rate', 'Medium Count Rate', 'Hard Count Rate'
        tstart (float): Value of 'TSTART' in event file header. Defaults to None
        make_xlabel (bool, optional): Whether to write the x-axis label or not. Defaults to False
    """

    lc = pd.read_csv(lc_file)
    times = (lc["Time"] - tstart) / 1000
    for _, row in hr_values.iterrows():
        text = row["Formula"]
        identifier = row["Identifier"]
        color = row["Color"]

        if identifier == "m-s":
            hr = (lc["Medium Count Rate"] - lc["Soft Count Rate"]) / (lc["Medium Count Rate"] + lc["Soft Count Rate"])
            plt.step(times, hr, color, where = "post", label = text)
        elif identifier == "h-s":
            hr = (lc["Hard Count Rate"] - lc["Soft Count Rate"]) / (lc["Hard Count Rate"] + lc["Soft Count Rate"])
            plt.step(times, hr, color, where = "post", label = text)
        elif identifier == "s-m-h":
            hr = (lc["Soft Count Rate"] - (lc["Medium Count Rate"] + lc["Hard Count Rate"])) / (lc["Soft Count Rate"] + (lc["Medium Count Rate"] + lc["Hard Count Rate"]))
            plt.step(times, hr, color, where = "post", label = text)
        elif identifier == "h-m-s-u":
            hr = ((lc["Soft Count Rate"] + lc["Ultrasoft Count Rate"]) - (lc["Hard Count Rate"] + lc["Medium Count Rate"])) / ((lc["Soft Count Rate"] + lc["Ultrasoft Count Rate"]) + (lc["Hard Count Rate"] + lc["Medium Count Rate"]))
            plt.step(times, hr, color, where = "post", label = text)

    if make_xlabel:
        plt.xlabel("Time (ks)", fontsize = 10)
    plt.ylabel(f"Hardness Ratio over {(lc['Time'].iloc[-1] - lc['Time'].iloc[-2]):.2f}s bins", fontsize = 10)
    plt.grid(True, which = "both", linestyle = "--", linewidth = 0.5)
    plt.tick_params(axis = "both", which = "major", labelsize = 10)

def bayesian_blocks_plotter(plt, times_array, bin_edges, color = "black", text = None, error_bar = False, linewidth = 1, make_xlabel = False):
    """Creates bayesian blocks segmented step plot of Count Rates= v/s Time. Plots thinner line in case of no error bars to increase visibility

    Args:
        plt (matplotlib.axes._axes.Axes/matplotlib.figure.Figure): MatPlotLib layer on which to plot data
        times (numpy.ndarray): Array of photon arrival times (s), typically 'time' column of event list, all values should be subtracted by 'tstart'
        bin_edges (numpy.ndarray): Array of bin edges created by bayesian blocks after likelihood merging (s), all values should be subtracted by 'tstart'
        color (str, optional): Color of the plot. Defaults to 'black'
        text (str, optional): The text to add as the label of the plot. Defaults to None
        error_bar (bool, optional): Whether to plot error bars or not. Defaults to False
        linewidth (int/float, optional): Width of the line of the plot, recommended to be lowered when plotting for multiple segmentation. Defaults to 1
        make_xlabel (bool, optional): Whether to write the x-axis label or not. Defaults to False

    Returns:
        tuple(np.ndarray, np.ndarray): Tuple of two arrays, one of the bayesian segmented counts, and the other of bayesian segmented count rates
    """

    time_intervals = np.diff(bin_edges)
    counts_bb, _ = histogram(times_array, bin_edges)
    count_rates = counts_bb / time_intervals
    errors = np.abs(np.sqrt(counts_bb) / time_intervals)

    bin_midpoints = (bin_edges[:-1] + bin_edges[1:]) / 2

    plt.step(bin_edges / 1000, np.append(count_rates, count_rates[-1]), where = "post", color = color, linestyle = "-", label = text, linewidth = linewidth)

    if error_bar:
        plt.errorbar(bin_midpoints / 1000, count_rates, yerr = errors, fmt = "none", ecolor = "orange", capsize = 2, capthick = 0.75, elinewidth = 0.75)
        plt.plot(bin_midpoints / 1000, count_rates, marker = "o", linestyle = "None", color = color, markersize = 3, markeredgewidth = 0.5, markeredgecolor = "black")
    
    if make_xlabel:
        plt.xlabel("Time (ks)", fontsize = 10)
    else:
        plt.ylabel("Count Rate (cts/s)", fontsize = 10)
    plt.grid(True, which = "both", linestyle = "--", linewidth = 0.5)
    plt.tick_params(axis = "both", which = "major", labelsize = 10)

    return counts_bb, count_rates

def plot_postage_stamps(obs_dir, obs_id, source, sky_image, detector_image, instrument, off_axis_angle = None, fig = None):
    """Generates plots of postage stamp images in sky and detector coordinates

    Args:
        obs_dir (str): Absolute path to directory where light curves are to be saved
        obs_id (str): The Obs. ID Number
        source (str): Name of source, preferably in J2000 sexagecimal format
        sky_image (str): Absolute path to sky image file
        detector_image (str): Absolute path to detector image file
        instrument(str): Which instrument's postage stamp ist to be plotted (ACIS/HRC)
        off_axis_angle (int/float, optional): Off-Axis angle to be displayed between both plots (arcmin). Defaults to None
        fig (matplotlib.axes._axes.Axes/matplotlib.figure.Figure, optional): MatPlotLib layer on which to plot data, if None, then images are saved as PNG
    """

    acis_res = 1/0.492
    hrc_res = 1/0.13175

    if instrument == "ACIS":
        res = acis_res
    else:
        res = hrc_res

    def get_bounds(hdu_list):
        bounds_table = Table.read(hdu_list["BOUNDS"])
        return {
            "x_min": float(bounds_table["X_MIN"][0]),
            "y_min": float(bounds_table["Y_MIN"][0]),
            "x_max": float(bounds_table["X_MAX"][0]),
            "y_max": float(bounds_table["Y_MAX"][0]),
        }
    
    def ticks_from_bounds(real_bounds, image_bounds, max_ticks = 10):
        start_tick, end_tick = real_bounds
        if end_tick == start_tick:
            return ([start_tick], [str(start_tick)])
        
        real_tick_positions = np.linspace(start_tick, end_tick, num = max_ticks)
        image_tick_positions = tuple(np.interp(tick, real_bounds, image_bounds) for tick in real_tick_positions)
        real_tick_labels = tuple(f"{tick:.0f}" for tick in real_tick_positions)
        return image_tick_positions, real_tick_labels

    sky_image_data = 255 - np.sqrt(fits.getdata(sky_image, ext = 0))
    detector_image_data = 255 - np.sqrt(fits.getdata(detector_image, ext = 0))

    if fig is not None:
        sky_image_plot, detector_image_plot = fig
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            sky_image_plot.tick_params(axis = "both", labelsize = 8)
            detector_image_plot.tick_params(axis = "both", labelsize = 8)
            
            sky_image_plot.set_xlabel("Sky X Pixel", fontsize = 10)
            sky_image_plot.set_ylabel("Sky Y Pixel", fontsize = 10)
            sky_image_plot.grid(True, linestyle = "-", color = "gray")
            sky_image_plot.imshow(sky_image_data, cmap = "gray", extent = [0, sky_image_data.shape[1], 0, sky_image_data.shape[0]], interpolation = "none")

            with fits.open(sky_image) as hdu:
                sky_bounds = get_bounds(hdu)

            sky_y_ticks = ticks_from_bounds((round(sky_bounds["y_min"]), round(sky_bounds["y_max"])), sky_image_plot.get_ylim())
            sky_x_ticks = ticks_from_bounds((round(sky_bounds["x_min"]), round(sky_bounds["x_max"])), sky_image_plot.get_xlim())
            sky_image_plot.set_yticks(*sky_y_ticks)
            sky_image_plot.set_xticks(*sky_x_ticks, rotation = 90)
            sky_image_plot.grid(True, which = "both", linestyle = "--", linewidth = 0.5)

            x_min, x_max = sky_image_plot.get_xlim()
            y_min, y_max = sky_image_plot.get_ylim()

            scale_bar_length = res
            pad_x = 0.02 * (x_max - x_min)
            pad_y = 0.02 * (y_max - y_min)

            scale_x_start = x_max - scale_bar_length - pad_x
            scale_x_end = x_max - pad_x
            scale_y = y_min + pad_y

            sky_image_plot.plot([scale_x_start, scale_x_end], [scale_y, scale_y], color = "red", linewidth = 2)
            sky_image_plot.text(scale_x_start, scale_y, "1 arcsec", color = "red", ha = "right", va = "bottom", fontsize = 8)
            
            detector_image_plot.set_xlabel("Detector X Pixel", fontsize = 10)
            detector_image_plot.set_ylabel("Detector Y Pixel", fontsize = 10)
            detector_image_plot.grid(True, linestyle = "-", color = "gray")
            detector_image_plot.imshow(detector_image_data, cmap = "gray", extent = [0, detector_image_data.shape[1], 0, detector_image_data.shape[0]], interpolation = "none")

            with fits.open(detector_image) as hdu:
                detector_bounds = get_bounds(hdu)

            detector_y_ticks = ticks_from_bounds((round(detector_bounds["y_min"]), round(detector_bounds["y_max"])), detector_image_plot.get_ylim())
            detector_x_ticks = ticks_from_bounds((round(detector_bounds["x_min"]), round(detector_bounds["x_max"])), detector_image_plot.get_xlim())
            detector_image_plot.set_yticks(*detector_y_ticks)
            detector_image_plot.set_xticks(*detector_x_ticks, rotation = 90)
            detector_image_plot.grid(True, which = "both", linestyle = "--", linewidth = 0.5)

            os.remove(sky_image)
            os.remove(detector_image)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            figure, (sky_image_plot, detector_image_plot) = plt.subplots(nrows = 2, ncols = 1, figsize = (5, 10), layout = "constrained")
            figure.subplots_adjust(wspace = 0.4)

            sky_image_plot.tick_params(axis = "both", labelsize = 8)
            detector_image_plot.tick_params(axis = "both", labelsize = 8)

            sky_image_plot.set_title(f"Off Axis Angle: {off_axis_angle}'", y = 1.02)
            sky_image_plot.set_xlabel("Sky X Pixel", fontsize = 10)
            sky_image_plot.set_ylabel("Sky Y Pixel", fontsize = 10)
            sky_image_plot.grid(True, linestyle = "-", color = "gray")
            sky_image_plot.imshow(sky_image_data, cmap = "gray", extent = [0, sky_image_data.shape[1], 0, sky_image_data.shape[0]])

            with fits.open(sky_image) as hdu:
                sky_bounds = get_bounds(hdu)

            sky_y_ticks = ticks_from_bounds((round(sky_bounds["y_min"]), round(sky_bounds["y_max"])), sky_image_plot.get_ylim())
            sky_x_ticks = ticks_from_bounds((round(sky_bounds["x_min"]), round(sky_bounds["x_max"])), sky_image_plot.get_xlim())
            sky_image_plot.set_yticks(*sky_y_ticks)
            sky_image_plot.set_xticks(*sky_x_ticks, rotation = 90)
            sky_image_plot.grid(True, which = "both", linestyle = "--", linewidth = 0.5)

            x_min, x_max = sky_image_plot.get_xlim()
            y_min, y_max = sky_image_plot.get_ylim()

            scale_bar_length = res
            pad_x = 0.02 * (x_max - x_min)
            pad_y = 0.02 * (y_max - y_min)

            scale_x_start = x_max - scale_bar_length - pad_x
            scale_x_end = x_max - pad_x
            scale_y = y_min + pad_y

            sky_image_plot.plot([scale_x_start, scale_x_end], [scale_y, scale_y], color = "red", linewidth = 2)
            sky_image_plot.text(scale_x_start, scale_y, "1 arcsec", color = "red", ha = "right", va = "bottom", fontsize = 8)

            detector_image_plot.set_xlabel("Detector X Pixel", fontsize = 10)
            detector_image_plot.set_ylabel("Detector Y Pixel", fontsize = 10)
            detector_image_plot.grid(True, linestyle = "-", color = "gray")
            detector_image_plot.imshow(detector_image_data, cmap = "gray", extent = [0, detector_image_data.shape[1], 0, detector_image_data.shape[0]])

            with fits.open(detector_image) as hdu:
                detector_bounds = get_bounds(hdu)

            detector_y_ticks = ticks_from_bounds((round(detector_bounds["y_min"]), round(detector_bounds["y_max"])), detector_image_plot.get_ylim())
            detector_x_ticks = ticks_from_bounds((round(detector_bounds["x_min"]), round(detector_bounds["x_max"])), detector_image_plot.get_xlim())
            detector_image_plot.set_yticks(*detector_y_ticks)
            detector_image_plot.set_xticks(*detector_x_ticks, rotation = 90)
            detector_image_plot.grid(True, which = "both", linestyle = "--", linewidth = 0.5)

            os.remove(sky_image)
            os.remove(detector_image)
            figure.savefig(os.path.join(obs_dir, f"{source}_{obs_id}.png"), dpi = 300, bbox_inches = "tight")
            plt.close(figure)