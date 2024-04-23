def extract_power(filename, verbose=False):
    with open(filename, 'r') as f:
        lines = f.readlines()[::-1]
        for line in lines:
            # Check if the line starts with 'Total'
            if line.startswith('Total Dynamic Power'):
                # Not the line we are looking for
                pass
            elif line.startswith('Total'):
                # Split the line into words
                words = line.split()
                
                if words[-1] == 'uW':
                    value = words[-2]
                else:
                    value = words[-1]
                
                try:
                    return float(value)
                except ValueError:
                    if verbose:
                        print(f'Could not extract power from file. Invalid value {value}')
                    return -1
    return -1

def extract_time(filename, verbose=False):
    with open(filename, 'r') as f:
        lines = f.readlines()[::-1]
        for line in lines:
            trimmed = line.strip()

            if trimmed.startswith('data required time'):
                value = trimmed.split(' ')[-1]

                try:
                    return float(value)
                except ValueError:
                    if verbose:
                        print(f'Could not extract time from file. Invalid value {value}')
                    return -1

def extract_area(filename, verbose=False):
    with open(filename, 'r') as f:
        lines = f.readlines()[::-1]
        for line in lines:
            trimmed = line.strip()

            if trimmed.startswith('Total cell area:'):
                value = trimmed.split(' ')[-1]
                
                try:
                    return float(value)
                except ValueError:
                    if verbose:
                        print(f'Could not extract area from file. Invalid value {value}')
                    return -1
                
def parse_vcd(filename, verbose=False):
    timescale_id = '$timescale'
    time_id = '#'

    timescale = 1.0
    last_time = 0
    rounding = 0  # Number of decimals to round, avoids floating point errors

    with open(filename, 'r') as f:
        lines = f.readlines()
        for i, line_us in enumerate(lines):
            line = line_us.strip()

            if line.startswith(timescale_id):
                timescale_line = line.split(' ')

                if len(timescale_line) > 1:
                    timescale_str = timescale_line[1]
                else:
                    timescale_str = lines[i+1].strip().split(' ')[0]
                
                timescale_str = timescale_str.lower()
                if timescale_str[-1] != 's':
                    print(f'Unrecognised or unsupported timescale {timescale_str}')
                    break

                timescale_str = timescale_str[:-1]
                if timescale_str[-1] == 'p':
                    timescale = 1/(1e6)
                    rounding = 6
                elif timescale_str[-1] == 'n':
                    timescale = 1/1000
                    rounding = 3
                elif timescale_str[-1] == 'u':
                    timescale = 1.0
                    rounding = 0
                elif verbose:
                    print(f'Unrecognised or unsupported timescale {timescale_str}')
                
                try:
                    timescale /= float(timescale_str[:-1])
                except ValueError:
                    if verbose:
                        print(f'Could not parse timescale from line {line}')
                
                break
            
        for line_us in lines[::-1]:
            line = line_us.strip()

            if line.startswith(time_id):
                time_str = line[len(time_id):]
                try:
                    last_time = int(time_str)
                except ValueError:
                    if verbose:
                        print(f'Could not parse time from line {line}')

                if time_str.endswith('000000'):
                    rounding = max(0, rounding - 6)
                elif time_str.endswith('000'):
                    rounding = max(0, rounding - 3)
                
                break
    
    return round(last_time * timescale, rounding)

def separate_by_splits(values, splits):
    separated_values = [None] * len(splits)
    for i in range(len(splits)):
        separated_values[i] = {}

    for key, value in values.items():
        for i, s in enumerate(splits):
            if key.endswith(s):
                test_name = key[:-len(s)]
                separated_values[i][test_name] = value
                break

    return separated_values

def check_splits(values):
    keys = [None] * len(values)
    for i in range(len(values)):
        keys[i] = values[i].keys()
    
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            if keys[i] != keys[j]:
                return False
    
    return True
