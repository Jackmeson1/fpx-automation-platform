import unittest

from SystemTestCase import sys_suite
from SystemTestCase.tc_mapping import TcFuncMapping
from executor.sysrunner import TestStatus, SysTestResult
from monitor import get_logger

logger = get_logger(__name__)

import os
import keyboard
from enum import Enum
from pexpect import ExceptionPexpect


class TcFailAction(Enum):
    CONTINUE = 'continue'
    NEXT = 'next'
    STOP = 'stop'

    def __str__(self):
        return self.value


class SysTcFail(ExceptionPexpect):
    def __init__(self, err_text, action=None):
        super().__init__(err_text)
        self.action: str = action


class TestCaseInfo:
    def __init__(self, is_debug=False, tc_id=-1, tc_desc='', full_filename='', fixture_path_list=[],
                 skip=False, expect_fail=False, log_dir='logs'):
        self.is_debug = is_debug
        self.full_filename = full_filename
        self.filename = full_filename.split('/')[-1]
        # self.tc_file = tc_file
        self.skip: bool = skip
        self.expect_fail: bool = expect_fail
        self.tcid: int = tc_id
        self.desc = tc_desc
        self.fixture_path_list: list = fixture_path_list
        self.log_dir = log_dir


class SysTestCase(unittest.TestCase, TcFuncMapping):
    def __init__(self, test_method, tc_info: TestCaseInfo = None, testsuite=None):
        super().__init__(test_method)
        TcFuncMapping.__init__(self)
        # self.tc_func = self._init_tc_func()
        self.tc_info = tc_info
        self.testsuite: sys_suite.SysTestSuite = testsuite
        # self.action = testsuite.failed_action if testsuite else TcFailAction.NEXT.value
        self.action = testsuite.failed_action
        self.tcid_list = [tc_info.tcid]
        self.status = TestStatus.NOTRUN
        self.shouldStop = False
        self.fail_list: list = []   # store list of fail steps that is unhandled (when action == CONTINUE)
        self.labels = {}
        self.log_fname = None
        self.logfile = None

    def tearDown(self):
        if self.testsuite is not None and self.testsuite.pause_fail and self._detect_fail():
            print('PAUSE: pause on failed of TC {}; press "c" to continue.'.format(self.tc_info.tcid))
            keyboard.wait('c')
        super().tearDown()

    def _detect_fail(self):
        for e in self._outcome.errors:
            if e[1] is not None:
                return True
        return False

    def _init_tc_func(self):
        super()._init_tc_func()
        self.tc_func.update({
            # TcDirective.SET_PARAMS: self.set_params
        })

    def run(self, result=None):
        """run Single TC or check failed tc list and update the tc status in testsuite when TC is within a suite"""
        # if self.testsuite is None:
        #     result = super().run(result)
        # elif self.tc_info.tcid not in self.testsuite.failed_tcid_list:
        #     result = super().run(result)
        #     self.testsuite.update_status(self.tcid_list, result)
        try:
            result: SysTestResult = super().run(result)
        except SysTcFail:
            result.shouldStop = self.shouldStop
        self.status = result.tc_status
        # self.shouldStop = result.shouldStop
        self.pass_count = len(result.successes)
        self.warning_count = len(result.warnings)
        self.fail_count = len(result.failures) + len(result.errors)
        self.error_stack = ''
        for err in result.errors:
            stack = err[1] if isinstance(err, tuple) else str(err)
            logger.error(stack)
            self.error_stack += stack.splitlines()[-1] + '\n'
        if self.testsuite and any([tcid not in self.testsuite.failed_tcid_list for tcid in self.tcid_list]):
            self.testsuite.update_status(self.tcid_list, self.status)
        return result

    def defaultTestResult(self):
        pass

    def debug(self):
        if self.pause:
            # TODO: implement F5, F6, F7, F8 for debugging steps
            pass
        super().debug()

    @staticmethod
    def get_init_file(path: str, file_name: str = 'init.prov'):
        if path[-1] != '/':
            path += '/'
        init_prov = path + file_name
        if not os.path.exists(init_prov):
            init_prov = None
        return init_prov

    @staticmethod
    def get_fixture_file(path: str, file_name: str = 'fixture.prov'):
        if path[-1] != '/':
            path += '/'
        fixture_file = path + file_name
        if not os.path.exists(fixture_file):
            fixture_file = None
        return fixture_file
