# README

The goal of this small project is to generate testbenches with thousand of random arguments, then use icarus_verilog to simulate and generate a `.vcd` file, finally prepare a`.tcl` script so that DesignCompiler can run it automatically.

The best way of using the program is by setting it up using a JSON, then calling the `generator.generate_from_json` function.

## Concepts

The program generate from one or multiple generators, each containing one or multiple tests.

A generator has a name and tells the program how to generate numbers. Then one testbench is generated for each test in the generator. These tests share the same random numbers. Hence twice the same test inside the same generator will produce two identical testbenches. But two identical tests in two different generators will produce different testbenches due to randomness.

The program generates a Verilog `.v` file (the testbench) whose name is the `GEN_FILE.v` in which `GEN` is the name of the generator and `FILE` is the name of the output file in the test. It can be setup to generate a `.tcl` file and a `.vcd` file with the same name as the Verilog one. If the `.tcl` and `.vcd` files are generated, a `run_test.sh` is also generated to automatically convert the `.vcd` file to a `.saif` one, and run the `.tcl` file.

The `.tcl` file is generated from a template and will look something like this:

```tcl
set NAME GEN # in which GEN is the name of the generator
set SIM_FILE GEN_FILE # in which GEN is the name of the generator and FILE the name of the test's output testbench, without the extension
set TOP_MODULE MOD # in which MOD is the name of the top module of the test

# Plain content of the template tcl file
```

The three set variables can be used in the template, for instance like this:

```tcl
report_area >> ${SIM_FILE}_AREA.txt
```

Do not forget to end the template `.tcl` file with the `quit` instruction (automatically quits the dc_shell after execution) so that when running the `run_test.sh` file, all the tests are executed with no required user input in between.



## Generating tests

The generator tells how many and how long should the hexadecimal numbers be. For instance, it can generate 10 times a 3 and a 4 hexadecimal characters numbers. The testbench is then generated from at least 3 files: prefix, suffix and template. The generated file resembles this:

```verilog
// Plain content of the prefix file
// N times the template with the random numbers (10 times in the example above)
// Plain content of the suffix file
```

The template must tell where to put the numbers. In the example above, the template will be repeated 10 times with different numbers, and everytime two numbers are generated. These are put in the template where the string `$1` and `$2` appear. The template hence would look something like:

```verilog
@(posedge clk); en <= 1; wen <= 1; addr <= 12'h$1; din <= 16'h$2;
```

In the above example, the program generates a number whose length is 3 hexadecimal character (for instance: f2c). The generated numbers can also be large a specific number of bits, instead. Hence a 10-bit number can be generated as well (for instance: 32c). This is set in the JSON file.



### Using multiple templates

To simulate processes like a write and read sharing the same address, two options are provided:

1. Use one template that uses multiple time the same value
2. Use two templates

In the first solution, the template would look something like this:

```verilog
@(posedge clk); en <= 1; wen <= 1; addr <= 12'h$1; din <= 16'h$2;
@(posedge clk); en <= 1; wen <= 0; addr <= 12'h$1; din <= 16'hxxxxxxxx;
```

Notice that the generated address (`$1`) is used twice.

But the test can also take multiple templates, separated by some specific (non random) code:

```verilog
// Plain content of the prefix file
// N times the first template
// [optional] plain content of a file
// N times the second template
// [optional] plain content of a file, the same as above
// N times the third template
// ...
// Plain content of the suffix file
```

Each template share the same random numbers. Hence the templates could be something like:

template 1:

```verilog
@(posedge clk); en <= 1; wen <= 1; addr <= 12'h$1; din <= 16'h$2;
```

template 2:

```verilog
@(posedge clk); en <= 1; wen <= 0; addr <= 12'h$1; din <= 16'hxxxxxxxx;
```



Some code can be put between the first and second template. That code cannot use any random numbers (no `$1`, `$2`, ...).



### Reordering

The order in which the random numbers are fed can be customised depending on some simple rules, through the `order` entry. Currently, the following rules are implemented:

* **null**: no particular re-ordering
* **inverse**: reverse the order of the list
* **ntsf**: (stands for "never twice the same first"). It tries as much as possible to avoid generating two sets of numbers whose first character of the first number is the same. Hence the numbers ['011', 'abc'], ['011', 'abc'], ['111', 'abc'] will become ['011', 'abc'], ['111', 'abc'], ['011', 'abc']. Hence the first number of each set ('011', '011', '111') will always have a different first char (['0', '0', '1'] becomes '0', '1', '0')
* **always_different**: re-order words so that the starting letter of the last element of each word has a different starting letter than the first element of the next word. Gence, the word ['000', '111'] cannot be followed by ['100', '211'] because '111' and '100' both start with '1'

Ordering can also be an array where each element is one of the entry here-above. In which case, the first template will be ordered according to the first entry of the array, the second template according to the second and so on. If the re-ordering array is smaller than the number of templates, the last few templates are re-ordered according to the last order. So if the order is `["ntsf", "always_different"]` and template is `["template1.v", "template2.v", "template3.v"]` then `"template1.v"` uses `"ntsf"` while the other two templates use `"always_different"`.



### Filtering

Words can be filtered so that they meet certain conditions:

* **null**: no particular filtering
* **dffe**: (stands for "Different First of First Element"). Takes the length of the first element of the word. Then takes all the other elements of the same size. The first letter of those elements must be different

Note that the number of generated words will be the same regardless of the filter. The filter only ensures that all of those words are generated following a given condition.



## JSON file

Here is a JSON example:

```json
{
    "export_dc": true,
    "tcl_template": "tcl_template.tcl",
    "auto_run": {
        "src_folder": "verilog_code/",
        "files": "uut.sv sub_module.sv",
        "args": "-g2012",
        "vcd": "waveform.vcd"
    },
    "generate": [
        {
            "name": "mytest",
            "n": 1000,
            "lengths": [10, 32],
            "from_bits": true,
            "output_folder": "example/output/",
            "order": "ntsf",
          	"filter": "dffe",
            "test": [
                {
                    "output": "first.v",
                    "template": "example/template_first_mytest.v",
                    "inter_template": null,
                    "prefix": "example/first_pre.v",
                    "suffix": "example/first_post.v",
                    "module": "first"
                },
                {
                    "output": "second.v",
                    "template": ["example/template_second_mytest_1.v", "example/template_second_mytest_2.v"],
                    "inter_template": "example/template_second_inter.v",
                    "prefix": "example/second_pre.v",
                    "suffix": "example/second_post.v",
                    "module": "second"
                }
            ]
        }
    ]
}
```

The JSON uses the following parameters:

* **export_dc** [optional, defaults to false]: if `true`, generate a `run_test.sh` file and `.tcl` file. In which case, the *tcl_template* command must be set. Requires *auto_run* to be set
* **tcl_template** [optional, unless *export_dc* is true]: path of the template tcl file to use
* **auto_run** [optional, unless *export_dc* is true]: sets parameters to run the simulation using iverilog to generate a `.vcd` file
  * **src_folder**: path to the folder that contains all the modules, except the testbench (which will be generated automatically)
  * **files**: the verilog source files except the generated testbench
  * **args**: additional arguments to be passed to the iverilog command
  * **vcd**: name of the exported `.vcd` file. This should match the one in the prefix or suffix file, used to generate the testbench
* **generate**: an array of generators
  * **name**: name of the generator. Should be unique amongst generators
  * **enable** [optional, defaults to true]: if false, the generator is skipped
  * **n**: the number of times the template should be repeated. In other words, the number of times numbers need to be generated
  * **lengths**: the length of each number that should be generated. This is either the number of bits, or the number of hexadecimal characters the numbers should be (depending on the *from_bits* parameter)
  * **from_bits** [optional, defaults to false]: if true, the number lengths specified in *lengths* are interpreted as the number of bits
  * **output_folder**: where to export
  * **order** [optional, defaults to None]: change the order of the generated words
  * **filter** [optional, defaults to None]: ensures all words meet a given condition
  * **tests**: a list of tests to generate. They each share the same generated numbers
    * **output**: the name of the output file for the test
    * **enable** [optional, defaults to true]: if false, the test is skipped
    * **template**: either the path to the template, or an array of paths to different templates
    * **inter_template** [optional, defaults to null]: path to the code to put between the templates. Unused if there is only one template
    * **prefix**: path to the prefix file
    * **sufffix**: path to the suffix file
    * **module** [optional, except if *export_dc* is true]: the name of the top module



This example file hence generates all the files for a DC simulation. It generates 1000 times one 10 and one 32 bits number (2000 numbers in total). It has two tests hence generates two testbenches, with those same 2000 numbers:

example/output/mytest_first.v:

```verilog
// Content of {example/first_pre.v}
/*
	1000 times, content of {example/template_first_mytest.v}
	Each time, with different values for $1 and $2.
		$1 is 10 bits long (3 hexadecimal characters, first one from 0 to 3)
		$2 is 32 bits long (8 hexadecimal characters)
 */
// Content of {example/first_post.v}
```

example/output/mytest_second.v:

```verilog
// Content of {example/second_pre.v}
/*
	1000 times, content of {example/template_second_mytest_1.v}
	Each time, with different values for $1 and $2.
		$1 is 10 bits long (3 hexadecimal characters, first one from 0 to 3)
		$2 is 32 bits long (8 hexadecimal characters)
 */
// Content of {example/template_second_inter.v}
/*
	1000 times, content of {example/template_second_mytest_2.v}
	Each time, with different values for $1 and $2.
		$1 is 10 bits long (3 hexadecimal characters, first one from 0 to 3)
		$2 is 32 bits long (8 hexadecimal characters)
 */
// Content of {example/second_post.v}
```

The exact same 2000 numbers are used throughout these two files.