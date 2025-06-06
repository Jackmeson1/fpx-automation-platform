from unittest import TestResult
from src.ftnt_lundary_tc import DemoTc
import unittest
from monitor import init_logger
from HtmlTestRunner import HTMLTestRunner
import time


class SysTestSuite(unittest.TestSuite):
    def __init__(self, tests=(), max_tries: int = 99):
        self.init__ = super().__init__(tests)
        self.max_tries = max_tries
        self.test_done: bool = False
        self.rm_set_none = False

    def run(self, result: TestResult) -> TestResult:
        for i in range(self.max_tries):
            result = super().run(result)
            if self.test_done:
                break
            else:
                time.sleep(5)
        return result

    def _removeTestAtIndex(self, index):
        """Stop holding a reference to the TestCase at index."""
        try:
            test = self._tests[index]
        except TypeError:
            # support for suite implementations that have overridden self._tests
            pass
        else:
            # Some unittest tests add non TestCase/TestSuite objects to
            # the suite.
            if hasattr(test, 'countTestCases'):
                self._removed_tests += test.countTestCases()
            if self.rm_set_none:
                self._tests[index] = None
            else:
                self._tests.pop(index)

def main():
    init_logger()
    tc1 = DemoTc('test_exec_tc', {'tc_name': 'TC1'})
    tc2 = DemoTc('test_exec_tc', {'tc_name': 'TC2'})
    print('---------- Run TCs -------------')
    tc_result = unittest.TestResult(verbosity=9)
    runner = HTMLTestRunner(output='/tmp/logs', verbosity=2)
    runner.run(tc1)
    # runner.run(tc2)
    # tc1(tc_result)
    # tc1.run(tc_result)
    # tc2.run()

    # suite = unittest.TestSuite()
    suite = SysTestSuite()
    suite.addTest(tc1)
    suite.addTest(tc2)
    print('---------- Run TestSuite -------------')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    #
    # print('--------single TC suite--------')
    # suite = unittest.TestSuite()
    # suite.addTest(tc1)
    # runner.run(suite)

if __name__ == '__main__':
    main()