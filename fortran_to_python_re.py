"""
convert fortran file to python if there is no go to
"""
import os
import re


def read_text_content(filename):
    f = open(filename, 'rt')
    txt = f.read()
    f.close()
    return txt


def replace_fortran_comments_to_python(txt):
    comment_replaced_txt = re.sub(pattern='^[^\s]', repl='#', string=txt, flags=re.MULTILINE)
    return comment_replaced_txt


def replace_fortran_continue_to_next_line_to_python(txt):
    dollar6_replaced_txt = re.sub(pattern=r'\n\s{5}[^\s]\s+', repl=' ', string=txt, flags=re.MULTILINE)
    return dollar6_replaced_txt


class FortranVariableDeclarationParser:
    def __init__(self, variable_declaration_txt, type_name):
        self.type_name = type_name
        self.declaration_txt = variable_declaration_txt
        self.declaration_txt = self.declaration_txt.replace('(', ' ( ')
        self.declaration_txt = self.declaration_txt.replace(')', ' ) ')

        self.location = 0
        self.variable_info_list = []

        self.splitter = re.compile(r"[\w%s']+" % re.escape('=.()*+-/<>!:'))

    def split_symbols(self):
        # http://stackoverflow.com/questions/1059559/python-split-strings-with-multiple-delimiters
        # https://docs.python.org/2/library/re.html#re.escape

        # split fortran line using delimiters as above
        return self.splitter.findall(self.declaration_txt)

    def parse(self):
        self.variable_info_list = self.split_symbols()
        while len(self.declaration_txt) > self.location:
            self.location += 1

        return self.variable_info_list


def find_type_variable_names(fortran_source_txt, type_name):
    """
    Detect variable declarations
    :param fortran_source_txt: str Fortran source code
    :param type_name: str e.g., CHARACTER, DOUBLE PRECISION, ...
    :return:tuple of variable name strings
    """
    # lines starting with type name :
    variable_lines = re.findall(r'^\s{6}%s\s+(.+)' % type_name, fortran_source_txt, flags=re.MULTILINE)

    variable_names = []
    for variable_line in variable_lines:
        # split variable_line with word bounds
        variable_names_in_line = re.split(r"\s|,", variable_line)

        # add variable names found in one line to the big list
        variable_names += variable_names_in_line

    # TODO : can we do it with one line

    return tuple(variable_names)


def main(fortran_filename):
    fortran_src = read_text_content(fortran_filename)

    comment_replaced_src = replace_fortran_comments_to_python(fortran_src)
    dollar6_replaced_src = replace_fortran_continue_to_next_line_to_python(comment_replaced_src)

    print(dollar6_replaced_src)


if __name__ == '__main__':
    args = os.path.join(os.pardir, 'pyslicot', 'SB02MT.f')
    from sys import argv

    if 1 < len(argv):
        args = argv[1]
    main(args)
