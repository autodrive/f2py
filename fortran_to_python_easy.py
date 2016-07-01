"""
convert fortran file to python if there is no go to
"""
import os
import re

import fortran_info


def read_text_content(filename):
    f = open(filename, 'rt')
    txt = f.read()
    f.close()

    return txt


def fortran_filename_to_python_filename(fortran_filename):
    return ''.join((os.path.splitext(fortran_filename)[0].lower(), '.py'))


def write_python_file(python_filename, python_lines):
    f = open(python_filename, 'wt')
    for python_line in python_lines:
        f.write('%s\n' % python_line)
    f.close()


def replace_logical_operators(fortran_src):
    logical_operators = (
        ('.EQ.', '=='),
        ('.NE.', '!='),
        ('.LT.', '<'),
        ('.LE.', '<='),
        ('.GE.', '>='),
        ('.GT.', '>'),
        ('.OR.', 'or'),
        ('.AND.', 'and'),
        ('.NOT.', 'not'),
    )

    before = str(fortran_src)
    for old, new in logical_operators:
        after = before.replace(old, (' %s ' % new))
        before = after

    return after


def main(fortran_filename):
    fortran_src = read_text_content(fortran_filename)

    fortran_src = replace_logical_operators(fortran_src)

    fortran_lines = fortran_src.splitlines()

    python_lines = []

    # line loop
    for k, fortran_line in enumerate(fortran_lines):
        if fortran_info.is_comment(fortran_line):
            python_line = '#' + fortran_line[1:]
        elif fortran_info.is_continue_previous_line(fortran_line):
            last_line = python_lines.pop()
            python_line = last_line + split_symbols(fortran_line)
        else:
            python_line = split_symbols(fortran_line)
        python_lines.append(python_line)

    # write file
    python_filename = fortran_filename_to_python_filename(fortran_filename)
    write_python_file(python_filename, python_lines)


def split_symbols(fortran_line):
    # # http://stackoverflow.com/questions/1059559/python-split-strings-with-multiple-delimiters
    python_line = re.findall(r"[\w=\.\(\)*\[\]']+", fortran_line)
    return python_line


if __name__ == '__main__':
    args = os.path.join(os.pardir, 'pyslicot', 'SB02MT.f')
    from sys import argv

    if 1 < len(argv):
        args = argv[1]
    main(args)
