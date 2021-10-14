import subprocess
from argparse import ArgumentParser
import re
import sys

juparse = ArgumentParser(description='Tests your file compared to input')

juparse.add_argument('source',
                     type=str,
                     help='the path of the source code')
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
    help='the output and input are in one file, where the input matches regex')
juparse.add_argument('-i',
                     '--input',
                     type=str,
                     help='the path of the file containing the input')

args = juparse.parse_args()

program_out = ''
if args.flags is not None:
    subprocess.run('javac', args.source, *args.flags.split(' '))
else:
    subprocess.run('javac', args.source)
if args.input is not None:
    program_out = subprocess.run('java',
                                 args.source.split('.')[0], '<',
                                 args.input)
elif args.regexin is not None:
    with open(args.output) as j_output:
        whole_file = j_output.read()
        optional_input = ''.join(re.findall(args.regexin, whole_file))
        optional_output = ''.join(re.split(args.regexin, whole_file))
    program_out = subprocess.run('java',
                                 args.source.split('.')[0], '<',
                                 optional_input)
    sys.exit(program_out == optional_output)
else:
    program_out = subprocess.run('java', args.source.split('.')[0])

with open(args.output) as j_output:
    print(program_out == j_output.read())
