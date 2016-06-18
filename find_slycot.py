import os
import re
from pprint import pprint


def pwd():
    return os.path.abspath(os.curdir)


def get_first_script_parameter():
    from sys import argv
    result = os.curdir
    if 1 < len(argv):
        result = argv[1]
    return os.path.abspath(result)


def print_sorted_keys(function_names):
    keys = list(function_names.keys())
    keys.sort()
    for i, key in enumerate(keys):
        print(i, key)
        pprint(function_names[key])


class RecursiveFinder(object):
    def __init__(self, initial_path=os.curdir, extension='.py', pattern="from" + " slycot import"):
        self.abs_return_path = os.path.abspath(os.curdir)
        abs_initial_path = os.path.abspath(initial_path)
        self.extension = extension
        self.pattern = pattern

        self.result = {}

        if not os.path.exists(abs_initial_path):
            raise IOError('File does not exist: %s' % abs_initial_path)
        elif not os.path.isdir(abs_initial_path):
            raise IOError('Not a directory: %s' % abs_initial_path)
        else:
            self.abs_initial_path = abs_initial_path
            os.chdir(self.abs_initial_path)
            self.walker()

    def __del__(self):
        """destructor"""
        os.chdir(self.abs_return_path)

    def walker(self):
        for root, dirs, files in os.walk(self.abs_initial_path):
            # TODO : list of folders to ignore
            if '.git' not in root and '.idea' not in root and not root.startswith('..\\build'):
                folder_list = self.process_folder(root, files)
                if folder_list:
                    self.result[root] = folder_list

    def process_folder(self, root, files):
        current_path = pwd()
        os.chdir(os.path.abspath(root))

        folder_result = {}

        for file_name in files:
            file_result = self.process_file(root, file_name)
            if file_result:
                folder_result[file_name] = file_result

        os.chdir(current_path)

        return folder_result

    def process_file(self, path, file_name):
        result = []

        if os.path.splitext(file_name)[-1] == self.extension:
            f = open(file_name, 'r')
            txt = f.read()
            f.close()

            lines = txt.splitlines()

            for k, line in enumerate(lines):

                if self.pattern in line:
                    # print file_name, k, ':', line
                    result.append((k, line))

        return result


class RecursiveFinderFortran(RecursiveFinder):
    def __init__(self, initial_path=get_first_script_parameter(), extension='.f', pattern="CALL", function_list=False):
        self.function_list = function_list
        RecursiveFinder.__init__(self, initial_path=initial_path, extension=extension, pattern=pattern)

    def process_file(self, path, file_name):
        """
        Process the file if in the list
        Parameters
        ----------
        path
        file_name

        Returns
        -------

        """
        result = []

        function_name = os.path.splitext(file_name)[0].lower()

        if function_name in self.function_list:
            result = RecursiveFinder.process_file(self, path=path, file_name=file_name)

        return result


class FindFunctionNamesFromImport(object):
    def __init__(self, finder_result_dict):
        self.finder_result_dict = finder_result_dict
        self.function_names = {}

    def find_function_names(self):
        for path, files in self.finder_result_dict.items():
            for filename, lines in files.items():
                for line_number, line in lines:
                    self.handle_line_if_not_comment(line, path, filename, line_number)

        return self.function_names

    @staticmethod
    def is_comment(line):
        """
        python version
        Parameters
        ----------
        line

        Returns
        -------

        """
        return '#' == line.strip()[0]

    def handle_line_if_not_comment(self, line, path, filename, line_number):
        if not self.is_comment(line):
            self.handle_file(filename, line, line_number, path)

    def handle_file(self, filename, line, line_number, path):
        """
        find function names from import line
        Parameters
        ----------
        filename
        line
        line_number
        path

        Returns
        -------

        """
        line_strip = line.strip()
        line_strip_split = line_strip.split()
        if 4 == len(line_strip_split):
            self.handle_one_function_import(line_strip_split, path, filename, line_number)
        elif 5 == len(line_strip_split):
            self.handle_two_functions_import(line_strip_split, path, filename, line_number)

    def handle_two_functions_import(self, line_strip_split, path, filename, line_number):
        function_name_list = self.find_function_names_from_import(line_strip_split)
        for key in function_name_list:
            self.add_function_name(key, path, filename, line_number)

    @staticmethod
    def find_function_names_from_import(line_strip_split):
        function_name_list = [line_strip_split[3][:-1], line_strip_split[4]]
        return function_name_list

    def handle_one_function_import(self, line_strip_split, path, filename, line_number):
        function_name = self.find_function_name_from_import(line_strip_split)
        self.add_function_name(function_name, path, filename, line_number)

    @staticmethod
    def find_function_name_from_import(line_strip_split):
        key = line_strip_split[-1]
        return key

    def add_function_name(self, key, path, filename, line_number):
        if key in self.function_names:
            self.function_names[key].append((path, filename, line_number))
        else:
            self.function_names[key] = [(path, filename, line_number)]


class FindFunctionUsedFortran(FindFunctionNamesFromImport):
    @staticmethod
    def is_comment(line):
        return 'C' == line[1 - 1]


def main():
    python_finder = RecursiveFinder(os.pardir)

    python_function_finder = FindFunctionNamesFromImport(python_finder.result)
    function_names = python_function_finder.find_function_names()

    print_sorted_keys(function_names)

    fortran_finder = RecursiveFinderFortran(function_list=tuple(function_names.keys()))

    pprint(fortran_finder.result, width=240)
    # fortran_function_finder = FindFunctionUsedFortran(fortran_finder.result)
    # fortran_function_names = fortran_function_finder.find_slicot_function_names_from_import()

    # print_sorted_keys(fortran_function_names)

if __name__ == '__main__':
    main()
