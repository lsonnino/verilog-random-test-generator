import os

def get_longest(array, last_longest=0):
    return max(last_longest, max([len(i) for i in array]))
def to_str(array, last_longest=0):
    str_array = [str(i) for i in array]
    longest_str = get_longest(str_array, last_longest=last_longest)

    return str_array, longest_str

def apply_rename_dict(splits, energy, compare_dict, export, rename_dict):
    for i in range(len(splits)):
        splits[i] = rename_dict.get(splits[i], splits[i])
        
        for k in energy[i].keys():
            new_key = rename_dict.get(k, k).lower()
            if new_key != k:
                energy[i][new_key] = energy[i].pop(k)
    
    for i in range(len(export)):
        export[i] = rename_dict.get(export[i], export[i])
    
    old_keys = list(compare_dict.keys())
    for k in old_keys:
        v = compare_dict.pop(k)

        new_key = rename_dict.get(k, k)
        for vi in range(len(v)):
            v[vi] = rename_dict.get(v[vi], v[vi])
        
        compare_dict[new_key] = v
    
    return splits, energy, compare_dict, export

def flatten_all_energies(energy):
    array = []

    for i in range(len(energy)):
        for _, i in energy[i].items():
            array.append(i)

    return array

def export_to_md(splits, energy, times, areas, compare_dict, export, output=None):
    lines = []
    lines.append('# Results')
    ls = get_longest(splits)

    # Export times and areas
    times_str, times_longest = to_str(times)
    area_str, area_longest = to_str(areas)
    longest = max(times_longest, area_longest)
    longest = max(longest, ls)

    lines.append('**Time and area:**')
    lines.append('|      | ' + ' | '.join([s.center(longest) for s in splits]) + ' |')
    lines.append('| ---- | ' + ' | '.join([':'+('-' * (longest-2))+':' for _ in splits]) + ' |')
    lines.append('| Time | ' + ' | '.join([s.center(longest) for s in times_str]) + ' |')
    lines.append('| Area | ' + ' | '.join([s.center(longest) for s in area_str]) + ' |')
    lines.append('')
    lines.append('units: um2 and ns')
    lines.append('')
    lines.append('')
    lines.append('')

    # Export energy consumptions
    longest_key = get_longest(export)
    longest = ls
    _, longest = to_str(flatten_all_energies(energy), last_longest=longest)

    lines.append('**Energy consumptions:**')
    compare_start_index = len(lines)
    lines.append('| '+ (' '*longest_key) +' | ' + ' | '.join([s.center(longest) for s in splits]) + ' | ')
    lines.append('| '+ ('-'*longest_key) +' | ' + ' | '.join([':'+('-' * (longest-2))+':' for _ in splits]) + ' | ')
    for k in export:
        lines.append(f'| {k.center(longest_key)} | ' + ' | '.join([f'{round(en[k.lower()], 5)}'.center(longest) for en in energy]) + ' | ')
    lines.append('')
    lines.append('units: pJ')

    # Add comparison
    for c, cc in compare_dict.items():
        heading = [f'{c}/{cci}' for cci in cc]

        lines[compare_start_index] += ' | '.join(heading) + ' | '
        lines[compare_start_index+1] += ' | '.join([':'+('-' * max(8, len(h)-2))+':' for h in heading]) + ' | '

        num_index = splits.index(c)
        for cci in cc:
            denum_index = splits.index(cci)

            for i, k in enumerate(export):
                v = round(energy[num_index][k.lower()] / energy[denum_index][k.lower()] * 100, 2)
                lines[compare_start_index+2+i] += f'{v}%' + ' | '

    # Write all lines to file
    if output is None:
        print('\n'.join(lines))
    else:
        with open(output, 'w') as f:
            f.write('\n'.join(lines))
