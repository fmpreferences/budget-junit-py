import subprocess
from argparse import ArgumentParser
import re
from tempfile import TemporaryFile
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
    '-m',
    '--matchinput',
    type=str,
    help=
    '''the output and input are in one file, where the input matches the given
    pattern. written in a way inputs are represented by a "."
    e.g. if inputs are denoted with [.] the actual input is in []. use \\.
    to escape
    ''')
juparse.add_argument('-s',
                     '--whitespace',
                     action='store_true',
                     help='if set ignores whitespace')
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


if args.flags is not None:
    subprocess.run(['javac', args.source, *args.flags.split(' ')])
else:
    subprocess.run(['javac', args.source])
if args.input is not None:
    with open(
            args.input) as j_input, TemporaryFile('a+') as input_output, open(
                args.output) as j_output:
        input_output.truncate(0)
        subprocess.run(['java', args.source.split(".")[0]],
                       stdin=j_input,
                       stdout=input_output)
        input_output.seek(0)
        if args.whitespace:
            print(input_output.read().strip() == j_output.read().strip())
        else:
            print(input_output.read() == j_output.read())
elif args.matchinput is not None:
    with open(args.output) as j_output:
        pattern = re.sub(r'(?<!\\)\.', r'(.*?)', args.matchinput)
        pattern = re.sub(r'\\\.', r'.', pattern)
        o = j_output.read()
        out_and_in = re.split(pattern, o)
        _out = []
        _in = []
        if re.match(pattern, o) is None:
            _out = out_and_in[::2]
            _in = out_and_in[1::2]
        else:
            _out = out_and_in[1::2]
            _in = out_and_in[::2]
        _output = ''.join(_out)
        _input = '\n'.join(_in) + '\n'
        with TemporaryFile('a+') as tinput, TemporaryFile(
                'a+') as toutput, TemporaryFile('a+') as tstdout:
            tinput.write(_input)
            tinput.seek(0)
            if args.whitespace:
                toutput.write(_output.strip())
            else:
                toutput.write(_output)
            toutput.seek(0)
            subprocess.run(['java', args.source.split(".")[0]],
                           stdin=tinput,
                           stdout=tstdout)
            toutput.seek(0)
            tstdout.seek(0)
            if args.whitespace:
                print(tstdout.read().strip() == _output.strip())
            else:
                print(tstdout.read() == _output)

else:
    with open(args.output) as j_output, TemporaryFile('a+') as input_output:
        subprocess.run(['java', args.source.split('.')[0]],
                       stdout=input_output)
        input_output.seek(0)
        if args.whitespace:
            print(input_output.read().strip() == j_output.read().strip())
        else:
            print(input_output.read() == j_output.read())
