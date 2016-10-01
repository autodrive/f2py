"""
convert fortran file to python if there is no go to
"""
import os


def read_text_content(filename):
    f = open(filename, 'rt')
    txt = f.read()
    f.close()

    return txt


def main(fortran_filename):
    fortran_src = read_text_content(fortran_filename)
    print(fortran_src)


if __name__ == '__main__':
    args = os.path.join(os.pardir, 'pyslicot', 'SB02MT.f')
    from sys import argv

    if 1 < len(argv):
        args = argv[1]
    main(args)
