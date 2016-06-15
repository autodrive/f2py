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
            if "slycot" in line:
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


def main():
    current_path = pwd()

    result = {}
    for root, dirs, files in os.walk(os.pardir):
        if '.git' not in root and '.idea' not in root:
            folder_list = process_folder(root, files)
            if folder_list:
                result[root] = folder_list

    pprint(result)

    os.chdir(current_path)


if __name__ == '__main__':
    main()
