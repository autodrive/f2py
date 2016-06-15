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
                        key = line_strip_split[-1]
                        if key in function_names:
                            function_names[key].append((path, filename, line_number))
                        else:
                            function_names[key] = [(path, filename, line_number)]

    pprint(function_names)


def main():
    current_path = pwd()

    result = recursively_find_slycot()

    # pprint(result)
    find_slicot_function_names(result)

    os.chdir(current_path)


def recursively_find_slycot():
    result = {}
    for root, dirs, files in os.walk(os.pardir):
        if '.git' not in root and '.idea' not in root and not root.startswith('..\\build'):
            folder_list = process_folder(root, files)
            if folder_list:
                result[root] = folder_list
    return result


if __name__ == '__main__':
    main()
