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
#       expression analyzer
'''

        self.maxDiff = None
        self.assertEqual(comments_replaced_txt, expected_replaced_txt)

    def test_replace_fortran_continue_to_next_line_to_python(self):
        fortran_example = '''      SUBROUTINE SB02MT( JOBG, JOBL, FACT, UPLO, N, M, A, LDA, B, LDB,
     $                   Q, LDQ, R, LDR, L, LDL, IPIV, OUFACT, G, LDG,
     $                   IWORK, DWORK, LDWORK, INFO )
#
#     SLICOT RELEASE 5.0.
'''

        comments_replaced_txt = f2pr.replace_fortran_continue_to_next_line_to_python(fortran_example)

        expected_replaced_txt = '''      SUBROUTINE SB02MT( JOBG, JOBL, FACT, UPLO, N, M, A, LDA, B, LDB, Q, LDQ, R, LDR, L, LDL, IPIV, OUFACT, G, LDG, IWORK, DWORK, LDWORK, INFO )
#
#     SLICOT RELEASE 5.0.
'''
        self.assertEqual(
            len(expected_replaced_txt.splitlines()),
            len(comments_replaced_txt.splitlines()),
        )

        self.assertEqual(expected_replaced_txt, comments_replaced_txt)


class TestFortranToPythonReDeclarationLines(unittest.TestCase):
    def setUp(self):
        self.fortran_example = '''#
#     .. Parameters ..
      DOUBLE PRECISION  ZERO, ONE
      PARAMETER         ( ZERO = 0.0D0, ONE = 1.0D0 )
#     .. Scalar Arguments ..
      CHARACTER         FACT, JOBG, JOBL, UPLO
      INTEGER           INFO, LDA, LDB, LDG, LDL, LDQ, LDR, LDWORK, M, N, OUFACT
#     .. Array Arguments ..
      INTEGER           IPIV(*), IWORK(*)
      DOUBLE PRECISION  A(LDA,*), B(LDB,*), DWORK(*), G(LDG,*), L(LDL,*), Q(LDQ,*), R(LDR,*)
#     .. Local Scalars ..
      LOGICAL           LFACTA, LFACTC, LFACTU, LJOBG, LJOBL, LUPLOU
      CHARACTER         TRANS
      INTEGER           I, J, WRKOPT
      DOUBLE PRECISION  EPS, RCOND, RNORM
#     .. External Functions ..
      LOGICAL           LSAME
      DOUBLE PRECISION  DLAMCH, DLANSY
      EXTERNAL          DLAMCH, DLANSY, LSAME
#     .. External Subroutines ..
      EXTERNAL          DCOPY, DGEMM, DGEMV, DPOCON, DPOTRF, DSYCON, DSYRK, DSYTRF, DSYTRS, DTRSM, XERBLA
#     .. Intrinsic Functions ..
      INTRINSIC         INT, MAX
#     .. Executable Statements ..
#
      INFO   = 0
      LJOBG  = LSAME( JOBG, 'G' )
      LJOBL  = LSAME( JOBL, 'N' )
      LFACTC = LSAME( FACT, 'C' )
      LFACTU = LSAME( FACT, 'U' )
      LUPLOU = LSAME( UPLO, 'U' )
      LFACTA = LFACTC.OR.LFACTU
#
#     Test the input scalar arguments.
#
      IF( .NOT.LJOBG .AND. .NOT.LSAME( JOBG, 'N' ) ) THEN
         INFO = -1
      ELSE IF( .NOT.LJOBL .AND. .NOT.LSAME( JOBL, 'Z' ) ) THEN
         INFO = -2
      ELSE IF( .NOT.LFACTA .AND. .NOT.LSAME( FACT, 'N' ) ) THEN
         INFO = -3
      ELSE IF( .NOT.LUPLOU .AND. .NOT.LSAME( UPLO, 'L' ) ) THEN
         INFO = -4
      ELSE IF( N.LT.0 ) THEN
         INFO = -5
      ELSE IF( M.LT.0 ) THEN
         INFO = -6
'''

    def test_find_type_variable_names_character(self):
        variable_info_list = f2pr.find_type_variable_names(self.fortran_example, 'CHARACTER')

        expected_tuple = ({'name': 'FACT', 'type': 'CHARACTER'},
                          {'name': 'JOBG', 'type': 'CHARACTER'},
                          {'name': 'JOBL', 'type': 'CHARACTER'},
                          {'name': 'UPLO', 'type': 'CHARACTER'},
                          {'name': 'TRANS', 'type': 'CHARACTER'})

        self.assertSequenceEqual(expected_tuple, variable_info_list)

    def te_st_find_type_variable_names_double_precision(self):
        variable_names_found = set(f2pr.find_type_variable_names(self.fortran_example, 'DOUBLE PRECISION'))

        expected_set = set(('ZERO', 'ONE',
                            'A', 'B', 'DWORK', 'G', 'L', 'Q', 'R',
                            'EPS', 'RCOND', 'RNORM',
                            'DLAMCH', 'DLANSY',
                            ))

        self.assertSetEqual(expected_set, variable_names_found)

    def test_FortranVariableDeclarationParserChar(self):
        parser = f2pr.FortranVariableDeclarationParser('FACT, JOBG, JOBL, UPLO', 'CHARACTER')

        parsed_variable_info_list = parser.parse()

        expected_variable_info_list = [{'name': "FACT", 'type': "CHARACTER"},
                                       {'name': "JOBG", 'type': "CHARACTER"},
                                       {'name': "JOBL", 'type': "CHARACTER"},
                                       {'name': "UPLO", 'type': "CHARACTER"}, ]

        self.assertSequenceEqual(expected_variable_info_list, parsed_variable_info_list)

    def test_FortranVariableDeclarationParserDouble(self):
        parser = f2pr.FortranVariableDeclarationParser(
            'A(LDA,*), B(LDB,*), DWORK(*), G(LDG,*), L(LDL,*), Q(LDQ,*), R(LDR,*)',
            'DOUBLE PRECISION')

        parsed_variable_info_list = parser.parse()

        expected_variable_info_list = [{'name': "A", 'type': "DOUBLE PRECISION", "dim": '(LDA,*)'},
                                       {'name': "B", 'type': "DOUBLE PRECISION", "dim": '(LDB,*)'},
                                       {'name': "DWORK", 'type': "DOUBLE PRECISION", "dim": '(*)'},
                                       {'name': "G", 'type': "DOUBLE PRECISION", "dim": '(LDG,*)'},
                                       {'name': "L", 'type': "DOUBLE PRECISION", "dim": '(LDL,*)'},
                                       {'name': "Q", 'type': "DOUBLE PRECISION", "dim": '(LDQ,*)'},
                                       {'name': "R", 'type': "DOUBLE PRECISION", "dim": '(LDR,*)'}, ]

        maxDiff_backup = self.maxDiff
        self.maxDiff = 1024
        self.assertSequenceEqual(expected_variable_info_list, parsed_variable_info_list)
        self.maxDiff = maxDiff_backup
