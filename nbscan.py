#! /usr/bin/env python3

# nbscan.py
#
# John Conery
# University of Oregon
# January 2017

# This script scans Jupyter notebooks to find cells matching specified criteria.  The
# script was developed for notebooks managed by nbgrader, but will work with any directory
# hiearchy.

# Run 'nbscan.py --help' to see examples.

import argparse
import os
import re
import random
import nbformat

from nbformat.reader import NotJSONError

def build_file_list(args):
    '''
    Return a list of file names to scan.  The list is initialized with names specified
    as positional arguments on the command line.  Then do a recursive search through
    any folders specified with --dir or --submitted options.  If the final list is empty
    (i.e. no notebook names on the command line and none found in directories) print a
    message and exit.
    '''
    
    def filter_argv_files(files):
        '''
        Make sure each file named on the command line exists, print an error message and
        exit unless all files are found.
        '''
        all_found = True
        for fn in args.files:
            if os.path.isfile(fn):
                files.add(fn)
            else:
                print('No such file:', fn)
                all_found = False
        if not all_found:
            exit(1)
        
    def add_files_in_dir(files, dirnames, projects=None):
        '''
        Do a recursive walk through the directories in dirnames, add the names of all 
        .ipynb files to files (the set of files to scan).  Skips folders with names
        that start with periods (e.g. ".ipynb_checkpoints" or ".sync")
        '''
        for dn in dirnames:
            for path, _, fnames in os.walk(dn):
                if '/.' in path:
                    continue
                if projects and not any(map(lambda p: p in path, projects)):
                    continue
                for fn in fnames:
                    if fn.endswith('.ipynb'):
                        files.add(os.path.join(path,fn))
                        
    file_set = set()
    
    filter_argv_files(file_set)

    if args.dir:
        add_files_in_dir(file_set, args.dir)
        
    if args.submitted:
        add_files_in_dir(file_set, ['submitted'], args.submitted)
        
    if len(file_set) == 0:
        print('No files to scan')
        exit(1)
    
    if args.random:
        return sorted(random.sample(file_set, args.random))
    else:
        return sorted(file_set)
        

def scan_files(files, args, pattern):
    '''
    Process the notebooks in the list of files.  Open each notebook and scan each cell,
    subjecting each cell to a series of filters.  Cells that pass all filters are then
    printed to stdout.
    '''
    
    def print_cell_ids(fn, lst):
        '''
        If --tags is on the command line print cell tag names instead of cell contents.
        '''
        print(fn)
        for tag in lst:
            print('  ', tag)
        print()

    def print_hits(fn, lst):
        '''
        Print the contents of cells that pass all the filters.  fn is the name of the
        file that contains the cells, lst is a list of cells from that file.  Unless
        --plain was specified on the command line the file name and the parts of the 
        cell that match the search pattern are printed in color.
        '''
        if not args.plain:
            print(highlight(fn))
            print(highlight('='*len(fn)))
        for source in lst:
            print(colorized(source))
            if not args.plain:
                print(highlight('---------'))
        print()
                
    def colorized(text):
        if args.plain or not pattern:
            return text
        else:
            return re.sub(pattern, lambda m: highlight(m.group(0),4), text, flags=re.IGNORECASE)
        
    def highlight(text, cn=1):
        return '\033[03{:1d}m{}\033[m'.format(cn, text)
        
    for fn in files:
        try:
            nb = nbformat.read(fn, args.nbformat)
        except (NotJSONError, UnicodeDecodeError) as e:
            print(e, fn)
            continue

        matches = []
        cell_type = 'code' if args.code else 'markdown' if args.markdown else None
        
        for cell in nb['cells']:
            tag = cell['metadata']['nbgrader'].get('grade_id') if 'nbgrader' in cell['metadata'] else None
            if cell_type and (cell['cell_type'] != cell_type):
                continue
            if args.id and tag != args.id:
                continue
            if pattern and (re.search(pattern, cell['source'], re.IGNORECASE) is None):
                continue
            if args.tags:
                if tag is not None:
                    matches.append(tag)
            else:
                matches.append(cell['source'])
            
        if len(matches) > 0:
            if args.tags:
                print_cell_ids(fn, matches)
            else:
                print_hits(fn, matches)

## Define command line arguments

desc = '''
Search for and print contents of cells in Jupyter notebooks. Cells can be filtered by type 
(code or markdown), by nbgrader tag ID, or by those that match a regular expression.  
Specify files to scan by name or recursively search a directory to find notebooks.
'''

epi = '''
Examples:

  $ nbscan.py source/hello/hello.ipynb --code
       print the contents of all the code cells in hello.ipynb in the source folder
       
  $ nbscan.py source/hello/hello.ipynb source/oop/oop.ipynb --markdown --grep color:red
       print the markdown cells in hello.ipyb and oop.ipynb that have the HTML style "color:red"
       
  $ nbscan.py --dir source --tags
       print the nbgrader cell IDs in all cells in all notebooks in the source folder
              
  $ nbscan.py --dir submitted/harry --dir submitted/hermione --id hello
       print the cell with nbgrader id 'hello' in any notebooks submitted by students
       named 'harry' or 'hermione'
              
  $ nbscan.py --dir source --markdown --grep ^#\{1,2\}\\s
       print the level 1 or level 2 headers in all notebooks in the source folder
       
  $ nbscan.py --dir source --markdown --prompt
       as above, but enter search pattern interactively, without shell quote characters: ^#{1,2}\s 
       
  $ nbscan.py --submitted hello --code --grep 'def hello'
       search all notebooks submitted for the hello project for code cells containing definitions
       of the hello function
       
  $ nbscan.py --submitted hello --id hello_doc --random 3
       print the contents of cells tagged hello_doc in the hello projects submitted by 3 random
       students
'''

def init_api():
    parser = argparse.ArgumentParser(description = desc, epilog=epi, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', metavar='FN', nargs='*', help="notebook files(s) to scan")
    parser.add_argument('--dir', metavar='DIR', action='append', help="find all notebooks in or below this directory")
    parser.add_argument('--submitted', metavar='X', action='append', help="search subdirectories of project or student name X")
    parser.add_argument('--random', metavar='N', type=int, help="find N random students")
    grep = parser.add_mutually_exclusive_group()
    grep.add_argument('--grep', metavar='P', help='look for cells containing pattern P')
    grep.add_argument('--prompt', action='store_true', help='prompt for grep pattern')
    celltype = parser.add_mutually_exclusive_group()
    celltype.add_argument('--id', metavar='X', help='search nbgrader cells with this ID')
    celltype.add_argument('--code', action='store_true', help='scan code cells only')
    celltype.add_argument('--markdown', action='store_true', help='scan markdown cells only')
    parser.add_argument('--tags', action='store_true', help='print cell IDs instead of contents')
    parser.add_argument('--nbformat', metavar='N', type=int, default=4, help='Jupyter notebook format (default: 4)')
    parser.add_argument('--plain', action='store_true', help='plain text output (no headers, colors)')
    return parser.parse_args()

if __name__ == '__main__':
    args = init_api()
    
    if args.prompt:
        pattern = input('pattern: ')
        
    lst = build_file_list(args)
    scan_files(lst, args, args.grep or (args.prompt and pattern))

