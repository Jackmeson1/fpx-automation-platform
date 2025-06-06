'''Default Test result object of PySystem
'''
from unittest import TextTestResult, TextTestRunner

from SystemTestCase import SysTestCase


''' Status of a Testcase '''
class TestStatus:
    NOTRUN, SUCCESS, FAILURE, ERROR, SKIP, WARNING = ('NOTRUN', 'SUCCESS', 'FAILURE', 'ERROR', 'SKIP', 'WARNING')


class TcOutcome(object):
    def __init__(self):
        self.output: str = None
        self.exception_info: str = None


class SysTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.tc_status = TestStatus.NOTRUN   # status of current TC
        self.tc_output: str = ''
        self.successes = []
        self.warnings = []
        # self.shouldStop = False

    def addSuccess(self, test: SysTestCase):
        super().addSuccess(test)
        self.tc_status = TestStatus.SUCCESS
        self.successes.append(test)

    def addError(self, test, err):
        super().addError(test, err)
        self.tc_status = TestStatus.ERROR

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.tc_status = TestStatus.FAILURE

    def addSkip(self, test, reason):
        super().addFailure(test, reason)
        self.tc_status = TestStatus.SKIP

    def addWarning(self, test, warning):
        self.warnings.append((test, warning))
        self.tc_status = TestStatus.WARNING


class SysTestRunner(TextTestRunner):
    def __init__(self, stream=None, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=SysTestResult, warnings=None,
                 *, tb_locals=False):
        super().__init__(stream=stream, descriptions=descriptions, verbosity=verbosity, failfast=failfast,
                         buffer=buffer, resultclass=resultclass, warnings=warnings, tb_locals=tb_locals)

