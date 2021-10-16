import subprocess
from argparse import ArgumentParser
import re
from tempfile import TemporaryFile
import difflib

juparse = ArgumentParser(description='Tests your file compared to input')

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
    pattern. written in a way inputs are represented by a "."
    e.g. if inputs are denoted with [.] the actual input is in []. use \\.
    to escape
    ''')
juparse.add_argument('-s',
                     '--whitespace',
                     action='store_true',
                     help='if set ignores whitespace')

args = juparse.parse_args()
'''
main program
'''
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
        _stdout = input_output.read()
        if args.whitespace:
            a = re.sub(r'\s', '', _stdout)
            b = re.sub(r'\s', '', j_output.read())
            for line in difflib.context_diff(a, b):
                print(line)
            print(a == b)
        else:
            b = j_output.read()
            for line in difflib.context_diff(_stdout, b):
                print(line)
            print(_stdout == b)
        if args.dump is not None:
            with open(args.dump, 'w') as dump:
                dump.write(_stdout)
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
            _stdout = tstdout.read()
            if args.whitespace:
                print(re.sub(r'\s', '', _stdout) == re.sub(r'\s', '', _output))
            else:
                print(_stdout == _output)
            if args.dump is not None:
                with open(args.dump, 'w') as dump:
                    dump.write(_stdout)

else:
    with open(args.output) as j_output, TemporaryFile('a+') as input_output:
        subprocess.run(['java', args.source.split('.')[0]],
                       stdout=input_output)
        input_output.seek(0)
        _stdout = input_output.read()
        if args.whitespace:
            print(
                re.sub(r'\s', '', _stdout) == re.sub(r'\s', '',
                                                     j_output.read()))
        else:
            print(_stdout == j_output.read())
