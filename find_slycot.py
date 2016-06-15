import os
import re


def pwd():
    return os.path.abspath(os.curdir)


def process_file(file_name):
    if ".py" == os.path.splitext(file_name)[-1]:
        with open(file_name, 'r') as f:
            txt = f.read()
            f.close()

            lines = txt.splitlines()

            for k, line in enumerate(lines):
                if "slycot" in line:
                    print file_name, k, ':', line


def process_folder(root, files):
    current_path = pwd()
    os.chdir(os.path.abspath(root))
    for file_name in files:
        process_file(file_name)

    os.chdir(current_path)


def main():
    current_path = pwd()

    for root, dirs, files in os.walk(os.pardir):
        process_folder(root, files)

    os.chdir(current_path)


if __name__ == '__main__':
    main()
