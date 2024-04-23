import os

from parse_results import *

def open_files(reports_folder, vcd_folder, splits=[], power_suffix='_POWER', time_suffix='_TIME', area_suffix='_AREA', verbose=False):
    power = {}
    time = {}
    area = {}
    vcd_time = {}

    # Open all files in reports_folder
    for file in os.listdir(reports_folder):
        # Ensure file ends with '.txt'
        if not file.endswith('.txt'):
            continue

        # Remove the file extension
        filename = file[:-4]

        # Parse the file
        if filename.endswith(power_suffix):
            test_name = filename.replace(power_suffix, '')
            # Extract the power value from the file
            power[test_name] = extract_power(os.path.join(reports_folder, file), verbose=verbose)
        elif filename.endswith(time_suffix):
            test_name = filename.replace(time_suffix, '')
            # Extract the time value from the file
            time[test_name] = extract_time(os.path.join(reports_folder, file), verbose=verbose)
        elif filename.endswith(area_suffix):
            test_name = filename.replace(area_suffix, '')
            # Extract the area value from the file
            area[test_name] = extract_area(os.path.join(reports_folder, file), verbose=verbose)
        else:
            # Ignore the file
            continue
    
    # Open all files in vcd_folder
    for file in os.listdir(vcd_folder):
        # Ensure the file ends with .vcd
        if not file.endswith('.vcd'):
            continue

        # Remove the file extension
        filename = file[:-4]

        # Extract the time value from the file
        vcd_time[filename] = parse_vcd(os.path.join(vcd_folder, file), verbose=verbose)
    
    # Split the results if necessary
    if len(splits) > 0:
        power = separate_by_splits(power, splits)
        time = separate_by_splits(time, splits)
        area = separate_by_splits(area, splits)
        vcd_time = separate_by_splits(vcd_time, splits)
    else:
        power = [power]
        time = [time]
        area = [area]
        vcd_time = [vcd_time]
    
    # Ensure all dictionaries have the same keys
    for i in range(len(power)):
        assert power[i].keys() == time[i].keys() == area[i].keys() == vcd_time[i].keys()
    assert check_splits(power)
    assert check_splits(time)
    assert check_splits(area)
    assert check_splits(vcd_time)

    return power, time, area, vcd_time

def compute_energy(power, vcd_time, divide=1):
    energy = []
    keys = list(power[0].keys())
    nsplits = len(power)

    for i in range(nsplits):
        energy.append({})

        for k in keys:
            energy[i][k] = power[i][k] * vcd_time[i][k] / divide
    
    return energy

def get_unique(values, splits, verbose=False):
    nsplits = len(splits)
    unique_value = [-1.0] * nsplits

    for i in range(nsplits):
        for k, j in values[i].items():
            if unique_value[i] < 0:
                unique_value[i] = j
            elif j != unique_value[i]:
                if verbose:
                    print(f'[split {splits[i]}] Item {k} has a different area value: {j} instead of {unique_value[i]}')
    
    return unique_value

def apply_correct(energy, correct_dict):
    for i in range(len(energy)):
        for k in energy[i].keys():
            if k in correct_dict:
                bias = 0.0
                divide = 1.0

                if 'bias' in correct_dict[k]:
                    bias_name = correct_dict[k]['bias']
                    bias = energy[i][bias_name]
                if 'divide' in correct_dict[k]:
                    divide = correct_dict[k]['divide']
                
                energy[i][k] = (energy[i][k] - bias) / divide
    
    return energy