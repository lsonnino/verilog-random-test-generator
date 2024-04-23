import os
import argparse
import json

from data_handler import *
from analysis_export import *

def analyse(
    reports_folder, vcd_folder, splits=[], divide=1,
    power_suffix='_POWER', time_suffix='_TIME', area_suffix='_AREA',
    verbose=False, output=None, correct_dict={}, compare_dict={}, export=None, rename_dict={}
):
    # Open all files
    power, time, area,  vcd_time = open_files(
        reports_folder=reports_folder, vcd_folder=vcd_folder,
        splits=splits,
        power_suffix=power_suffix, time_suffix=time_suffix, area_suffix=area_suffix,
        verbose=verbose
    )

    # Compute the energy consumption
    energy = compute_energy(power, vcd_time, divide=divide)

    # Get unique values
    time = get_unique(time, splits, verbose=verbose)
    area = get_unique(area, splits, verbose=verbose)

    # Build export if necessary
    if len(export) == 0:
        export = list(energy[0].keys())

    # Apply correction
    apply_correct(energy, correct_dict)

    # Apply renaming
    splits, energy, compare_dict, export = apply_rename_dict(splits, energy, compare_dict, export, rename_dict)
    
    # Export the results to a markdown file
    export_to_md(splits, energy, time, area, compare_dict, export, output=output)

def parse_arguments(json_file, reports_folder, vcd_folder, splits, divide, power_suffix, time_suffix, area_suffix, verbose, output):
    if json_file is not None:
        with open(json_file, 'r') as f:
            data = json.load(f)

            if reports_folder is None:
                reports_folder = data.get('reports', reports_folder)
            if vcd_folder is None:
                vcd_folder = data.get('vcd', vcd_folder)
            if splits is None:
                splits = data.get('splits', [])
            else:
                splits = []
            if divide is None:
                divide = data.get('divide', divide)
            else:
                divide = 1
            if power_suffix is None:
                power_suffix = data.get('power_suffix', power_suffix)
            else:
                power_suffix = '_POWER'
            if time_suffix is None:
                time_suffix = data.get('time_suffix', time_suffix)
            else:
                time_suffix = '_TIME'
            if area_suffix is None:
                area_suffix = data.get('area_suffix', area_suffix)
            else:
                area_suffix = '_AREA'
            if verbose is False:
                verbose = data.get('verbose', verbose)
            if output is None:
                output = data.get('output', output)
            
            correct_dict = data.get('correct', {})
            compare_dict = data.get('compare', {})
            export = data.get('export', [])
            rename_dict  = data.get('rename', {})
    
    if splits is None:
        splits = []
    if divide is None:
        divide = 1

    analyse(
        reports_folder, vcd_folder,
        splits=splits, divide=divide,
        power_suffix=power_suffix, time_suffix=time_suffix, area_suffix=area_suffix,
        verbose=verbose, output=output, correct_dict=correct_dict, compare_dict=compare_dict, export=export, rename_dict=rename_dict
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Verilog Test Generator - results parser',
        description='Parse results from Verilog test runs',
        epilog='This program extracts power, energy, time and area from reports and vcd files.'
    )
    parser.add_argument('--reports', dest='reports', help='The path to the folder containing the power, area and timing reports', default=None)
    parser.add_argument('--vcd', dest='vcd', help='The path to the folder containing the vcd files used for test generation', default=None)
    parser.add_argument('--json', help='Take arguments from JSON file', default=None)
    parser.add_argument('--splits', dest='splits', nargs='*', help='Separate results depending on those suffixes', default=None)
    parser.add_argument('--divide', dest='divide', type=int, help='Divide energy consumptions by this value', default=None)
    parser.add_argument('-p', dest='power_suffix', help='The suffix used to distinguish power reports. Defaults to _POWER', default=None)
    parser.add_argument('-t', dest='time_suffix', help='The suffix used to distinguish time reports. Defaults to _TIME', default=None)
    parser.add_argument('-a', dest='area_suffix', help='The suffix used to distinguish area reports. Defaults to _AREA', default=None)
    parser.add_argument('--output', dest='output', help='Where to store the output. By defaults, prints it to stdout', default=None)
    parser.add_argument('--verbose', dest='verbose', help='Prints warning messages', default=False, action='store_true')

    args = parser.parse_args()
    if args.divide == 0:
        print('Cannot divide by 0')
    elif (args.json is None) and ((args.reports is None) or (args.vcd is None)):
        print('Missing arguments. Please specify at least a JSON file or both reports and vcd folders')
    else:
        parse_arguments(
            args.json, args.reports, args.vcd,
            splits=args.splits, divide=args.divide,
            power_suffix=args.power_suffix, time_suffix=args.time_suffix, area_suffix=args.area_suffix,
            verbose=args.verbose, output=args.output
        )
