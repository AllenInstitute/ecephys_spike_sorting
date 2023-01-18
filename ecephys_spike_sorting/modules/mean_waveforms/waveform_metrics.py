import numpy as np
import random
import pandas as pd

from scipy.stats import linregress
from scipy.signal import resample

def calculate_waveform_metrics(waveforms, 
                               cluster_id, 
                               peak_channel, 
                               channel_map, 
                               sample_rate, 
                               upsampling_factor, 
                               spread_threshold,
                               site_range,
                               site_spacing,
                               epoch_name):
    
    """
    Calculate metrics for an array of waveforms.

    Metrics come from Jia et al. (2019) High-density extracellular probes reveal 
    dendritic backpropagation and facilitate neuron classification. J Neurophys

    https://doi.org/10.1152/jn.00680.2018


    Inputs:
    -------
    waveforms : numpy.ndarray (num_spikes x num_channels x num_samples)
        Can include NaN values for missing spikes
    cluster_id : int
        ID for cluster
    peak_channel : int
        Location of waveform peak
    channel_map : numpy.ndarray
        Channels used for spike sorting
    sample_rate : float
        Sample rate in Hz
    upsampling_factor : float
        Relative rate at which to upsample the spike waveform
    spread_threshold : float
        Threshold for computing spread of 2D waveform
    site_range : float
        Number of sites to use for 2D waveform metrics
    site_spacing : float
        Average vertical distance between sites (m)

    Outputs:
    -------
    metrics : pandas.DataFrame
        Single-row table containing all metrics

    """

    snr = calculate_snr(waveforms[:, peak_channel, :])

    mean_2D_waveform = np.squeeze(np.nanmean(waveforms[:, channel_map, :], 0))
    local_peak = np.argmin(np.abs(channel_map - peak_channel))

    num_samples = waveforms.shape[2]
    new_sample_count = int(num_samples * upsampling_factor)

    mean_1D_waveform = resample(
        mean_2D_waveform[local_peak, :], new_sample_count)

    timestamps = np.linspace(0, num_samples / sample_rate, new_sample_count)

    duration = calculate_waveform_duration(mean_1D_waveform, timestamps)
    halfwidth = calculate_waveform_halfwidth(mean_1D_waveform, timestamps)
    PT_ratio = calculate_waveform_PT_ratio(mean_1D_waveform)
    repolarization_slope = calculate_waveform_repolarization_slope(
        mean_1D_waveform, timestamps)
    recovery_slope = calculate_waveform_recovery_slope(
        mean_1D_waveform, timestamps)

    amplitude, spread, velocity_above, velocity_below = calculate_2D_features(
        mean_2D_waveform, timestamps, local_peak, spread_threshold, site_range, site_spacing)

    data = [[cluster_id, epoch_name, peak_channel, snr, duration, halfwidth, PT_ratio, repolarization_slope,
              recovery_slope, amplitude, spread, velocity_above, velocity_below]]

    metrics = pd.DataFrame(data,
                           columns=['cluster_id', 'epoch_name', 'peak_channel', 'snr', 'duration', 'halfwidth',
                                     'PT_ratio', 'repolarization_slope', 'recovery_slope', 'amplitude',
                                     'spread', 'velocity_above', 'velocity_below'])

    return metrics

def calculate_waveform_metrics_from_avg(avg_waveform,
                                        snr,
                                        cluster_id, 
                                        peak_channel, 
                                        channel_map, 
                                        sample_rate, 
                                        upsampling_factor, 
                                        spread_threshold,
                                        site_range,
                                        site_x, site_y):

    """
    Calculate metrics for an array of waveforms for a single cluster.

    Metrics come from Jia et al. (2019) High-density extracellular probes reveal 
    dendritic backpropagation and facilitate neuron classification. J Neurophys

    https://doi.org/10.1152/jn.00680.2018


    Inputs:
    -------
    avg_waveform : numpy.ndarray (num_channels x num_samples)
        from C_waves output
    snr : from C_waves output
    cluster_id : int
        ID for cluster
    peak_channel : int
        Location of waveform peak, read from C_waves input clus_Table
    channel_map : numpy.ndarray
        Channels used for spike sorting
    sample_rate : float
        Sample rate in Hz
    upsampling_factor : float
        Relative rate at which to upsample the spike waveform
    spread_threshold : float
        Threshold for computing spread of 2D waveform
    site_range : float
        Number of sites to use for 2D waveform metrics
    site_x, site_y : channel positions in um

    Outputs:
    -------
    metrics : pandas.DataFrame
        Single-row table containing all metrics

    """

    # snr = calculate_snr(waveforms[:, peak_channel, :])
    
    # calulating from average waveforms drawn from whole session
    epoch_name = 'complete_session'
    
    # all metric calculations are restricted to the channesl in the map
    # jic removed this -- we need to sample all channels for 2D calculations
    # moreover, this is assumed in the stnadard Allen calculation
    # mean_2D_waveform = np.squeeze(avg_waveform[channel_map, :])
    # local_peak = np.argmin(np.abs(channel_map - peak_channel))
    mean_2D_waveform = avg_waveform
    local_peak = peak_channel

    num_samples = mean_2D_waveform.shape[1]
    new_sample_count = int(num_samples * upsampling_factor)

    mean_1D_waveform = resample(
        mean_2D_waveform[local_peak, :], new_sample_count)

    timestamps = np.linspace(0, num_samples / sample_rate, new_sample_count)

    duration = calculate_waveform_duration(mean_1D_waveform, timestamps)
    halfwidth = calculate_waveform_halfwidth(mean_1D_waveform, timestamps)
    PT_ratio = calculate_waveform_PT_ratio(mean_1D_waveform)
    repolarization_slope = calculate_waveform_repolarization_slope(
        mean_1D_waveform, timestamps)
    recovery_slope = calculate_waveform_recovery_slope(
        mean_1D_waveform, timestamps)

    amplitude, spread, velocity_above, velocity_below = calculate_2D_features(
        mean_2D_waveform, timestamps, local_peak, site_x, site_y, spread_threshold, site_range)

    data = [[cluster_id, epoch_name, peak_channel, snr, duration, halfwidth, PT_ratio, repolarization_slope,
              recovery_slope, amplitude, spread, velocity_above, velocity_below]]

    metrics = pd.DataFrame(data,
                           columns=['cluster_id', 'epoch_name', 'peak_channel', 'snr', 'duration', 'halfwidth',
                                     'PT_ratio', 'repolarization_slope', 'recovery_slope', 'amplitude',
                                     'spread', 'velocity_above', 'velocity_below'])

    return metrics

# ==========================================================

# EXTRACTING 1D FEATURES

# ==========================================================


def calculate_snr(W):
    
    """
    Calculate SNR of spike waveforms.

    Converted from Matlab by Xiaoxuan Jia

    ref: (Nordhausen et al., 1996; Suner et al., 2005)

    Input:
    -------
    W : array of N waveforms (N x samples)

    Output:
    snr : signal-to-noise ratio for unit (scalar)

    """

    W_bar = np.nanmean(W, axis=0)
    A = np.max(W_bar) - np.min(W_bar)
    e = W - np.tile(W_bar, (np.shape(W)[0], 1))
    snr = A/(2*np.nanstd(e.flatten()))

    return snr


def calculate_waveform_duration(waveform, timestamps):
    
    """ 
    Duration (in seconds) between peak and trough

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)
    timestamps : numpy.ndarray (N samples)

    Outputs:
    --------
    duration : waveform duration in milliseconds

    """

    trough_idx = np.argmin(waveform)
    peak_idx = np.argmax(waveform)

    # to avoid detecting peak before trough
    if waveform[peak_idx] > np.abs(waveform[trough_idx]):
        duration =  timestamps[peak_idx:][np.where(waveform[peak_idx:]==np.min(waveform[peak_idx:]))[0][0]] - timestamps[peak_idx] 
    else:
        duration =  timestamps[trough_idx:][np.where(waveform[trough_idx:]==np.max(waveform[trough_idx:]))[0][0]] - timestamps[trough_idx] 

    return duration * 1e3


def calculate_waveform_halfwidth(waveform, timestamps):
    
    """ 
    Spike width (in seconds) at half max amplitude

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)
    timestamps : numpy.ndarray (N samples)

    Outputs:
    --------
    halfwidth : waveform halfwidth in milliseconds

    """

    trough_idx = np.argmin(waveform)
    peak_idx = np.argmax(waveform)

    try:
        if waveform[peak_idx] > np.abs(waveform[trough_idx]):
            threshold = waveform[peak_idx] * 0.5
            thresh_crossing_1 = np.min(
                np.where(waveform[:peak_idx] > threshold)[0])
            thresh_crossing_2 = np.min(
                np.where(waveform[peak_idx:] < threshold)[0]) + peak_idx
        else:
            threshold = waveform[trough_idx] * 0.5
            thresh_crossing_1 = np.min(
                np.where(waveform[:trough_idx] < threshold)[0])
            thresh_crossing_2 = np.min(
                np.where(waveform[trough_idx:] > threshold)[0]) + trough_idx

        halfwidth = (timestamps[thresh_crossing_2] - timestamps[thresh_crossing_1]) 

    except ValueError:

        halfwidth = np.nan

    return halfwidth * 1e3


def calculate_waveform_PT_ratio(waveform):

    """ 
    Peak-to-trough ratio of 1D waveform

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)

    Outputs:
    --------
    PT_ratio : waveform peak-to-trough ratio

    """

    trough_idx = np.argmin(waveform)

    peak_idx = np.argmax(waveform)

    PT_ratio = np.abs(waveform[peak_idx] / waveform[trough_idx])

    return PT_ratio


def calculate_waveform_repolarization_slope(waveform, timestamps, window=20):
    
    """ 
    Spike repolarization slope (after maximum deflection point)

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)
    timestamps : numpy.ndarray (N samples)
    window : int
        Window (in samples) for linear regression

    Outputs:
    --------
    repolarization_slope : slope of return to baseline (V / s)

    """

    max_point = np.argmax(np.abs(waveform))

    waveform = - waveform * (np.sign(waveform[max_point])) # invert if we're using the peak

    repolarization_slope = linregress(timestamps[max_point:max_point+window], waveform[max_point:max_point+window])[0]

    return repolarization_slope * 1e-6



def calculate_waveform_recovery_slope(waveform, timestamps, window=20):

    """ 
    Spike recovery slope (after repolarization)

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)
    timestamps : numpy.ndarray (N samples)
    window : int
        Window (in samples) for linear regression

    Outputs:
    --------
    recovery_slope : slope of recovery period (V / s)

    """

    max_point = np.argmax(np.abs(waveform))

    waveform = - waveform * (np.sign(waveform[max_point])) # invert if we're using the peak

    peak_idx = np.argmax(waveform[max_point:]) + max_point

    recovery_slope = linregress(timestamps[peak_idx:peak_idx+window], waveform[peak_idx:peak_idx+window])[0]

    return recovery_slope * 1e-6


# ==========================================================

# EXTRACTING 2D FEATURES

# ==========================================================


def calculate_2D_features(waveform, timestamps, peak_channel, site_x, site_y, spread_threshold = 0.12, site_range=16):
    
    """ 
    Compute features of 2D waveform (channels x samples)

    Inputs:
    ------
    waveform : numpy.ndarray (N channels x M samples)
    timestamps : numpy.ndarray (M samples)
    peak_channel : int
    spread_threshold : float
    site_range: int
    site_x, site_y : float

    Outputs:
    --------
    amplitude : uV
    spread : um
    velocity_above : s / m
    velocity_below : s / m

    """

    assert site_range % 2 == 0 # must be even
    
    # sample sites that are in the same "column" as the peak channel
    # first find nn with y ~= y_peak
    # x = x_peak or x_nn. For NP 1.0, this will select either the 
    # two left or two right hand columns.
    
    dist = np.sqrt(( pow((site_x - site_x[peak_channel]),2) + pow((site_y - site_y[peak_channel]),2)))
    ydiff = ( site_y != site_y[peak_channel])
    n_channel = site_x.size
    min_dist = 1e6   # a value larger than the  distance to nn
    x_nn = -1
    amp_nn = 0
    x_peak = site_x[peak_channel]
    
    for i in range(n_channel):
        if ydiff[i] and dist[i] <= min_dist:  #only consider nn at diff y
            min_dist = dist[i]
            # to break ties between columns at the same distance, pick nn with
            # largest amplitude
            currAmp = np.max(waveform[i,:]) - np.min(waveform[i,:])
            if currAmp > amp_nn:
                x_nn = site_x[i]
            
    # select among sites with x = x_peak and x_nn for sites to sample
    inCol = (site_x == x_peak) | (site_x == x_nn)   
    sort_dist_ind = np.argsort(dist)
    sites_to_sample = np.zeros(site_range+1, dtype='int32')
    
    nfound = 0
    i = 0
    # walk over all sites in order of distance from the peak_channel, add to
    # list of channels to sample
    while nfound < site_range and i < n_channel:
        curr_chan = sort_dist_ind[i]
        if inCol[curr_chan]:
            sites_to_sample[nfound] = curr_chan
            nfound = nfound + 1           
            # print('site, dist: ' + repr(curr_chan) + ',' + repr(dist[curr_chan]))
        i = i+1
            
    
    # original implentation for NP 1.0, assuming all sites in one bank, pick 
    # even or odd sites 
    # sites_to_sample = np.arange(-site_range, site_range+1, 2) + peak_channel
    # sites_to_sample = sites_to_sample[(sites_to_sample > 0) * (sites_to_sample < waveform.shape[0])]

    # take only as many sites as we "found"
    sites_to_sample = sites_to_sample[0:nfound]
    wv = waveform[sites_to_sample, :]

    #smoothed_waveform = np.zeros((wv.shape[0]-1,wv.shape[1]))
    #for i in range(wv.shape[0]-1):
    #    smoothed_waveform[i,:] = np.mean(wv[i:i+2,:],0)

    trough_idx = np.argmin(wv, 1)
    trough_amplitude = np.min(wv, 1)

    peak_idx = np.argmax(wv, 1)
    peak_amplitude = np.max(wv, 1)

    duration = np.abs(timestamps[peak_idx] - timestamps[trough_idx])

    overall_amplitude = peak_amplitude - trough_amplitude
    amplitude = np.max(overall_amplitude)
    max_chan = np.argmax(overall_amplitude)

    points_above_thresh = np.where(overall_amplitude > (amplitude * spread_threshold))[0]
    
    if len(points_above_thresh) > 1:
        points_above_thresh = points_above_thresh[isnot_outlier(points_above_thresh)]
        
    yDist = site_y[sites_to_sample] - site_y[peak_channel]
    yDist = yDist[points_above_thresh]
    
    # debug print to understand what sites are selected
#    for i in range(numpts):
#        print('i, ydist:' + repr(i) + ', ' + repr(yDist[i]))
    if len(yDist) > 0:
        spread = np.max(yDist) - np.min(yDist)
    else:
        spread = 0

    # original channel based calculation of spread
    
    # spread = len(points_above_thresh) * site_spacing * 1e6
    # channels = sites_to_sample - peak_channel
    # channels = channels[points_above_thresh]

    trough_times = timestamps[trough_idx] - timestamps[trough_idx[max_chan]]
    trough_times = trough_times[points_above_thresh]

    velocity_above, velocity_below = get_velocity(yDist, trough_times)
 
    return amplitude, spread, velocity_above, velocity_below


# ==========================================================

# HELPER FUNCTIONS:

# ==========================================================


def get_velocity(yDist, times):
    
    """
    Calculate slope of trough time above and below soma.

    Inputs:
    -------
    yDist : np.ndarray
        distance of site to soma, in um
    times : np.ndarray
        Trough time relative to peak channel

    Outputs:
    --------
    velocity_above : float
        Inverse of velocity of spike propagation above the soma (s / m)
    velocity_below : float
        Inverse of velocity of spike propagation below the soma (s / m)

    """
    
    above_soma = yDist >= 0
    below_soma = yDist <= 0
    
    if np.sum(above_soma) > 1:
        spread = np.max(yDist[above_soma]) - np.min(yDist[above_soma])  
    else:
        spread = 0
        
    if spread > 0:
        slope_above, intercept, r_value, p_value, std_err = linregress(yDist[above_soma], times[above_soma])
        velocity_above = slope_above * 1e6     #convert slope to s / m
    else:
        velocity_above = np.nan
    
    if np.sum(below_soma) > 1:  
        spread = np.max(yDist[below_soma]) - np.min(yDist[below_soma])
    else:
        spread = 0
        
    if spread > 0:
        slope_below, intercept, r_value, p_value, std_err = linregress(yDist[below_soma], times[below_soma])
        velocity_below = slope_below * 1e6     #convert slope to s / m
    else:
        velocity_below = np.nan

    return velocity_above, velocity_below


def isnot_outlier(points, thresh=1.5):

    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """

    if len(points.shape) == 1:
        points = points[:,None]

    median = np.median(points, axis=0)
    
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score <= thresh
