""" Object for TestCase key work to functions in System Testcase of System Objects """
import time
import re


class TcFuncMapping:
    P_COMMA = re.compile(r'(?<!\\),')

    def __init__(self):
        self.cmd_params: dict = dict()
        self._init_tc_func()

    def _init_tc_func(self) -> dict:
        self.tc_func = {'SLEEP': self.sleep}

    def set_params(self, params: dict):
        self.cmd_params = params

    def sleep(self, t: str):
        if t.isdecimal():
            time.sleep(int(t))
        else:
            raise TypeError('{} is not int for SLEEP command'.format(t))

