import itertools
import unittest

import fortran_to_python_re as f2pr


class TestFortranToPythonRe(unittest.TestCase):
    def test_replace_fortran_comments_to_python(self):
        # test case from https://docs.oracle.com/cd/E19957-01/805-4939/z40007332024/index.html
        fortran_example = '''c      Start expression analyzer
       CHARACTER S, STACK*80
       COMMON /PRMS/ N, S, STACK
       ...
*      Crack the expression:
       IF ( S .GE. '0' .AND. S .LE. '9' ) THEN ! EoL comment
              CALL PUSH        ! Save on stack. EoL comment
d             PRINT *, S       ! Debug comment & EoL comment
       ELSE
              CALL TOLOWER ! To lowercase EoL comment
       END IF
D      PRINT *, N!       Debug comment & EoL comment
       ...
C      Finished
!       expression analyzer
'''

        comments_replaced_txt = f2pr.replace_fortran_comments_to_python(fortran_example)

        expected_replaced_txt = '''#      Start expression analyzer
       CHARACTER S, STACK*80
       COMMON /PRMS/ N, S, STACK
       ...
#      Crack the expression:
       IF ( S .GE. '0' .AND. S .LE. '9' ) THEN ! EoL comment
              CALL PUSH        ! Save on stack. EoL comment
#             PRINT *, S       ! Debug comment & EoL comment
       ELSE
              CALL TOLOWER ! To lowercase EoL comment
       END IF
#      PRINT *, N!       Debug comment & EoL comment
       ...
#      Finished
#       expression analyzer'''

        self.assertLongStringEqual(comments_replaced_txt, expected_replaced_txt)

    def assertLongStringEqual(self, expected, result):
        expected_list = result.splitlines()
        replaced_list = expected.splitlines()
        return map(self.assertLongStringEqualHelper, itertools.izip(expected_list, replaced_list))

    def assertLongStringEqualHelper(self, item):
        exp, res = item
        return self.assertEqual(exp, res)

    def test_replace_fortran_dollar6_to_python(self):
        fortran_example = '''      SUBROUTINE SB02MT( JOBG, JOBL, FACT, UPLO, N, M, A, LDA, B, LDB,
     $                   Q, LDQ, R, LDR, L, LDL, IPIV, OUFACT, G, LDG,
     $                   IWORK, DWORK, LDWORK, INFO )
#
#     SLICOT RELEASE 5.0.
'''

        comments_replaced_txt = f2pr.replace_fortran_dollar6_to_python(fortran_example)

        expected_replaced_txt = '''      SUBROUTINE SB02MT( JOBG, JOBL, FACT, UPLO, N, M, A, LDA, B, LDB, Q, LDQ, R, LDR, L, LDL, IPIV, OUFACT, G, LDG, IWORK, DWORK, LDWORK, INFO )
#
#     SLICOT RELEASE 5.0.
'''
        self.assertEqual(
            len(expected_replaced_txt.splitlines()),
            len(comments_replaced_txt.splitlines()),
        )

        self.assertEqual(expected_replaced_txt, comments_replaced_txt)
