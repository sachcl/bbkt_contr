#sample/sample/sample.py

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
