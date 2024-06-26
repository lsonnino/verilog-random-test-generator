from gen_words import gen_words, bits_to_len
from dc_iverilog import *
import ordering
import filtering
import json, os

def parse(template, args):
    # Replace $i by args[i]

    s = template
    
    # Enumerate in reverse order to void confusion between $10 and $1
    for i, arg in reversed(list(enumerate(args))):
        s = s.replace(f'${i + 1}', arg)
    
    return s

def write_template(f, words, template='template.v'):
    # Get template
    t = open(template, 'r')
    template_txt = t.read()
    t.close()

    # Parsed words
    for w in words:
        f.write(parse(template_txt, w) + '\n')
def write_prefix(f, prefix='prefix.txt'):
    if type(prefix) == type([]):
        for p in prefix:
            with open(p, 'r') as txt:
                f.write(txt.read())
    else:
        with open(prefix, 'r') as txt:
            f.write(txt.read())
def write_suffix(f, suffix='suffix.txt'):
    if type(suffix) == type([]):
        for s in suffix:
            with open(s, 'r') as txt:
                f.write(txt.read())
    else:
        with open(suffix, 'r') as txt:
            f.write(txt.read())

def generate(words, output, template, inter_template=None, prefix='prefix.v', suffix='suffix.v', multiple_words=False):
    # Open output file
    f = open(output, 'w')

    # Write prefix
    write_prefix(f, prefix)

    # Write template
    inter_template_txt = ''
    if inter_template:
        it = open(inter_template, 'r')
        inter_template_txt = it.read()
        it.close()

    if type(template) == type([]):
        for i, t in enumerate(template):
            use_words = words[i if i < len(words) else -1] if multiple_words else words

            f.write('\n')
            write_template(f, use_words, t)

            if i < len(template) - 1:
                f.write('\n')
                f.write(parse(inter_template_txt, use_words[0]))
    else:
        write_template(f, words[0] if multiple_words else words, template)

    # Write suffix
    f.write('\n')
    write_suffix(f, suffix)

    # Close output file
    f.close()

def get_order(order_str):
    if order_str is not None:
        if order_str == 'inverse':
            return ordering.inverse
        elif order_str == 'ntsf':
            return ordering.ntsf
        elif order_str == 'always_different':
            return ordering.always_different
        else:
            print(f'Warning: Unknown order {order_str}. Ignoring.')
            return None
    else:
        return None

def generate_from_json(test_file, RUN_TEST_SH='run_test.sh'):
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    # Get general parameters
    runner = data.get('auto_run', None)
    export_dc = data.get('export_dc', False)
    tcl_template = data.get('tcl_template', '')
    generators = data.get('generate', [])

    # Sanity check
    if export_dc and (tcl_template == ''):
        print(f'Warning: No TCL template provided. Disabling DC export.')
        export_dc = False

    # Each generator uses different generated words
    for generator in generators:
        # get commoon parameters
        name = generator.get('name', '')
        gen_enable = generator.get('enable', True)
        tests = generator.get('test', [])
        n = generator.get('n', 1)
        lengths = generator.get('lengths', [])
        from_bits = generator.get('from_bits', False)
        output_folder = generator.get('output_folder', './')
        order_str = generator.get('order', None)
        filter_str = generator.get('filter', None)

        if not gen_enable:
            print(f" > Generator {name} is disabled.")
            continue

        print()
        print("=====================")
        print("  Generator:")
        print(f"    Name: {name}")
        print("=====================")
        print()

        # Validation check
        if len(tests) is None:
            print(f'Warning: No tests provided. Stopping here.')
            return
        
        if len(lengths) == 0:
            print(f'Warning: No lengths provided for generator {name}. Is this intended ?')
        
        if (name == '') and (len(generators) > 1):
            print(f'Warning: No lengths provided for generator. Is this intended ?')
            name = 'noname'
        
        if output_folder[-1] != '/':
            output_folder += '/'
        
        if filter_str is not None:
            if filter_str == 'pass_all':
                filter = filtering.pass_all
            elif filter_str == 'dffe':
                filter = filtering.dffe
            else:
                print(f'Warning: Unknown filter {filter_str}. Ignoring.')
                filter = None
        else:
            filter = None

        # Generate words
        if from_bits:
            lengths, first_custom_alphabet = bits_to_len(lengths)
            generated_words = gen_words(n, lengths, out=None, first_custom_alphabet=first_custom_alphabet, filter=filter)
        else:
            generated_words = gen_words(n, lengths, out=None, filter=filter)
        
        # Order words
        if order_str is not None:
            if type(order_str) == type([]):
                multiple_words = True
                words = [None] * len(order_str)

                for i, o in enumerate(order_str):
                    order = get_order(o)
                    if order is not None:
                        words[i] = order(generated_words)
                    else:
                        words[i] = generated_words
            else:
                multiple_words = False

                order = get_order(order_str)
                if order is not None:
                    words = order(generated_words)
                else:
                    words = generated_words
        else:
            multiple_words = False
            words = generated_words
        
        # Generate tests
        os.system(f'mkdir -p {output_folder}')

        # Tests share the same words generation
        for t in tests:
            output_filename = name + '_' + t.get('output', 'testbench.v')
            output = output_folder + output_filename
            enable = t.get('enable', True)
            template = t.get('template', 'template.v')
            inter_template = t.get('inter_template', None)
            prefix = t.get('prefix', 'prefix.v')
            suffix = t.get('suffix', 'suffix.v')
            top_module = t.get('module', 'uut')

            # Remove .v or .sv extension
            if output_filename[-2:] == '.v':
                output_filename_no_ext = output_filename[:-2]
            elif output_filename[-2:] == '.sv':
                output_filename_no_ext = output_filename[:-3]
            
            if not enable:
                print(f" > Test {output_filename_no_ext} is disabled.")
                continue
            else:
                print(f" > Test: {output_filename_no_ext}")

            # Generate testbench
            generate(words, output, template, inter_template, prefix, suffix, multiple_words)

            # Run simulation and export for Design Compiler
            if runner is not None:
                if run(runner, output_filename, name, output_folder, output_filename_no_ext) and export_dc:
                    export_to_dc(output_folder, output_filename_no_ext, name, tcl_template, top_module, RUN_TEST_SH=RUN_TEST_SH)

if __name__ == '__main__':
    generate(
        n = 10, lengths = [10, 32], from_bits = True,
        output = 'testbench.v',
        template = 'template.v',
        suffix = 'suffix.v', prefix = 'prefix.v'
    )

    generate(
        n = 10, lengths = [10, 32], from_bits = True,
        output = 'testbench_split.v',
        template = ['template_1.v', 'template_2.v'], inter_template=None,
        suffix = 'suffix.v', prefix = 'prefix.v'
    )
