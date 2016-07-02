import re


whitespace = (' ', '\t')  # '\t' rarely used in .f files


def is_comment(fortran_line):
    result = not (fortran_line[0] in whitespace)
    return result


def is_continue_previous_line(fortran_line):
    result = False

    if not is_comment(fortran_line):
        if 6 < len(fortran_line):
            result = not (fortran_line[6 - 1] in whitespace)

    return result


def search_else_if(fortran_code):
    # https://docs.python.org/2/howto/regex.html#regex-howto
    pattern = r'\s(ELSE\sIF)\s*\('

    r = re.compile(pattern)
    return r.search(fortran_code)


def search_continue(fortran_code):
    pattern = r'(?P<label>\d+)\s+(?P<keyword>CONTINUE)'

    r = re.compile(pattern)
    return r.search(fortran_code)


def list_externals(fortran_code):
    fortran_lines = fortran_code.splitlines()

    result = []
    last_line = ''
    b_found = False

    for line in fortran_lines:
        if is_comment(line):
            # ignore comment
            pass
        elif is_continue_previous_line(line):
            # ignore continue for now
            pass
        else:
            # http://stackoverflow.com/questions/1059559/python-split-strings-with-multiple-delimiters
            result.append(re.findall(r"[\w']+", line))

    return result
