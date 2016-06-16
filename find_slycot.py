import os
import re
from pprint import pprint


def pwd():
    return os.path.abspath(os.curdir)


def process_file(path, file_name):
    result = []
    if ".py" == os.path.splitext(file_name)[-1]:
        f = open(file_name, 'r')
        txt = f.read()
        f.close()

        lines = txt.splitlines()

        for k, line in enumerate(lines):
            if "from" + " slycot import" in line:
                # print file_name, k, ':', line
                result.append((k, line))
    return result


def process_folder(root, files):
    current_path = pwd()
    os.chdir(os.path.abspath(root))

    folder_result = {}

    for file_name in files:
        file_result = process_file(root, file_name)
        if file_result:
            folder_result[file_name] = file_result

    os.chdir(current_path)

    return folder_result


def find_slicot_function_names(r):
    function_names = {}
    for path, files in r.items():
        for filename, lines in files.items():
            for line_number, line in lines:
                line_strip = line.strip()
                if not line_strip.startswith('#'):
                    line_strip_split = line_strip.split()
                    if 4 == len(line_strip_split):
                        handle_one_function_import(function_names, line_strip_split, path, filename, line_number)
                    elif 5 == len(line_strip_split):
                        handle_two_functions_import(function_names, line_strip_split, path, filename, line_number)

    return function_names


def print_sorted_keys(function_names):
    keys = function_names.keys()
    keys.sort()
    for i, key in enumerate(keys):
        print(i, key)
        print(function_names[key])


def handle_two_functions_import(function_names, line_strip_split, path, filename, line_number):
    keys = [line_strip_split[3][:-1], line_strip_split[4]]
    for key in keys:
        add_function_name(key, function_names, path, filename, line_number)


def handle_one_function_import(function_names, line_strip_split, path, filename, line_number):
    key = line_strip_split[-1]
    add_function_name(key, function_names, path, filename, line_number)


def add_function_name(key, function_names, path, filename, line_number):
    if key in function_names:
        function_names[key].append((path, filename, line_number))
    else:
        function_names[key] = [(path, filename, line_number)]


def recursively_find_slycot():
    result = {}
    for root, dirs, files in os.walk(os.pardir):
        if '.git' not in root and '.idea' not in root and not root.startswith('..\\build'):
            folder_list = process_folder(root, files)
            if folder_list:
                result[root] = folder_list
    return result


class RecursiveFinder(object):
    def __init__(self, initial_path=os.curdir):
        self.abs_return_path = os.path.abspath(os.curdir)
        abs_initial_path = os.path.abspath(initial_path)
        if not os.path.exists(abs_initial_path):
            raise IOError('File does not exist: %s' % abs_initial_path)
        elif not os.path.isdir(abs_initial_path):
            raise IOError('Not a directory: %s' % abs_initial_path)
        else:
            self.abs_initial_path = abs_initial_path


def main():
    current_path = pwd()

    result = recursively_find_slycot()

    # pprint(result)
    function_names = find_slicot_function_names(result)

    # pprint(function_names)
    print_sorted_keys(function_names)

    os.chdir(current_path)


if __name__ == '__main__':
    main()
