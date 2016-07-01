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
