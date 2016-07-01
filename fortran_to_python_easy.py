"""
convert fortran file to python if there is no go to
"""
import os

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


def main(fortran_filename):
    fortran_src = read_text_content(fortran_filename)

    fortran_lines = fortran_src.splitlines()

    python_lines = []

    # line loop
    for fortran_line in fortran_lines:
        if fortran_info.is_comment(fortran_line):
            python_line = '#' + fortran_line[1:]
        else:
            python_line = fortran_line
        python_lines.append(python_line)

    # write file
    python_filename = fortran_filename_to_python_filename(fortran_filename)
    write_python_file(python_filename, python_lines)


if __name__ == '__main__':
    args = os.path.join(os.pardir, 'pyslicot', 'SB02MT.f')
    from sys import argv

    if 1 < len(argv):
        args = argv[1]
    main(args)
