def is_comment(fortran_line):
    whitespace = (' ', '\t')  # '\t' rarely used in .f files
    result = not (fortran_line[0] in whitespace)
    return result
