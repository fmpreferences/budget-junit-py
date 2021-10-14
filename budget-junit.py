import subprocess
from argparse import ArgumentParser
import re
import sys

juparse = ArgumentParser(description='Tests your file compared to input')

juparse.add_argument('source', type=str, help='the path of the source code')
juparse.add_argument('output',
                     type=str,
                     help='the path of the file containing the output')
juparse.add_argument('-f',
                     '--flags',
                     type=str,
                     help='special javac flags and arguments')
juparse.add_argument(
    '-r',
    '--regexin',
    type=str,
    help=
    r'''the output and input are in one file, where the input matches a regex.
    written in a way inputs can be caught by capture group one
    e.g. if inputs are denoted with \[(.*)\] the actual input is in group one
    ''')
juparse.add_argument('-i',
                     '--input',
                     type=str,
                     help='the path of the file containing the input')

args = juparse.parse_args()

program_out = ''
if args.flags is not None:
    subprocess.run(['javac', args.source, *args.flags.split(' ')])
else:
    subprocess.run(['javac', args.source])
if args.input is not None:
    optional_input = ''
    with open(args.input) as j_input:
        with open(args.input + ".output", 'a+') as input_output:
            subprocess.run(['java', args.source.split(".")[0]],
                           stdin=j_input,
                           stdout=input_output)
            actual_out = input_output.readlines()
            print(actual_out)
    with open(args.output) as j_output:
        print(j_output.read() == actual_out)
elif args.regexin is not None:
    print(args.regexin)
    with open(args.output) as j_output:
        whole_file = j_output.read()
        optional_input = '\n'.join(re.findall(args.regexin, whole_file))
        optional_output = ''.join(re.split(args.regexin, whole_file))
    print(['java', args.source.split('.')[0], '<', optional_input])
    program_out = subprocess.run(
        ['java', args.source.split('.')[0], '<', optional_input])
    sys.exit(program_out == optional_output)
else:
    program_out = subprocess.run(['java', args.source.split('.')[0]])
with open(args.output) as j_output:
    print(program_out == j_output.read())
