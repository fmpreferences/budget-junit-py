import subprocess
from argparse import ArgumentParser
import re

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
    '-m',
    '--matchinput',
    type=str,
    help=
    '''the output and input are in one file, where the input matches the given
    pattern. written in a way inputs are represented by a "."
    e.g. if inputs are denoted with [.] the actual input is in []. use \\.
    to escape
    ''')
juparse.add_argument('-i',
                     '--input',
                     type=str,
                     help='the path of the file containing the input')

args = juparse.parse_args()


def regex_repl(match: re.Match):
    '''
    regex match function, replaces any single character with escape,
    and period with a special regex'''
    if match.group(0) == '.':
        return r'(?<!\\)\.'
    if not match.group(0).isalnum():
        return '\\' + match.group(0)
    else:
        return match.group(0)


program_out = ''
if args.flags is not None:
    subprocess.run(['javac', args.source, *args.flags.split(' ')])
else:
    subprocess.run(['javac', args.source])
if args.input is not None:
    optional_input = ''
    with open(args.input) as j_input:
        with open(args.input + ".output", 'a+') as input_output:
            input_output.truncate(0)
            subprocess.run(['java', args.source.split(".")[0]],
                           stdin=j_input,
                           stdout=input_output)
    with open(args.input + ".output") as input_output:
        program_out = input_output.read()
elif args.matchinput is not None:
    with open(args.output, 'r') as j_output:
        print(args.matchinput)
        pattern = re.sub(r'(?<!\\)\.', r'(.*)', args.matchinput)
        pattern = re.sub(r'\\\.', r'.', pattern)
        print(pattern)
        _output = j_output.read()
        print(_output)
        for i in range(len(_output)):
            print(re.search(pattern, _output, i))
else:
    with open(args.source + '.output', 'a+') as input_output:
        program_out = subprocess.run(
            ['java', args.source.split('.')[0]], stdout=input_output)
with open(args.output) as j_output:
    print(program_out == j_output.read())
