"""
convert fortran file to python if there is no go to
"""
import os
import re

import fortran_info
import wapj_logger

logger = wapj_logger.initialize_logger('f2py_easy.log')


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


def replace_continue(multi_line_fortran_src):
    # https://docs.python.org/2/howto/regex.html
    # http://stackoverflow.com/questions/6116978/python-replace-multiple-strings

    r = re.compile(r'(?P<label>\d+)\s+(?P<keyword>CONTINUE)')
    # 20 CONTINUE
    # match.group('label') == 20

    after = r.sub(lambda m: '# end_for %s' % m.group('label'), multi_line_fortran_src)

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
        'RETURN': 'return',
        'CALL': '',  # call a subroutine
        'CONTINUE': '# continue',
    # placeholder for a label https://docs.oracle.com/cd/E19957-01/805-4939/6j4m0vn83/index.html
        'end_if': '# end_if',
    }
    return python_word[fortran_word]


def get_first_word(line_list):
    """
    To handle [label] CONTINUE correctly
    
    :param list(str) line_list: 
    :return: 
    """
    result = ''
    for word in line_list:
        if not word.isdigit():
            result = word
            break

    return result


def decide_indent_level(python_line_list_split, tab_stop=4):
    push_dict = {'SUBROUTINE': {'pop': {'end'},
                                'passing': set()},
                 'IF': {'pop': {'end_if'},
                        'passing': {'elif', 'ELSE'}},
                 'DO': {'pop': {'CONTINUE'},
                        'passing': set()},
                 }

    indent_stack = []
    for line_list in python_line_list_split:
        b_pushed = False
        word = get_first_word(line_list)

        if 'IF' == word:
            # to handle one-line if lines correctly
            if 'THEN' == line_list[-1]:
                b_pushed = True
                indent_stack.append(word)
        elif word in push_dict:
            indent_stack.append(word)
            b_pushed = True
        elif indent_stack:
            if word in push_dict[indent_stack[-1]]['pop']:
                indent_stack.pop()
            elif word in push_dict[indent_stack[-1]]['passing']:
                b_pushed = True

        if isinstance(line_list, list):
            if b_pushed:
                indent = len(indent_stack) - 1
            else:
                indent = len(indent_stack)

            format_string = '%' + str(indent * tab_stop) + 'd'
            line_list.insert(0, format_string % indent)


def f2py(fortran_src, b_include_fortran=True):
    # >, <, ==, !=, ...
    fortran_src_logic_replaced = replace_logical_operators(fortran_src)
    del fortran_src

    #  ')' --> ' ) '
    fortran_src_symbol_replaced = replace_symbol(fortran_src_logic_replaced)
    del fortran_src_logic_replaced

    # end if, else if
    fortran_src_keywords_replaced = replace_two_word_keywords(fortran_src_symbol_replaced)
    del fortran_src_symbol_replaced

    fortran_lines = fortran_src_keywords_replaced.splitlines()
    del fortran_src_keywords_replaced

    python_lines = []

    # line loop
    for k, fortran_line in enumerate(fortran_lines):
        fortran_line_str = str(fortran_line)

        if fortran_info.is_comment(fortran_line_str):
            # mark comment lines
            python_line_00 = '#' + fortran_line_str[1:]
            # if comment, undo adding spaces around '(' & ')'.
            python_line = undo_replace_symbol(python_line_00)
            del python_line_00
        else:

            if fortran_info.is_continue_previous_line(fortran_line_str):
                # merge continuing lines
                last_line = python_lines.pop()
                python_line = last_line + split_symbols(fortran_line_str)
            else:
                # split around '(', ')', ',', ...
                python_line = split_symbols(fortran_line_str)

            if b_include_fortran:
                python_lines.append('#' + fortran_line_str)

        python_lines.append(python_line)

    del fortran_lines[:]
    del fortran_lines

    decide_indent_level(python_lines)
    return python_lines


def main(fortran_filename, b_include_fortran=True):
    fortran_src = read_text_content(fortran_filename)

    python_lines = f2py(fortran_src, b_include_fortran=b_include_fortran)

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
    logger.info('start program '.ljust(60, '='))
    from sys import argv
    try:
        main(argv[1])
    except IndexError:
        msg = "Try to convert fortran file to python if there is no go to\n" \
            '$ python %s [path to a fortran file]' % os.path.split(__file__)[-1]
        print(msg)
    logger.info('end program '.ljust(60, '='))
