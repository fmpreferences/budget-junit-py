# budget-junit-py
junit for those who dont know. not as versatile as actual junit but easy to use

## usage:
```bash
budget-junit.py [-h] [-d DUMP] [-f FLAGS] [-i INPUT] [-m MATCHINPUT] [-s] source output
```

source: the java file to test. may have some unexpected behavior with flags

output: the stdout to compare to. can be a file or directories. will break if you dont specify an input file but the file needs an input to finish

-d: make a file with the given name that stores the program output

-f: compiler flags, may work very unexpectedly. i literally dont understand java enough to fix your error if it's related to this if you really need it, so, sorry

-i: the file to pass in as input for the program. can be a file or directories, but cannot be a file if the output is a directory

-m: matches group one of a regex pattern you pass in. new lines are automatically added in after group 1.

is ignored if -i is set

e.g. if inputs are denoted with {(.\*?)} group 1 is in (.\*?). make sure to escape properly in the shell.

note you may need to eat up the newline in your match pattern. if no group is specified, it uses group 0 by default; be warned that this may not be optimal. also note that more than 1 group will just match group 1. use (?:) accordingly.

depending on the shell you may need to escape a lot. for example the phrase (.\*?) needs every character to be escaped, which can be annoying. if you dont want to deal with this enclose the pattern in a string or pass an existing file in as the pattern.

-s: ignores white space, trailing space, space before and after newline, and duplicate newlines


## requirements:

python 3

java jdk for the javac and java commands

should be platform independent

## other:

this program creates temporary files because i couldnt find a way to feed input or parse output without using files
