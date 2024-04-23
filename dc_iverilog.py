
def run(runner, testbench, name, output_folder, output_filename_no_ext, RUN_ENV='run_env'):
    # Parse arguments
    args = runner.get('args', '')
    src_folder = runner.get('src_folder', './')
    files = runner.get('files', '')
    vcd = runner.get('vcd', None)

    files_array = files.split(' ')
    
    # Sanity check
    if vcd is None:
        print("Error: No VCD file specified. Stopping here.")
        return False
    if src_folder[-1] != '/':
        src_folder += '/'

    # Setup environment
    os.system(f'mkdir -p {RUN_ENV}')
    for f in files_array:
        os.system(f'cp {src_folder + f} {RUN_ENV}/')
    os.system(f'cp {output_folder + testbench} {RUN_ENV}/')

    # Run simulation
    os.system(f'cd {RUN_ENV} && iverilog {args} -o {name} {testbench} {files} && vvp {name}')
    # Cleanup
    os.system(f'rm {RUN_ENV}/{name}')
    os.system(f'mv {RUN_ENV}/{vcd} {output_folder}{output_filename_no_ext}.vcd')

    return True

def export_to_dc(output_folder, output_filename_no_ext, name, tcl_template, top_module, RUN_TEST_SH='run_test.sh'):
    with open(tcl_template, 'r') as tcl:
        tcl_txt = tcl.read()
    
    # Write TCL script
    with open(output_folder + output_filename_no_ext + '.tcl', 'w') as f:
        # Set variables that can be used in the TCL script
        f.write(f'set NAME {name}\n')
        f.write(f'set SIM_FILE {output_filename_no_ext}\n')
        f.write(f'set TOP_MODULE {top_module}\n\n')
        # Write the rest of the TCL script
        f.write(tcl_txt)
    
    # Append to run_test.sh
    with open(output_folder + RUN_TEST_SH, 'a') as f:
        f.write(f'vcd2saif -input {output_filename_no_ext}.vcd -output {output_filename_no_ext}.saif\n')
        f.write(f'dc_shell -f {output_filename_no_ext}.tcl\n')
