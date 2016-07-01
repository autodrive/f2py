import os
import unittest

import fortran_to_python_easy as f2pe


class TestFortranToPythonEasy(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(os.pardir, 'pyslicot', 'SB02MT.f')

    def test_fortran_filename_to_python_filename(self):
        fortran_filename = 'SB02MT.f'
        result = f2pe.fortran_filename_to_python_filename(fortran_filename)
        expected = 'sb02mt.py'
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
