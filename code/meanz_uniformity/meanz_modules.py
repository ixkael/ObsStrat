# Collecting Routines for use in MAF analysis
# Code written by:
# R. Mandelbaum
# R. Hlozek
# Rubin Sim Notebooks contributors https://github.com/lsst/rubin_sim_notebooks/graphs/contributors
# A. Kannawadi

import os
import numpy as np
import matplotlib.pyplot as plt
import healpy as hp
import pandas as pd
import sqlite3
import rubin_sim
import rubin_sim.maf as maf
from rubin_sim.scheduler.utils import SkyAreaGenerator
from rubin_sim.data import get_baseline
import scipy.special as sc

def load_maf_map(fname,nside=64):
    surveyAreas = SkyAreaGenerator(nside=nside)
    map_footprints, map_labels = surveyAreas.return_maps()
    fin = maf.MetricBundle(
        metric=maf.ExgalM5(),
        slicer=maf.HealpixSubsetSlicer(nside=nside, use_cache=False, hpid=np.where(map_labels == "lowdust")[0]),
        constraint='note not like "DD%" and note not like "twilight_near_sun"'
    )
    fin._setup_metric_values()
    #counts/map values
    opmap=fin.metric_values
    mafmap=np.copy(opmap.data)
    mafmap[opmap.mask]=0
    mafmap[mafmap>0]=1
    
    return mafmap

def maf_maps_to_fits(fname_in, fname_out,nside=64):
    usemap = load_maf_map(fname_in,nside=nside)
    # save this into fits file:
    hp.write_map(fname_out, usemap, overwrite=True)
    print("Written: %s"%fname_out)


# Here we define a function for some of the metric plots we want to show.
# TO DO: need to rename this function since it doesn't actually always plot the metrics
def metric_plots(use_run_name, use_opsim_fname, use_metric=maf.ExgalM5(), use_color_min=None, use_color_max=None,
                year=10,nside=64, use_filter="i", return_map=False):
    # use_run_name says which OpSim DB we want to use, e.g. `baseline_v2.1_10yrs` - will also be used for labels
    # use_opsim_fname says where it lives, e.g. `/global/cfs/cdirs/lsst/groups/CO/rubin_sim/sim_baseline/baseline_v2.1_10yrs.db`
    surveyAreas = SkyAreaGenerator(nside=nside)
    map_footprints, map_labels = surveyAreas.return_maps()
    days = year*365.25
    # Here the constraint on use of i-band data, exclusion of DDFs, time limitations, and avoiding twilight exposures 
    constraint_str='filter="YY" and note not like "DD%" and night <= XX and note not like "twilight_near_sun" '
    constraint_str = constraint_str.replace('XX','%d'%days)
    constraint_str = constraint_str.replace('YY','%s'%use_filter)
    
    # Just some optional plotting stuff
    if use_color_min is not None and use_color_max is not None:
        plot_dict={"color_min": use_color_min, "color_max": use_color_max, "x_min": use_color_min, "x_max": use_color_max}
    else:
        plot_dict=None
        
    # Decide what summary statistics we want
    my_summary_stats = [maf.MedianMetric(), maf.MeanMetric(), maf.RmsMetric(), maf.PercentileMetric(percentile=25), maf.PercentileMetric(percentile=75)]
    
    # First, define a MetricBundle object.
    depth_map_bundle = maf.MetricBundle(
        metric=use_metric,
        # Exclude the galactic plane
        slicer=maf.HealpixSubsetSlicer(nside=nside, use_cache=False, hpid=np.where(map_labels == "lowdust")[0]),
        constraint=constraint_str,
        run_name=use_run_name,
        summary_metrics=my_summary_stats,
        plot_dict=plot_dict
    )
    
    bd = maf.metricBundles.make_bundles_dict_from_list([depth_map_bundle])
    bgroup = maf.MetricBundleGroup(
        bd, use_opsim_fname
    )
    bgroup.run_all()
    
    if return_map:
        map= depth_map_bundle.metric_values
        output_map = np.copy(map.data)
        output_map[map.mask] = 0
        return bgroup, bd, output_map
    else:
        return bgroup, bd

def coeff_solve(ilim,meanz):

    from scipy.optimize import curve_fit
    ((a, b), _) = curve_fit(lambda x,a,b:3*a*x+3*b, ilim, meanz)
    return a, b

def p(z, ilim, a=0.044444444444444446, b=-0.7644444444444444):
    z0 = a*ilim + b
    return 0.5/z0*(z/z0)*(z/z0)*np.exp(-z/z0)



def percentile_bin_boundaries(*, ilim, num_bins=5, a=0.044444444444444446, b=-0.7644444444444444, **kwargs):
    """Return the tomographic bin boundaries.
    
    The number of returned values will be one more than ``num_bins``.
    The first entry should always be 0 and the last entry should be np.inf.
    """
    z0 = a*ilim + b
    return sc.gammaincinv(3, np.arange(0, 1 + 0.1/num_bins, 1./num_bins))*z0

def fixed_bin_boundaries(*, num_bins=5, zmin=0, zmax=2, a=0.044444444444444446, b=-0.7644444444444444, **kwargs):
    return np.linspace(zmin, zmax, num_bins+1)


def mean_z(ilim, num_bins=5,a=0.044444444444444446, b=-0.7644444444444444, tomographic_bin_boundaries=percentile_bin_boundaries, **kwargs):
    """Compute the mean redshift for each tomographic bin
    given the limiting i-band magnitude.
    
    This function uses the already calibrated value for z_0,
    but can be overridden by passing in the a and b coefficients,
    optionally.
    
    Parameters
    ----------
    ilim: `float`
        The limiting magnitude in i-band
    num_bins: `int`
        Number of tomographic bins
    a: `float`, optional
        The coefficient in z0 = a*ilim + b
    b: `float`, optional
        The offset in z0 = a*ilim + b
    tomographic_bin_boundaries: `Callable`
        A function that gives the edges of the tomographic bins.
        Additional arguments to pass to ``tomographic_bin_boundaries``
        can be passed as keyword arguments.
        
    Returns
    -------
    mean_z: `list` [`float`]
        A list of ``num_bins`` in length with mean redshift in each tomographic bin defined
        by ``tomographic_bin_boundaries``.
    """
    z0 = a*ilim + b
    t_edges = tomographic_bin_boundaries(ilim=ilim, num_bins=num_bins, a=a, b=b, **kwargs)/z0
    t_bins = zip(t_edges[:-1], t_edges[1:])
    return [3*z0*(sc.gammainc(4, t2)-sc.gammainc(4, t1))/(sc.gammainc(3, t2)-sc.gammainc(3, t1)) for (t1,t2) in t_bins]

def sensitivity(num_bins, fiducial_ilim=24.1, a=0.044444444444444446, b=-0.7644444444444444, tomographic_bin_boundaries=percentile_bin_boundaries, **kwargs):
    """Sensitivity of mean redshift to limiting magnitude (d<z>/dilim)
    
    Parameters
    ----------
    num_bins: `int`
        Number of tomographic bins
    fiducial_ilim: `float`, optional
        The fiducial limiting magnitude at which to calculate the sensitivity.
    a: `float`, optional
        The coefficient in z0 = a*ilim + b
    b: `float`, optional
        The offset in z0 = a*ilim + b
    tomographic_bin_boundaries: `Callable`
        A function that gives the edges of the tomographic bins.
        Additional arguments to pass to ``tomographic_bin_boundaries``
        can be passed as keyword arguments.
        
    Returns
    -------
    sensitivity: `list` [`float`]
        The derivative of mean_z wrt ilim for each tomographic bin defined
        by ``tomographic_bin_boundaries``.
    """
    z0 = a*fiducial_ilim + b
    t_edges = tomographic_bin_boundaries(num_bins=num_bins, ilim=fiducial_ilim, **kwargs)/z0
    t_bins = zip(t_edges[:-1], t_edges[1:])
    return [3*a*(sc.gammainc(4, t2)-sc.gammainc(4, t1))/(sc.gammainc(3, t2)-sc.gammainc(3, t1)) for t1,t2 in t_bins]

def my_total_power_metric(map, ell_max=30):
    mean_val = np.mean(map[map>0])
    map[map>0] -= mean_val
        
    cl = hp.anafast(map)
    ell = np.arange(np.size(cl))
    return np.sum((2*ell[ell<ell_max]+1)*cl[ell<ell_max])

# A utility to plot summary stats for strategies as a function of year, given a dataframe from the above routines.
def plot_metric_by_year(df, stat_name, y_axis_label=None):
    year_vals = np.array(list(set(df['Year'])))
    strategies=list(set(df['Strategy']))
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Offset axes:
    offsets = 0.05*np.arange(0,len(strategies))
    offsets -= np.mean(offsets)
    offset_index = 0

    # y-axis label handling
    if y_axis_label is None:
        y_axis_label = stat_name

        
    ## put in line style stuff
    for s in strategies:
        yvals = np.array(df[stat_name][df['Strategy']==s])
        ax.plot(year_vals+offsets[offset_index], yvals, label=s)
        offset_index += 1
    plt.xlabel('Year')
    plt.ylabel(y_axis_label)
    plt.legend()
    plt.show()
    
# A utility to plot summary stats for strategies as a function of year, given a dataframe from the above routines.
def plot_meanz_metrics_by_year(df, years, num_bins=5,y_axis_label=None):
    year_vals = years
    strategies=list(set(df['Strategy']))
    # fig = plt.figure()
    # ax = fig.add_subplot(111)

    # Offset axes:
    offsets = 0.01*np.arange(0,len(strategies))
    offsets -= np.mean(offsets)
    offset_index = 0

    # y-axis label handling
    if y_axis_label is None:
        y_axis_label = 'Mean z'

    ls = ['--','-',':','-.','-']
    lw = [1,2,2,2,1]
        
    ## put in line style stuff
    cols = ['r','g','k','c','m', 'lightcoral', 'mediumpurple','deepskyblue','teal','forestgreenß']
    offset = 0.05
    fig, axs = plt.subplots(len(year_vals),2,sharex=True)
  
    for sy,year in enumerate(year_vals):
        axs[sy][0].set_title(f'Year {year}')
        axs[sy][1].set_title(f'Year {year}')
        for scount,s in enumerate(strategies):
            for bin in range(num_bins):
                
                meanz=df['Mean z bin'][df['Strategy']==s][df['Year']==year].values[0][bin]
                stdz=df['Std z bin'][df['Strategy']==s][df['Year']==year].values[0][bin]
            
                if sy==0:
                    axs[sy][0].plot(bin+offset*scount,meanz, marker='*',label=s,color=cols[scount])
                    axs[sy][1].plot(bin+offset*scount,stdz, marker='*',label=s,color=cols[scount])
                else:
                    axs[sy][0].plot(bin+offset*scount,meanz, marker='*',color=cols[scount])
                    axs[sy][1].plot(bin+offset*scount,stdz, marker='*',color=cols[scount])
            
    #     axs[sy].set_ylabel(y_axis_label)

    axs[sy][0].set_xlabel('Bin')
    axs[sy][0].set_ylabel('Mean z')
    axs[sy][1].set_xlabel('Bin')
    axs[0][0].set_ylabel('Std z')
    # axs[0].legend()
    # axs[0].show()

# First define a routine to run across a list of years and produce a dataframe
def get_year_by_year_metrics(year_list, name_list, sim_list, use_filter="i"):
    overall_names = []
    overall_years = []
    overall_meds = []
    overall_means = []
    overall_std = []
    overall_iqr = []
    overall_meanzbins=[]
    overall_stdzbins=[]
    for year in year_list:
        for i in range(len(sim_list)):
            bgroup, bd = metric_plots(name_list[i], sim_list[i], year=year, use_filter=use_filter)
            overall_names.append(name_list[i]) # strategy name
            overall_years.append(year) 
            overall_meds.append(bd[list(bd.keys())[0]].summary_values['Median']) # median i-band mags
            overall_means.append(bd[list(bd.keys())[0]].summary_values['Mean'])   # mean i-band mags        
            overall_std.append(bd[list(bd.keys())[0]].summary_values['Rms']) # rms of the i-band mags
            overall_iqr.append(bd[list(bd.keys())[0]].summary_values['75th%ile']-bd[list(bd.keys())[0]].summary_values['25th%ile']) 
            overall_meanzbins.append(mean_z(ilim=bd[list(bd.keys())[0]].summary_values['Mean'], num_bins=5)) # mean z in each tomographic bin
            stdz = [float(sens)*float(bd[list(bd.keys())[0]].summary_values['Rms']) for sens in sensitivity(fiducial_ilim=float(bd[list(bd.keys())[0]].summary_values['Mean']), num_bins=5)]
            # multiply the sensitivity from Arun's code by the std of the i-band mag to get the std of the z in each bin
            overall_stdzbins.append(stdz)
            
    df = pd.DataFrame(list(zip(overall_names, overall_years, overall_meds, overall_means, overall_std, overall_iqr, overall_meanzbins,overall_stdzbins)), 
                  columns=['Strategy', 'Year', 'Median i-band depth', 'Mean i-band depth', 'Std i-band depth', 'IQR i-band depth', 'Mean z bin', 'Std z bin'])
    return df

# Define combined plotting routine - base it on Renee's
def combined_metric_plots(use_run_name_vec, use_opsim_fname_vec, 
                          use_metric=maf.ExgalM5(), year=10, use_color_min=None, use_color_max=None,nside=64):
    # use_run_name_vec says which OpSim DBs we want to use - will also be used for labels
    # use_opsim_fname_vec says where they live, e.g. one item might be `/global/cfs/cdirs/lsst/groups/CO/rubin_sim/sim_baseline/baseline_v2.1_10yrs.db`
    if use_color_min is not None and use_color_max is not None:
        plot_dict={"color_min": use_color_min, "color_max": use_color_max, "x_min": use_color_min, "x_max": use_color_max}
    else:
        plot_dict=None
    days = year*365.3
    constraint_str='filter="i" and note not like "DD%" and night <= XX and note not like "twilight_neo" '
    constraint_str = constraint_str.replace('XX','%d'%days)
    print(constraint_str)
    
    bg_list = []
    bd_list = []
    overall_plot_dict = {}
    color_list = ["k", "r", "b", "c", "g", "o", "m", "y"] # hopefully long enough to handle everything
    for i in range(len(use_run_name_vec)):
        use_run_name = use_run_name_vec[i]
        use_opsim_fname = use_opsim_fname_vec[i]
        print(use_run_name, use_opsim_fname)
        depth_map_bundle = maf.MetricBundle(
            metric=use_metric,
            slicer=maf.HealpixSubsetSlicer(nside=nside, use_cache=False, hpid=np.where(map_labels == "lowdust")[0]),
            constraint=constraint_str,
            run_name=use_run_name,
            summary_metrics=[maf.MedianMetric(), maf.MeanMetric(), maf.RmsMetric()],
            plot_dict=plot_dict
        )
        #print('Bundle diagnostics',depth_map_bundle.run_name, depth_map_bundle.metric.name, 
        #      depth_map_bundle.info_label, depth_map_bundle.slicer.slicer_name, depth_map_bundle.file_root)
        
        bd = maf.metricBundles.make_bundles_dict_from_list([depth_map_bundle])
        print(bd[list(bd.keys())[0]].summary_values)
        #bgroup = maf.MetricBundleGroup(
        #    bd, use_run_name, out_dir="./"
        #)
        #bgroup.run_all()
        
        #bg_list.append(bgroup)
        #bd_list.append(bd)
        #overall_plot_dict[use_run_name] = color_list[i]
    
    #ph = maf.PlotHandler()
    #ph.set_metric_bundles(bg_list)
    #ph.plot(plot_dicts=overall_plot_dict)
    #for i in range(len(bd_list)): print(use_opsim_fname_vec[i], year, bd_list[i][list(bd_list[i].keys())[0]].summary_values)
    #for tmpbd in bd_list: print(tmpbd[list(tmpbd.keys())[0]].summary_values)
 