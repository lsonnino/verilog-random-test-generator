from generator import generate_from_json
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Verilog Test Generator',
        description='Generate test vectors for Verilog modules',
        epilog='This program generates test vectors for Verilog modules.'
    )
    parser.add_argument('filename', help='The JSON file containing the test parameters')

    args = parser.parse_args()
    generate_from_json(args.filename)