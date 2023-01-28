# Compiler

Author
------
Krzysztof Urbisz
261730

Requirements
------------
 * [Python][Python] 3.10.6
 * [Pip][Pip] 22.0.4
 * [Sly][Sly] 0.5

[Python]: https://www.python.org/downloads/release/python-3106/
[Pip]: https://pypi.org/project/pip/
[Sly]: https://pypi.org/project/sly/

Usage
-----
After downloading Python3 and Pip3 we will need Sly which can be installed with
```sh
pip install sly
```
Here we can already compile a program using
```sh
python3 CompMain.py INPUT_FILE OUTPUT_FILE
```
where INPUT_FILE means relative or absolute path to input file
and OUTPUT_FILE means path to output file which will be created
if it does not exist (whole missing path will be created).

For example if we want to compile file "in.txt" to "out.txt" in same folder we can just use
```sh
python3 CompMain.py in.txt out.txt
```

Important information
---------------------
 * There are features used in project which requires Python 3.10 (lower versions will not work properly)
 * There is optimization which substitute procedure's code if it was used once so it can catch more possibilities of not initialized variables (e.g. error6.imp)
