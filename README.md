# budget-junit-py
```bash
usage: budget-junit.py [-h] [-d DUMP] [-f FLAGS] [-i INPUT] [-m MATCHINPUT] [-s] source output
```

source: the java file to test. may have some unexpected behavior with flags

output: the stdout to compare to. can be a file or (in development) directories

-d: make a file with the given name that stores the program output

-f: may work very unexpectedly

-i: the file to pass in as input for the program. can be a file or (in development) directories

-m: input and output are one file, and you use regex groups to match input from the output. may have unexpected behavior. (.*?) is recommended if you dont know what to do. make sure to use \\\\ correctly. automatically sends newline (\n character) for you. ignored if -i exists

## requirements:

python 3

java jdk for the javac and java commands

should be platform independent

## other:

this program creates temporary files because i couldnt find a way to feed input or parse output without using files