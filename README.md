# budget-junit-py
junit for those who dont know. not as versatile as actual junit but easy to use

# usage
```bash
budget-junit.py [-h] [-d DUMP] [-f FLAGS] [-i INPUT] [-m MATCHINPUT] [-s] source output
```

source: the java file to test. may have some unexpected behavior with flags

output: the stdout to compare to. can be a file or (in development) directories

-d: make a file with the given name that stores the program output

-f: may work very unexpectedly

-i: the file to pass in as input for the program. can be a file or (in development) directories

-m: the output and input are in one file, where the input matches the given pattern. written in a way inputs are represented by a matching group. can directly be instantiated through shell or passing a file in. does not detect newlines for you.

is ignored if -i is set

e.g. if inputs are denoted with {(.\*?)} the actual input matches (.\*?)and is in {}. use \\ to escape special characters in shell and \\\\ to escape special characters in the regex

using no groups or more than one may create unexpected behavior.

depending on the shell you may need to escape a lot. for example the phrase (.*?) needs every character to be escaped, which can be annoying. if you dont want to deal with this enclose the pattern in a string or pass an existing file in as the pattern.

## requirements:

python 3

java jdk for the javac and java commands

should be platform independent

## other:

this program creates temporary files because i couldnt find a way to feed input or parse output without using files