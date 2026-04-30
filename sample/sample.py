#! /usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, freqz
import pandas as pd
import matplotlib.lines as mlines

def calculate_rms_difference(breath_signal):
    num_points = len(breath_signal)
    middle_half_start = num_points // 4  # Starting index of the middle half
    middle_half_end = num_points * 3 // 4  # Ending index of the middle half

    # print("start ----- %d " %(middle_half_start))
    # print("end ----- %d " %(middle_half_end))

    middle_half = breath_signal[middle_half_start:middle_half_end]  # Extract the middle half of the signal
    differences = middle_half - 1  # Calculate the differences from one

    # print(middle_half)

    squared_differences = differences ** 2  # Square the differences
    mean_squared_difference = np.mean(squared_differences)  # Compute the mean of squared differences
    rms_difference = np.sqrt(mean_squared_difference)  # Calculate the square root to obtain RMS
   
    return rms_difference

def single_breath_flatten_detection(ins_start, ins_end, signal):
    ins_first_breath = signal[ins_start:ins_end]
    t_ins = np.arange(0, len(ins_first_breath), 1)
    #### Step 3 : Trim any trailing or leading pause as required.
    
    #### Step 4: Interpolate the N points.
    # Interpolate 65 points
    interpolated_points = np.interp(
        np.linspace(0, len(ins_first_breath) - 1, 65),  # Generate indices for interpolation
        range(len(ins_first_breath)),  # Original indices
        ins_first_breath  # Original array
    )

    #### Step 5: Divide the point y values by a factor such that the breath area is normalized to one with unity base length.
    factor = np.trapz(interpolated_points)
    factor = factor / 64
    normalized_interpolated_value = interpolated_points / factor

    #### Step 4: Interpolate the N points.
    sbf_index = calculate_rms_difference(normalized_interpolated_value)

    return sbf_index

def sbf_moving_average(data, window_size):
    # Convert array of integers to pandas series
    numbers_series = pd.Series(data)
    
    # Get the window of series
    # of observations of specified window size
    windows = numbers_series.rolling(window_size)
    
    # Create a series of moving
    # averages of each window
    moving_averages = windows.mean()
    
    # Convert pandas series back to list
    moving_averages_list = moving_averages.tolist()
    
    # Remove null entries from the list
    signal = moving_averages_list[window_size - 1:]

    return signal

def sbf_get_step(sbf_idx, curr_value, fl_max_idx):
    step = 0
    if sbf_idx > float(0.27) or curr_value > fl_max_idx:
        if curr_value > (fl_max_idx / 3):
            step = -(fl_max_idx / 3)
        elif curr_value > 0.0:
            step = -curr_value
        else:
            step = 0.0

    elif float(0.1) < sbf_idx and sbf_idx < float(0.27) and curr_value < float(fl_max_idx):
        step = (fl_max_idx / 3)
    elif float(0.0) < sbf_idx and sbf_idx < float(0.1) and curr_value < float(fl_max_idx):
        step = 2*(fl_max_idx / 3)
    else:
        step = 0

    return step

def sbf_fill_ffl(data_in, points, sbf_idx, ventilation_breaths):
    data_out = data_in
    starts = points[0:len(points):2]
    ends = points[1:len(points):2]
    
    # for start, end in zip(starts, ends):
    i = 1
    j = 0
    counter = 0
    # if (len(starts) > 0):
    #     start = starts[0]
    #     del starts[0]
    prev_step = float(0.0)

    #
    # Vnormal breath
    #
    Vcurr = 0
    vent_idx = 0
    Vnorm = ventilation_breaths[vent_idx]
    fl_max_idx = 0

    while i < len(data_in) and j < len(starts):

        if i == starts[j]:
            if (j < len(sbf_idx)):
                sbf = sbf_idx[j]
            else:
                sbf = 1.0

            #
            # if it is normal breath.
            #
            vent_idx += 1
            if (vent_idx < len(ventilation_breaths)):
                Vcurr = ventilation_breaths[vent_idx]
                if (sbf > 0.27):
                    Vnorm = (Vnorm + ventilation_breaths[vent_idx]) / 2
                else:
                    temp_fl_max_idx = Vcurr / Vnorm
                    if temp_fl_max_idx < 1:
                        fl_max_idx = temp_fl_max_idx
                    print("Flow limit idx maximun %f" %(fl_max_idx))

           
            step = sbf_get_step(sbf, data_out[i - 1], fl_max_idx)

            # Using 2 continuous steps to decide increment of value.
            if (prev_step == float(0.0)) and step > float(0.0):
                prev_step = step
                data_out[i] = data_out[i - 1]
            elif(prev_step > float(0.0)) and step > float(0.0):
                data_out[i] = data_out[i - 1] + step
                prev_step = float(0.0)
            elif step < float(0.0):
                data_out[i] = data_out[i - 1] + step
                prev_step = float(0.0)
            else:
                data_out[i] = data_out[i - 1]
                prev_step = float(0.0)

            j = j + 1
        else:
            counter = 0
            data_out[i] = data_out[i - 1]

        i = i + 1

    return data_out

# signal = fl_read_data("data/flow_limit.data")

def fl_sbf(zero_crossings, signal):
    d_ins_start = zero_crossings[0:len(zero_crossings):2]
    d_ins_end = zero_crossings[1:len(zero_crossings):2]

    count = 0
    sbf_idx = []
    fl_points = []
    # normal_points = []
    for start, end in zip(d_ins_start, d_ins_end):
        d_m_index = single_breath_flatten_detection(start, end, signal)
        sbf_idx.append(d_m_index)
        # normal_points.append(start)
        # normal_points.append(end)
        if (d_m_index < 0.27):
            count = count + 1
            fl_points.append(start)
            fl_points.append(end)
            print("%d. SBF index with flow limitation %f (start %d, end %d) " % (count, d_m_index, start, end))
    return sbf_idx, fl_points

def fl_ventiation(zero_crossings, signal):
    d_ins_start = zero_crossings[0:len(zero_crossings):2]
    d_ins_end = zero_crossings[1:len(zero_crossings):2]

    ventilation_value = []
    for start, end in zip(d_ins_start, d_ins_end):
        ins_time = signal[start:end]
        # value = sum(ins_time)
        # # value = value * (end - start)
        # value = value
        value = np.mean(ins_time)
        value = value * (end - start)
        ventilation_value.append(value)

    return ventilation_value

def fl_step_solution3(zero_crossings, sbf_idx, signal, ventilation_breaths):
    #
    # Create moving average for SBF index.
    #
    avg_sbf_idx = sbf_moving_average(sbf_idx, 3)
    avg_sbf_t = np.arange(0, len(avg_sbf_idx), 1)


    flow_limitation_data = [ 0 ] * len(signal)

    ffl_values = sbf_fill_ffl(flow_limitation_data, zero_crossings, sbf_idx, ventilation_breaths)
    return ffl_values
