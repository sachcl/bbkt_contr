#! /usr/bin/python
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt

from fl_load_data import *
from utils import *
from fl_breath_extraction import *

#
#
#
cutoff = 18
# Fs = 512
# Fs = 128

windows_length = 101
windows_step = 10

#
# Loading data.
#
# data_file = "data/snore_freq20_ampl03.data"       # 1.0
# data_file = "data/snore_freq20_ampl05.data"       # 2.0
# data_file = "data/snore_freq20_ampl10.data"       # 3.4
# data_file = "data/snore_freq20_ampl20.data"       # 4.9
# data_file = "data/snore_freq20_ampl40.data"       # 6.1   zero crossing work 
# data_file = "data/snore_freq20_ampl50.data"       # 6.7   

# data_file = "data/snore_freq20_ampl80.data"       # 7.7 
# data_file = "data/snore_freq20_ampl85.data"       # 7.8 

# data_file = "data/snore_freq30_ampl40.data"       # 7.6  zero crossing work 
# data_file = "data/snore_freq30_ampl80.data"       # 9.3

# data_file = "data/snore_freq40_ampl30.data"       # 7.4   zero crossing work 
# data_file = "data/snore_freq40_ampl60.data"       # 7.5   zero crossing work 
# data_file = "data/snore_freq40_ampl70.data"       # 9.3
# data_file = "data/snore_freq45_ampl80.data"       # 8.4   zero crossing work 

# data_file = "data/snore_flux_freq20_ampl05.data"       # 
# data_file = "data/snore_flux_freq20_ampl20.data"       # 
# data_file = "data/snore_flux_freq20_ampl40.data"       # 
# data_file = "data/snore_flux_freq20_ampl50.data"       # 

# data_file = "data/snore_flux_freq40_ampl70.data"       # 
# data_file = "data/snore_flux_freq45_ampl80.data"       # 

#
# Fsampling 128 Hz
#
# data_file = "data/snore_freq20_ampl05_sample128.data"       # 
# data_file = "data/snore_freq20_ampl20_sample128.data"       # 
# data_file = "data/snore_freq20_ampl50_sample128.data"       # 
# data_file = "data/snore_freq40_ampl70_sample128.data"       # 
data_file = "data/snore_freq20_ampl80_sample128.data"; Fs = 128       # 

#
# Fsampling 128 Hz
#
# data_file = "data/snore_freq20_ampl05_sample192.data"       # 
# data_file = "data/snore_freq20_ampl20_sample192.data"       # 
# data_file = "data/snore_freq20_ampl50_sample192.data"       # 
# data_file = "data/snore_freq40_ampl70_sample192.data"       # 

data = fl_read_data(data_file)
data = [x - 1 for x in data]


t = np.arange(0, len(data) * (1 / Fs), 1/Fs)

plt.subplot(511)
plt.plot(t, data)
plt.title(data_file)

# finding zero crossing point.
zero_crossings = fl_breath_zero_crossing_detection(data, Fs)
# zero_crossings = zero_crossings[3:]
zr_arr = np.array(zero_crossings)
zero_value = np.array(data)[zr_arr.astype(int)]
multiplier = (1/Fs)
t_zero_crossings =  [element * multiplier for element in zero_crossings]
plt.plot(t_zero_crossings, zero_value, 'ro')

# highpass filter.
filtered_data = [0] * len(data)
print("data len %ld, filter %ld", len(zero_crossings), len(data))
# filtered_data = butter_highpass_filter(data, cutoff, Fs)
filtered_data = ins_highpass_filter(filtered_data, zero_crossings, data, cutoff, Fs)
t = np.arange(0, len(filtered_data) * (1 / Fs), 1/Fs)
plt.subplot(512)
plt.plot(t, filtered_data)
plt.title('highpass filtered data')

# Find the short time energy.
# plt.subplot(513)
# ste_data = ste(filtered_data, scipy.signal.get_window("hamming", 101))
# t = np.arange(0, len(ste_data) * (1 / Fs), 1/Fs)
# plt.plot(t, ste_data)
plt.subplot(513)
ste_data = calculate_ste(filtered_data, windows_length, windows_step)
t = np.arange(0, len(ste_data) * (1 / Fs), 1/Fs)
plt.plot(t, ste_data)
plt.title('short-term-energy')

# Log of ste data
plt.subplot(514)
log_ste_data = np.log(ste_data)
log_ste_data[log_ste_data < 1] = 0
plt.plot(t, log_ste_data)
plt.title('logarithm of short-term-energy')

# first derivative of data.
# plt.subplot(515)
# first_derivative_ste = np.gradient(log_ste_data, t[1] - t[0])
# t = np.arange(0, len(first_derivative_ste) * (1 / Fs), 1/Fs)
# plt.plot(t, first_derivative_ste)
# plt.title('First Derivative')

# Snore index.
plt.subplot(515)
snore_index = [0] * len(data)
snore_index = snore_get_index(snore_index, log_ste_data, zero_crossings, windows_step)
t_snore_index = np.arange(0, len(snore_index) * (1 / Fs), 1/Fs)
plt.plot(t_snore_index, snore_index)
plt.title('Snore index')

plt.show()
