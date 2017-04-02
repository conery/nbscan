# nbscan

nbscan.py is a Python script that will search for and print contents of cells in Jupyter notebooks. 
The script was written to search through notebooks managed by the nbgrader pipline (http://nbgrader.readthedocs.io) but will
work for any Jupyter notebooks.

Cells can be filtered by type 
(code or markdown), by nbgrader tag ID, or by those that match a regular expression.  
Specify files to scan by name or recursively search a directory to find notebooks.

## Usage

```
nbscan.py FILES [--dir D] [--submitted X] [--code | --markdown | --id X] [options]
```

FILES can be a list of 0 or more notebook file names; if names are given each file is scanned to find cells
that match search critera.

If a directory is specified with `--dir` then that directory is recursively searched for notebooks (files 
with names ending in `.ipynb`) and those notebooks are added to the list of files to scan.  `--dir` can be
used more than once to search several directories.

The `--submitted` option is like `--dir`, except it searches below the `submitted` folder.  Assuming the
default project organization (submitted/student/project) specifying `--submitted X` can be used to search
for all notebooks submitted for project X, across all students.

Use `--code` or `--markdown` to scan only code cells or markdown cells, or `--id X` to scan only cells that
have X as their nbgrader ID.  These three options are mutually exclusive.

Other options are:
* `--grep P` will print only cells the match the pattern P; the pattern can be specified using regular expression syntax
* `--prompt` is the same as `--grep`, but prompts the user to enter the pattern (avoiding messy shell escapes)
* `--tags` asks the program to print the names of all the nbgrader IDs in notebooks
* `--random N` prints cells from N notebooks selected at random instead of all the notebooks
* `--plain` suppresses coloring of the parts of cells that match patterns
* `--nbformat N` specifies an IPython notebook version (the default is 4)

## Examples

These examples assume the script is being run in the top level directory of a course managed by nbgrader,
i.e. there are subdirectories named source, release, submitted, etc.

Print the contents of all the code cells in `hello.ipynb` in the `source` folder:
```
$ nbscan.py source/hello/hello.ipynb --code
```

Print the markdown cells in `hello.ipyb` and `oop.ipynb` that contain the string "color:red" somewhere in the cell:
```
$ nbscan.py source/hello/hello.ipynb source/oop/oop.ipynb --markdown --grep color:red
```

If `--tags` is specified the script prints nbgrader cell IDs instead of cell contents.  
This command prints the nbgrader cell IDs in all cells in all notebooks in the `source` folder:
```
$ nbscan.py --dir source --tags
```

Print the cell with nbgrader id `hello` in any notebooks submitted by students named 'harry' or 'hermione':
```
$ nbscan.py --dir submitted/harry --dir submitted/hermione --id hello
```

Print the level 1 or level 2 headers in all notebooks in the `source` folder:
```
$ nbscan.py --dir source --markdown --grep ^#\{1,2\}\\s
```

As above, but enter search pattern interactively, without shell quote characters; simply enter `^#{1,2}\s` when prompted:
```
$ nbscan.py --dir source --markdown --prompt
```

Search all notebooks submitted for the `hello` project for code cells containing definitions of the `hello` function:
```
$ nbscan.py --submitted hello --code --grep 'def hello'
```

Print the contents of cells tagged `hello_doc` in the hello projects submitted by 3 random students:
```
$ nbscan.py --submitted hello --id hello_doc --random 3
```

## Demo Project

The file named `demo.tar` contains a course folder that can be used to test the script using the commands in the examples above.
The archive will expand into a course folder named `demo`, complete with a course database
(`demo.db`) and `source`, `release`, `submitted`, `autograded`, and `feedback` folders.  There are two
projects, named `hello` and `oop`, and five students, with submitted notebooks for each student.
