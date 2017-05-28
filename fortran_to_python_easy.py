"""
convert fortran file to python if there is no go to
"""
import os
import re

import fortran_info


def read_text_content(filename):
    with open(filename, 'rt') as f:
        txt = f.read()

    return txt


def fortran_filename_to_python_filename(fortran_filename):
    """
    ***.f or ***.for -> ***.py

    :type fortran_filename: str
    :return: str
    """
    return ''.join((os.path.splitext(fortran_filename)[0].lower(), '.py'))


def write_python_file(python_filename, python_lines):
    """
    write a list of python script lines into a text file

    :type python_filename:str
    :type python_lines:list, tuple
    :rtype: None
    """
    f = open(python_filename, 'wt')
    for python_line in python_lines:
        f.write('%s\n' % python_line)
    f.close()


def replace_logical_operators(fortran_src):
    """
    apply logical_operators tuple pair
    :param fortran_src:str
    :return:str
    """
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

    return replace_loop(fortran_src, logical_operators, ' ')


def replace_symbol(fortran_src):
    """
    Insert separator ' ' before and after '(' and ')'

    Parameters
    ----------
    fortran_src

    Returns
    -------

    """
    logical_operators = (
        ('(', '('),
        (')', ')'),
    )

    return replace_loop(fortran_src, logical_operators, ' ')


def replace_else_if(fortran_src):
    # https://docs.python.org/2/howto/regex.html
    # http://stackoverflow.com/questions/6116978/python-replace-multiple-strings

    replace_these = {
        ' ELSE IF ': ' elif ',
        ' ELSE IF(': ' elif (',
    }

    replace_keys_these = dict((re.escape(k), v) for k, v in replace_these.items())
    r = re.compile("|".join(replace_keys_these.keys()))
    after = r.sub(lambda m: replace_keys_these[re.escape(m.group(0))], fortran_src)

    # print(after)

    return after


def replace_continue(fortran_src):
    # https://docs.python.org/2/howto/regex.html
    # http://stackoverflow.com/questions/6116978/python-replace-multiple-strings

    r = re.compile(r'(?P<label>\d+)\s+(?P<keyword>CONTINUE)')
    # 20 CONTINUE
    # match.group('label') == 20

    after = r.sub(lambda m: '# end_for %s' % m.group('label'), fortran_src)

    # print(after)

    return after


def replace_two_word_keywords(fortran_src):
    # https://docs.python.org/2/howto/regex.html
    # http://stackoverflow.com/questions/6116978/python-replace-multiple-strings
    replace_these = {
        ' END IF\n': ' # end_if\n',
        r' ELSE IF(': ' elif (',
        r' ELSE IF ': ' elif ',
    }
    # check indent_logic()

    replace_dict = dict((re.escape(k), v) for k, v in replace_these.items())
    pattern = re.compile("|".join(replace_dict.keys()))
    after = pattern.sub(lambda m: replace_dict[re.escape(m.group(0))], fortran_src)

    # print(after)

    return after


def undo_replace_symbol(fortran_src):
    logical_operators = (
        (' ( ', '('),
        (' ) ', ')'),
    )

    return replace_loop(fortran_src, logical_operators)


def replace_loop(fortran_src, pairs, separator=''):
    """

    :param str fortran_src:
    :param list(tuple) | tuple(tuple) pairs:
    :param str separator:
    :return:str
    """
    before = str(fortran_src)
    after = fortran_src
    for old, new in pairs:
        after = before.replace(old, ('%s%s%s' % (separator, new, separator)))
        before = after
    return after


def replace_word(fortran_word):
    """
    apply lookup tables of 1:1 keywords
    :param fortran_word:
    :return:
    """
    python_word = {
        'SUBROUTINE': 'def',
        'DO': 'for',
        'IF': 'if',
        'THEN': ':',
        'ELSE': 'else:',
        'END': '# end of subroutine',
    }
    return python_word[fortran_word]


def indent_logic(python_line_list_split, tab_stop=4):
    # TODO : check consistency of keywords : python or Fortran?
    # TODO : One line if
    # TODO : replace continue

    increase_next = {'SUBROUTINE', 'IF', 'DO'}
    decrease_next = {'end_if', 'CONTINUE'}
    decrease_itself = {'SUBROUTINE', 'elif', 'ELSE', 'end_if', 'CONTINUE', 'END'}

    next_indent = 0

    stack = []

    for line in python_line_list_split:
        if '#' != line[0]:
            indent = next_indent
            for word in line:
                if word in decrease_itself:
                    indent = max((0, indent - tab_stop))

                if word in increase_next:
                    stack.append(list(line))
                    next_indent = indent + tab_stop
                    break
                elif word in decrease_next:
                    append_this = stack.pop()
                    append_this.insert(0, '#')
                    line.append(append_this)
                    next_indent = indent
                    break

            if indent < 0:
                indent = 0
            elif indent > 100:
                raise Exception('indent > 100')

            format_string = '%' + str(indent) + 'd'
            line.insert(0, format_string % len(stack))
    # end of indent loop


def main(fortran_filename, b_include_fortran=True):
    fortran_src = read_text_content(fortran_filename)

    # >, <, ==, !=, ...
    fortran_src_logic_replaced = replace_logical_operators(fortran_src)
    del fortran_src

    #  ')' --> ' ) '
    fortran_src_symbol_replaced = replace_symbol(fortran_src_logic_replaced)
    del fortran_src_logic_replaced

    # end if, else if
    fortran_src_keywords_replaced = replace_two_word_keywords(fortran_src_symbol_replaced)

    fortran_lines = fortran_src_keywords_replaced.splitlines()
    del fortran_src_symbol_replaced

    python_lines = []

    # line loop
    for k, fortran_line in enumerate(fortran_lines):
        if fortran_info.is_comment(fortran_line):
            python_line = '#' + fortran_line[1:]
            python_line_undo = undo_replace_symbol(python_line)
            del python_line
            python_lines.append(python_line_undo)
        else:
            # if 6th column is not white space
            if fortran_info.is_continue_previous_line(fortran_line):
                last_line = python_lines.pop()
                python_line = last_line + split_symbols(fortran_line)
            else:
                python_line = split_symbols(fortran_line)
            if b_include_fortran:
                python_lines.append('#' + fortran_line)
            python_lines.append(python_line)

    indent_logic(python_lines)

    # write file
    python_filename = fortran_filename_to_python_filename(fortran_filename)
    write_python_file(python_filename, python_lines)


def split_symbols(fortran_line):
    # http://stackoverflow.com/questions/1059559/python-split-strings-with-multiple-delimiters
    # https://docs.python.org/2/library/re.html#re.escape

    # add '\' in front of all characters to use as delimiters
    delimiters = re.escape('=.()*+-/<>!:')

    # split fortran line using delimiters as above
    python_line = re.findall(r"[\w%s']+" % delimiters, fortran_line)
    return python_line


if __name__ == '__main__':
    args = os.path.join(os.pardir, 'pyslicot', 'SB02MT.f')
    from sys import argv

    if 1 < len(argv):
        args = argv[1]
    main(args)
