import subprocess
from argparse import ArgumentParser
from dataclasses import dataclass
import re
from tempfile import TemporaryFile
import difflib
import os


@dataclass
class TestResult:
    test_pass: bool
    stdout: str
    expected_out: str

    def print_diff(self):
        '''prints the diff and returns if the test passed'''
        if self.test_pass:
            print('test pass')
        else:
            print('test fail')
        for line in difflib.unified_diff(self.expected_out.split('\n'),
                                         self.stdout.split('\n'),
                                         'expected output', 'program output'):
            print(line)


def main():
    junit_parser = parser_setup()

    args = junit_parser.parse_args()

    if args.flags:
        subprocess.run(['javac', args.source, *args.flags.split(' ')])
    else:
        subprocess.run(['javac', args.source])

    pattern = args.matchinput
    if pattern:
        if os.path.isfile(pattern):
            with open(pattern) as pattern_f:
                pattern = pattern_f.read()
        print(f'checking for pattern:\n{pattern}')
    out_is_file = os.path.isfile(args.output)
    out_is_directory = os.path.isdir(args.output)

    in_is_directory = in_is_file = False

    if args.input:
        in_is_file = os.path.isfile(args.input)
        in_is_directory = os.path.isdir(args.input)
        if in_is_file and out_is_file:
            results = run_test(args.output, args, pattern, args.input)
            results.print_diff()
            if args.dump:
                with open(args.dump, 'w') as dump:
                    dump.write(results.stdout)
        elif in_is_directory and out_is_directory:
            compare_mulitple(args, pattern)
        else:
            print('''
            cannot have one input or output corresponding to multiple inputs
            or outputs!''')
    else:
        if out_is_file:
            results = run_test(args.output, args, pattern)
            results.print_diff()
            if args.dump:
                with open(args.dump, 'w') as dump:
                    dump.write(results.stdout)
        elif out_is_directory:
            compare_mulitple(args, pattern)


def parser_setup() -> ArgumentParser:
    '''sets up the ArgParser that reads from the command line
    '''
    junit_parser = ArgumentParser(
        description='''tests the output of [source] file against the [output].
        if using multiple outputs then make sure to match your input names as well'''
    )

    junit_parser.add_argument('source',
                              type=str,
                              help='the path of the source code')
    junit_parser.add_argument(
        'output', type=str, help='the path of the file containing the output')
    junit_parser.add_argument('-d',
                              '--dump',
                              type=str,
                              help='file to dump stdout to')
    junit_parser.add_argument('-f',
                              '--flags',
                              type=str,
                              help='special javac flags and arguments')
    junit_parser.add_argument('-i',
                              '--input',
                              type=str,
                              help='the path of the file containing the input')
    junit_parser.add_argument(
        '-m',
        '--matchinput',
        type=str,
        help=
        '''the output and input are in one file, where the input matches the given
        pattern. written in a way inputs are represented by a matching group. can
        directly be instantiated through shell or passing a file in. does not
        detect newlines for you
        e.g. if inputs are denoted with {(.*?)} the actual input matches (.*?)
        and is in {}. use \\ or quotes to escape special characters in shell
        and the right no. of backslashes to escape special characters in the regex.
        IMPORTANT: regex rules work so you can use any input matching you want but
        make sure to specify a matching group, any further groups after group 1 may
        be ignored. if the inputs are not matched right try escaping with more \\
        ''')
    junit_parser.add_argument('-s',
                              '--whitespace',
                              action='store_true',
                              help='if set ignores whitespace at end of lines')
    return junit_parser


def run_test(output, args, pattern=None, iinput=None) -> TestResult:
    '''run a test comparing the program output to the source output
    '''
    if iinput:
        with open(iinput) as jstdin, TemporaryFile('a+') as input_output, open(
                output) as expected_out:
            input_output.truncate(0)
            subprocess.run(['java', args.source.split(".")[0]],
                           stdin=jstdin,
                           stdout=input_output)
            input_output.seek(0)
            jstdout = input_output.read()
            expected_out = expected_out.read()
            return compare_outputs(args, jstdout, expected_out)
    elif pattern:
        with open(output) as expected_out:
            o = expected_out.read()
            _input, _output = separate_inputs(o, pattern)
            with TemporaryFile('a+') as tinput, TemporaryFile(
                    'a+') as toutput, TemporaryFile('a+') as tstdout:
                tinput.write(_input)
                tinput.seek(0)
                toutput.write(
                    _output)  # regardless of whitespace, take care after
                toutput.seek(0)
                subprocess.run(['java', args.source.split(".")[0]],
                               stdin=tinput,
                               stdout=tstdout)
                toutput.seek(0)
                tstdout.seek(0)
                _stdout = tstdout.read()
                return compare_outputs(args, _stdout, _output)
    else:
        with open(output) as expected_out, TemporaryFile('a+') as input_output:
            subprocess.run(['java', args.source.split('.')[0]],
                           stdout=input_output)
            input_output.seek(0)
            _stdout = input_output.read()
            expected_out = expected_out.read()
            return compare_outputs(args, _stdout, expected_out)


def compare_outputs(args, stdout, expected_out) -> TestResult:
    '''compares stdout with expected_out and returns the test result'''
    if args.whitespace:
        stdout_filtered = re.sub(r'(\s*?\n+)+', '\n', stdout).strip()
        expected_out_filtered = re.sub(r'(\s*?\n+)+', '\n',
                                       expected_out).strip()
        return TestResult(stdout_filtered == expected_out_filtered,
                          stdout_filtered, expected_out_filtered)
    else:
        return TestResult(stdout == expected_out, stdout, expected_out)


def separate_inputs(string, pattern) -> (str, str):
    '''return a tuple that returns input and output

    note the input already adds the newline after each line due to
    technical limitation'''
    def group_1(match):
        try:
            return match.group(1)
        except IndexError:
            return match.group()

    return '\n'.join(map(group_1, re.finditer(
        pattern, string))) + '\n', re.sub(pattern, "", string)


def compare_mulitple(args, pattern) -> None:
    '''compares the output or optional input given
    they are directories'''
    attempted = found = success = 0
    for root, _, files in os.walk(args.output):
        for f in files:
            try:
                test_case = os.path.join(root, f)
                if args.input:
                    input_test_case = os.path.join(
                        root.replace(args.output, args.input, 1), f)
                print(f'trying test case {f} in {test_case}...')
                results = run_test(test_case, args, pattern, input_test_case)
                results.print_diff()
                if results.test_pass:
                    success += 1
                if args.dump:
                    with open(
                            os.path.join(
                                root.replace(args.output, args.dump, 1), f),
                            'w') as dump:
                        dump.write(results.stdout)
                found += 1
            except FileNotFoundError:
                print(f"test case '{f}' in {test_case} not found, skipping")
            attempted += 1
    print(
        f'{attempted} cases attempted, {success} cases out of {found} found cases passed'
    )


if __name__ == '__main__':
    main()
