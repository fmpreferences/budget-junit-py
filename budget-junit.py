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
    pattern. written in a way inputs are represented by a matching group. can
    directly be instantiated through shell or passing a file in. does not 
    detect newlines for you
    e.g. if inputs are denoted with {(.*?)} the actual input matches (.*?)
    and is in {}. use \\ to escape special characters in shell and \\\\
    to escape special characters in the regex. 
    IMPORTANT: regex rules work so you can use any input matching you want but
    avoid using grouping other than the one matching input because it will
    break. if the inputs are not matched right try escaping with more \\
    ''')
juparse.add_argument('-s',
                     '--whitespace',
                     action='store_true',
                     help='if set ignores whitespace at end of lines')

args = juparse.parse_args()

if args.flags is not None:
    subprocess.run(['javac', args.source, *args.flags.split(' ')])
else:
    subprocess.run(['javac', args.source])

pattern = args.matchinput
if pattern is not None:
    if os.path.isfile(pattern):
        with open(pattern) as pattern_f:
            pattern = pattern_f.read()
    print(f'checking for pattern:\n{pattern}')


def run_test(output, iinput=None) -> dict:
    '''run a test comparing the program output to the source output,
    with an optional input iinput

    returns dict with keys:
        'test_pass': whether or not the test passed
        'stdout': the output of the source file
        'expected_out': the output that was expected
    '''
    global args, pattern
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
                a = re.sub(r'(\s*?\n+)+', '\n', _stdout)
                b = re.sub(r'(\s*?\n+)+', '\n', j_output.read())
                return {
                    'test_pass': a == b,
                    'stdout': a,
                    'expected_out': b
                }  # is there a better way? please?
            else:
                b = j_output.read()
                return {
                    'test_pass': _stdout == b,
                    'stdout': _stdout,
                    'expected_out': b
                }

    elif pattern is not None:
        with open(output) as j_output:
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
                    a = re.sub(r'(\s*?\n+)+', '\n', _stdout)
                    b = re.sub(r'(\s*?\n+)+', '\n', _output)
                    test_passes = (a == b)
                    return {
                        'test_pass': a == b,
                        'stdout': a,
                        'expected_out': b
                    }
                else:
                    return {
                        'test_pass': _stdout == _output,
                        'stdout': _stdout,
                        'expected_out': _output
                    }

    else:
        with open(output) as j_output, TemporaryFile('a+') as input_output:
            subprocess.run(['java', args.source.split('.')[0]],
                           stdout=input_output)
            input_output.seek(0)
            _stdout = input_output.read()
            if args.whitespace:
                a = re.sub(r'(\s*?\n+)+', '\n', _stdout)
                b = re.sub(r'(\s*?\n+)+', '\n', j_output.read())
                return {'test_pass': a == b, 'stdout': a, 'expected_out': b}
            else:
                _output = j_output.read()
                return {
                    'test_pass': _stdout == _output,
                    'stdout': _stdout,
                    'expected_out': _output
                }

    return test_passes


out_is_file = os.path.isfile(args.output)
out_is_directory = os.path.isdir(args.output)

in_is_directory = in_is_file = False

if args.input is not None:
    in_is_file = os.path.isfile(args.input)
    in_is_directory = os.path.isdir(args.input)
else:
    if out_is_file:
        results = run_test(args.output)
        if results['test_pass']:
            print('test pass')
        else:
            print('test fail')
        for line in difflib.unified_diff(results['expected_out'].split('\n'),
                                         results['stdout'].split('\n'),
                                         'expected output', 'program output'):
            print(line)
    elif out_is_directory:
        for root, _, files in os.walk(args.output):
            for f in files:
                test_case = os.path.join(root, f)
                print(f'trying test case {f} in {test_case}...')
                results = run_test(test_case)
                if results['test_pass']:
                    print('test pass')
                else:
                    print('test fail')
                for line in difflib.unified_diff(
                        results['expected_out'].split('\n'),
                        results['stdout'].split('\n'), 'expected output',
                        'program output'):
                    print(line)
                if args.dump is not None:
                    with open(
                            os.path.join(
                                root.replace(args.output, args.dump, 1), f),
                            'w') as dump:
                        dump.write(results['stdout'])

if args.matchinput is None:
    if in_is_file and out_is_file:
        results = run_test(args.output, args.input)
        if results['test_pass']:
            print('test pass')
        else:
            print('test fail')
        for line in difflib.unified_diff(results['expected_out'].split('\n'),
                                         results['stdout'].split('\n'),
                                         'expected output', 'program output'):
            print(line)
        if args.dump is not None:
            with open(args.dump, 'w') as dump:
                dump.write(results['stdout'])
    elif in_is_directory and out_is_directory:
        for root, _, files in os.walk(args.output):
            for f in files:
                try:
                    test_case = os.path.join(root, f)
                    input_test_case = os.path.join(
                        root.replace(args.output, args.input, 1), f)
                    print(f'trying test case {f} in {test_case}...')
                    results = run_test(test_case, input_test_case)
                    if results['test_pass']:
                        print('test pass')
                    else:
                        print('test fail')
                    for line in difflib.unified_diff(
                            results['expected_out'].split('\n'),
                            results['stdout'].split('\n'), 'expected output',
                            'program output'):
                        print(line)
                    if args.dump is not None:
                        with open(
                                os.path.join(
                                    root.replace(args.output, args.dump, 1),
                                    f), 'w') as dump:
                            dump.write(results['stdout'])
                except FileNotFoundError:
                    print(
                        f"test case '{f}' in {test_case} not found, skipping")

    else:
        print('''
        cannot have one input or output corresponding to multiple inputs
        or outputs!''')
