import subprocess
from argparse import ArgumentParser
import re
from tempfile import TemporaryFile
import difflib
import os

juparse = ArgumentParser(
    description='''tests the output of [source] file against the [output].
    if using multiple outputs then make sure to match your input names as well'''
)

juparse.add_argument('source', type=str, help='the path of the source code')
juparse.add_argument('output',
                     type=str,
                     help='the path of the file containing the output')
juparse.add_argument('-d', '--dump', type=str, help='file to dump stdout to')
juparse.add_argument('-f',
                     '--flags',
                     type=str,
                     help='special javac flags and arguments')
juparse.add_argument('-i',
                     '--input',
                     type=str,
                     help='the path of the file containing the input')
juparse.add_argument(
    '-m',
    '--matchinput',
    type=str,
    help=
    '''the output and input are in one file, where the input matches the given
    pattern. written in a way inputs are represented by a "(.*?)"
    e.g. if inputs are denoted with {(.*?)} the actual input is in {}. use \\\\
    to escape special characters
    IMPORTANT: regex rules work so you can use alternate input matching but
    avoid using grouping other than the one matching input because it will
    break. if the inputs are not matched right try escaping with \\\\
    ''')
juparse.add_argument('-s',
                     '--whitespace',
                     action='store_true',
                     help='if set ignores whitespace')

args = juparse.parse_args()

if args.flags is not None:
    subprocess.run(['javac', args.source, *args.flags.split(' ')])
else:
    subprocess.run(['javac', args.source])


def run_test(output, iinput=None):
    global args
    test_passes = False
    if iinput is not None:
        with open(iinput) as j_input, TemporaryFile(
                'a+') as input_output, open(output) as j_output:
            input_output.truncate(0)
            subprocess.run(['java', args.source.split(".")[0]],
                           stdin=j_input,
                           stdout=input_output)
            input_output.seek(0)
            _stdout = input_output.read()
            if args.whitespace:
                a = re.sub(r'\s*?\n', '', _stdout)
                b = re.sub(r'\s*?\n', '', j_output.read())

                test_passes = a == b
                for line in difflib.unified_diff([b], [a], 'expected output',
                                                 'program output'):
                    print(line)
            else:
                b = j_output.read()
                for line in difflib.unified_diff([b], [_stdout],
                                                 'expected output',
                                                 'program output'):
                    print(line)
                test_passes = (_stdout == b)
            if args.dump is not None:
                with open(args.dump, 'w') as dump:
                    dump.write(_stdout)
    elif args.matchinput is not None:
        with open(output) as j_output:
            o = j_output.read()
            out_and_in = re.split(args.matchinput, o)
            _out = []
            _in = []
            if re.match(args.matchinput, o) is None:
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
                _stdout = tstdout.read()
                if args.whitespace:
                    a = re.sub(r'\s*?\n', '', _stdout)
                    b = re.sub(r'\s*?\n', '', _output)
                    for line in difflib.unified_diff([b], [a],
                                                     'expected output',
                                                     'program output'):
                        print(line)
                    test_passes = (a == b)
                else:
                    for line in difflib.unified_diff([_output], [_stdout],
                                                     'expected output',
                                                     'program output'):
                        print(line)
                    test_passes = (_stdout == _output)
                if args.dump is not None:
                    with open(args.dump, 'w') as dump:
                        dump.write(_stdout)

    else:
        with open(output) as j_output, TemporaryFile('a+') as input_output:
            subprocess.run(['java', args.source.split('.')[0]],
                           stdout=input_output)
            input_output.seek(0)
            _stdout = input_output.read()
            if args.whitespace:
                a = re.sub(r'\s*?\n', '', _stdout)
                b = re.sub(r'\s*?\n', '', j_output.read())
                for line in difflib.unified_diff([b], [a], 'expected output',
                                                 'program output'):
                    print(line)
                test_passes = (a == b)
            else:
                for line in difflib.unified_diff([_output], [_stdout],
                                                 'expected output',
                                                 'program output'):
                    print(line)
                test_passes = (_stdout == j_output.read())
    return test_passes


run_test(args.output, args.input)
