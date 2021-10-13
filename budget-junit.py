import subprocess
from argparse import ArgumentParser
import re
import sys

juparse = ArgumentParser(description='Tests your file compared to input')

juparse.add_argument('source',
                     type=str,
                     help='the path of the file whose output to test')
juparse.add_argument('-f',
                     '--flags',
                     type=str,
                     help='special javac flags and arguments')
juparse.add_argument(
    '-r',
    '--regexin',
    type=str,
    help='the output and input are in one file, where the input matches regex')
juparse.add_argument('output',
                     type=str,
                     help='the path of the file containing the output')
juparse.add_argument('-i',
                     '--input',
                     type=str,
                     help='the path of the file containing the input')

program_out = ''
subprocess.run('javac', juparse.source, *juparse.flags.split(' '))
if juparse.input is not None:
    program_out = subprocess.run('java',
                                 juparse.source.split('.')[0], '<',
                                 juparse.input)
elif juparse.regexin is not None:
    with open(juparse.output) as j_output:
        whole_file = j_output.read()
        optional_input = ''.join(re.findall(juparse.regexin, whole_file))
        optional_output = ''.join(re.split(juparse.regexin, whole_file))
    program_out = subprocess.run('java',
                                 juparse.source.split('.')[0], '<',
                                 optional_input)
    sys.exit(program_out == optional_output)
else:
    program_out = subprocess.run('java', juparse.source.split('.')[0])

with open(juparse.output) as j_output:
    print(program_out == j_output.read())
