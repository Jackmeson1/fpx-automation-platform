import datetime
import os
import keyboard
import re

from lxml import etree

from SystemTestCase import sys_suite
from SystemTestCase.SysTestCase import SysTestCase, SysTcFail
from SystemTestCase.SysTestCase import TestCaseInfo
from SystemTestCase.SysTestCase import TcFailAction
from SystemObject.sys_obj import SysObj
from SystemObject.cli_node import CliNode
from SystemObject.gui_node import GuiNode
from SystemTestCase.tc_parser import TcFileParser, NameSpace
from SystemTestCase.tc_parser import FixtureFileParse
from SystemTestCase.tc_parser import TcDirective
from config.environment import ENV
from monitor.pysys_log import pysys_logger


def setUpModule():
    assert hasattr(ENV, 'CTRL_PC')
    # ENV.node_list = []
    for name, node in ENV.__dict__.items():
        if isinstance(node, CliNode):
            node: CliNode = node
            node.node_name = name
            ENV.node_list.append(node)
            node.login()

def tearDownModule():
    for i, node in enumerate(ENV.node_list):
        if isinstance(node, CliNode):
            node.logout()
            ENV.node_list.pop(i)


class ScriptTestCaseBase(SysTestCase):
    # nodes: list = []
    def __init__(self, test_method, tc_info: TestCaseInfo = None, test_suite=None):
        super().__init__(test_method, tc_info, test_suite)
        self.init_scr = None
        self.setup_scr = None
        self.teardown_scr = None
        self.test_scr = None
        self.curr_node: SysObj = None
        self.log_fname = self.get_logfile_name()
        self.logfile = None
        self.keepConfig = False

    # @classmethod
    # def setUpClass(cls) -> None:
    #     super().setUpClass()
    #     assert hasattr(ENV, 'CTRL_PC')
    #     ENV.node_list = []
    #     for name, node in ENV.__dict__.items():
    #         if isinstance(node, CliNode):
    #             node.node_name = name
    #             ENV.node_list.append(node)
    #             node.login()
    #         elif isinstance(node, GuiNode):
    #             node.node_name = name
    #             ENV.node_list.append(node)
    #             node.gui_login()
    #
    # @classmethod
    # def tearDownClass(cls) -> None:
    #     super().tearDownClass()
    #     for node in ENV.node_list:
    #         if isinstance(node, CliNode):
    #             node.logout()
    #         elif isinstance(node, GuiNode):
    #             node.gui_logout()

    def setUp(self):
        self.linenum = 0
        self.logfile = self.get_logfile('a')
        self.logfile.write('----------- TC starts @: {}-----------\n'.format(datetime.datetime.now()))
        self.logfile.write('<Test Objective>: {}\n\n'.format(self.tc_info.desc))
        self.logfile.close()
        self.logfile = self.get_logfile()  # open in binary mode for cli nodes logging
        for node in ENV.node_list:
            if hasattr(node, 'output'):
                node.output = ''
            if hasattr(node, 'logfile'):  # pexpect logfile
                node.logfile = self.logfile
            else:  # non-pexpect nodes
                pysys_logger.error('non-pexpect is not yet supported.')
        super().setUp()
        self.parse_script()
        # TODO enable log herf link on html report once tc starts
        curr_tc = self.testsuite.report.testcases[self.testsuite.report.curr_tc_index]
        curr_tc.attrib['href'] = self.log_fname
        self.testsuite.report.file.seek(0)
        self.testsuite.report.file.truncate()
        self.testsuite.report.file.write(etree.tostring(self.testsuite.report.document))
        self.testsuite.report.file.flush()
        self.testsuite.report.tc_update_file.seek(0)
        self.testsuite.report.tc_update_file.truncate()
        # self.testsuite.report.tc_update_file.write(self.report.testcases[self.report.curr_tc_index].get('title'))
        self.testsuite.report.tc_update_file.write(curr_tc.get('title') + ':' + curr_tc.get('status'))
        self.testsuite.report.tc_update_file.flush()
        self.exec_init_scr()

    def tearDown(self):
        super().tearDown()

    def get_logfile(self, mode='ab'):
        if self.logfile and not self.logfile.closed:   # if logfile has been created. self.logfile is set None when teardown
            return self.logfile
        else:
            if not os.path.exists(self.tc_info.log_dir):
                os.mkdir(self.tc_info.log_dir)
            return open(self._get_logfile_full_name(), mode)

    # log file is opened in 'ab' mode. covert string to bytes when it is necessary.
    def write_log(self, s):
        s = '\n' + s
        # s = '\n {} @ line {}'.format(s, self.linenum)
        if type(s) is str:
            o = bytes(s, 'utf-8')
        elif type(s) is not bytes:
            pysys_logger.error('log content must be in string or bytes format')
        else:
            o = s
        self.logfile.write(o)
        self.logfile.flush()

    def _get_logfile_full_name(self) -> str:
        filename = self.get_logfile_name()
        if self.testsuite:  # The TC is invoked by a testsuite
            filename = self.testsuite.log_dir + '/' + filename
        return filename

    # define an interface in this base class, must be implemented in the subclasses
    def get_logfile_name(self) -> str:
        pysys_logger.error(
            'This is an interface of "get_logfile_name" defined in the base class, must be implemented in subclasses.')
        exit(-1)

    def parse_script(self):
        msg = 'This is an interface of "prep_logfile" defined in the base class, must be implemented in subclasses.'
        pysys_logger.error(msg)
        raise SysTcFail(msg)

    def exec_init_scr(self):
        if self.logfile:
            self.write_log('---- TC Init Section: ----')
        self.exec_scr(self.init_scr)

    def exec_setup_scr(self):
        if self.logfile:
            self.write_log('---- TC Setup Section: ----')
        self.exec_scr(self.setup_scr)

    def exec_test_scr(self):
        if self.logfile:
            self.write_log('---- TC Test Secript Section: ----')
        self.exec_scr(self.test_scr)

    def exec_teardown_scr(self):
        if self.logfile:
            self.write_log('---- TC Teardown Section: -----')
        if self.keepConfig:
            if self.logfile:
                self.write_log('--- keep the current config of the failed case ----')
        else:
            self.exec_scr(self.teardown_scr)

    def exec_scr(self, script: list = None):
        # steps in a script file has been parsed as series of (command, paramater) tuples.
        if self.logfile:
            self.write_log('----------- {} ---------------\n'.format(datetime.datetime.now()))
        if script is None:
            pysys_logger.error('script is empty in {}'.format(self.tc_info.full_filename))
        for step in script:
            try:
                linenum = step[0]
                self.exec_step(step[1])
            except SysTcFail as e:
                action = e.action or self.action
                self.write_log('<ERROR> @line {}:  {}'.format(linenum, e.value))
                if action == TcFailAction.STOP:
                    pysys_logger.error('Test Script stops - ' + e.value)
                    # self.shouldStop = True
                    self.keepConfig = True
                    raise
                elif action == TcFailAction.CONTINUE:
                    pysys_logger.warning('Continue after step failed - ' + e.value)
                    self.fail_list.append(e.value)
                else:  # default action: raise exception and SysTestCase framework will jump to next TC.
                    raise
            # finally:
            #     self.action = self.testsuite.failed_action if self.testsuite else TcFailAction.NEXT
        if self.fail_list:
            raise SysTcFail(str(self.fail_list))

    def fetch_label(self, m) -> str:
        orig_val = m.group()
        try:
            if m.group(3):  # [Node:Label] r'\[\s*(\w+)\s*(:\s*(\w+))?\s*\]
                key = m.group(3)
                node_name = m.group(1)
                if node_name == NameSpace.LOCAL:
                    node = self
                elif node_name == NameSpace.GLOBAL:
                    node = ENV
                else:
                    node = getattr(ENV, node_name)
                label = node.labels.get(key) or getattr(node, key)
            else:
                '''[Label]: 
                1st - TC local labels
                2nd - labels in current node
                3rd - variables in current node
                4th - Global Labels'''
                # node = self.curr_node or self
                # return self.labels.get(key) or \
                #        node.labels.get(key) or \
                #        getattr(node, key, None) or \
                #        ENV.labels.get(key)
                key = m.group(1)
                label = self.labels.get(key)
                if label is None and self.curr_node:
                    label = self.curr_node.labels.get(key) or getattr(self.curr_node, key, None)
                if label is None:
                    label = ENV.labels.get(key)
            if label is None:
                raise KeyError
            return label
        except (AttributeError, NameError, KeyError):
            self.write_log('<WARNING>: Label: "{}" is not valid.\n'.format(m.group()))
            return orig_val
            # raise

    def fetch_colon_label(self, m: re.Pattern) -> str:
        orig_val = m.group()
        try:  # Node:Label r'(\w+):(\w+)'
            key = m.group(2)
            node_name = m.group(1)
            if node_name == NameSpace.LOCAL:
                node = self
            elif node_name == NameSpace.GLOBAL:
                node = ENV
            else:
                node = getattr(ENV, node_name)
            if node is None:
                raise NameError
            label = node.labels.get(key) or getattr(node, key)
            if label:
                return label
            else:
                raise KeyError
        except (AttributeError, NameError, KeyError):
            self.write_log('<WARNING>: Label: "{}" is not valid.\n'.format(m.group()))
        return orig_val

    def fetch_variable(self, m: re.Pattern) -> str:
        orig_val = m.group()
        try:  # Node:Label r'\(\$(\w+)\)'
            key = m.group(1)
            label = self.labels.get(key)
            if label is None and self.curr_node:
                label = self.curr_node.labels.get(key) or getattr(self.curr_node, key, None)
            if label is None:
                label = ENV.labels.get(key)
            if label:
                return label
            else:
                raise KeyError
        except (AttributeError, NameError, KeyError):
            self.write_log('<WARNING>: Label: "{}" is not valid.\n'.format(m.group()))
        return orig_val

    def label_sub(self, s: str):
        if not s:
            return s
        s = s.strip()
        if not s:
            return s
        val_parts = s.rsplit(maxsplit=1)
        multi_parts = len(val_parts) == 2
        last_val = val_parts[-1].strip() if multi_parts else s.strip()
        m = TcFileParser.P_LITERAL.match(last_val)  # parameters string in "" uses the orignal sting literally
        if m:
            last_val = m.group(1)
            return val_parts[0] + ' ' + last_val if multi_parts else last_val
        else:
            val = TcFileParser.P_LABEL.sub(self.fetch_label, s)
            val = TcFileParser.P_COLON_LABEL.sub(self.fetch_colon_label, val)
            return TcFileParser.P_VARIABLE.sub(self.fetch_variable, val)

    def exec_step(self, step: tuple) -> bool:
        cmd, param = step
        if cmd == TcDirective.SET_PARAMS:
            self.assertIsInstance(param, dict)
            for k, v in param.items():
                if type(v) is str:
                    # value = TcFileParser.P_LABEL.sub(self.fetch_label, v)
                    value = self.label_sub(v)
                elif type(v) is list:
                    # value = [TcFileParser.P_LABEL.sub(self.fetch_label, x) for x in v]
                    value = [self.label_sub(x) for x in v]
                else:
                    pysys_logger.error('Parameter {} is not string or list'.format(k))
                    raise TypeError('Parameter {} is not string or list'.format(k))
                param[k] = value
            if self.curr_node:
                self.curr_node.cmd_params = param
            else:
                self.cmd_params = param
        elif cmd == TcDirective.SET_LABEL:
            key = param[0]
            right_val = param[1]
            labels = self.curr_node.labels if self.curr_node else self.labels
            if type(right_val) is list:
                for i in range(len(right_val)):
                    # right_val[i] = TcFileParser.P_LABEL.sub(self.fetch_label, right_val[i])
                    right_val[i] = self.label_sub(right_val[i])
            elif type(right_val) is str:
                # right_val = TcFileParser.P_LABEL.sub(self.fetch_label, right_val)
                right_val = self.label_sub(right_val)
            else:
                pysys_logger.error('label value must be str or list. label value in step: {}'.format(right_val))
                raise
            labels[key] = right_val
        # elif cmd == TcDirective.SET_LIST:
            # pass
        elif cmd == TcDirective.EXEC:  # '[!]': call a pre-defined python function
            self.write_log('Execute python code:\n{}'.format(param))
            exec(param)
        elif not cmd:  # cmd == '' or cmd is None:
            return True
        elif cmd == TcDirective.SET_NODE:
            if isinstance(param, SysObj):
                node_name = param.node_name
            elif param == ENV:
                node_name = NameSpace.GLOBAL
            elif param is None:
                node_name = NameSpace.LOCAL
            else:
                err_msg = 'Node {} is not valid'.format(param)
                self.write_log('<ERROR>: ' + err_msg)
                raise TypeError(err_msg)
            self.curr_node = param
            self.write_log('<Node: {}>\n'.format(node_name))
            return True
        elif cmd == TcDirective.BREAKPOINT:
            if self.tc_info.is_debug:
                print('DEBUG: breakpoint in TC: {}, press "c" to continue.\n'.format(self.tc_info.full_filename))
                # keyboard.wait('c')
        else:
            # find function by keyword from current node or from Testcase class
            # func_list: dict = getattr((self.curr_node or self), 'tc_func', None)
            # cmd_func = func_list.get(cmd) if func_list else None
            func_list: dict = getattr((self.curr_node or self), 'tc_func', None)
            cmd_func = func_list.get(cmd) if func_list else None
            if param:
                # param = TcFileParser.P_LABEL.sub(self.fetch_label, param)
                param = self.label_sub(param)
            if cmd_func:
                if param:
                    cmd_func(param)
                else:
                    cmd_func()
            # elif isinstance(self.curr_node, GuiNode):  # execute script line as a GuiNode se python function
            #     if param:
            #         cmd += '({})'.format(param)
            #     GuiNode(self.curr_node).run_func(cmd)
            else:  # execute script line as a CLI command
                # if param:
                #     cmd += ' ' + param
                self.assertIsInstance(self.curr_node, CliNode,
                                      'It must be a CLI node to execute cli command. command line: {}'.format(cmd))
                self.curr_node.exec_cmd(cmd, param)
        return True

    def exec_os_cmd(self, cmd):
        self.write_log(cmd + '\n')
        stream = os.popen(cmd)
        self.write_log(stream.read() + '\n')

    def _init_tc_func(self):
        super()._init_tc_func()
        self.tc_func.update({'LOG': self.tc_log,
                               'LOG_ORIG': self.tc_log_orig
                            })
    
    def tc_log(self, msg: str):
        self.label_sub(msg)
        self.tc_log_orig(msg)
    
    def tc_log_orig(self, msg: str):
        self.write_log(msg)


class ScriptTC(ScriptTestCaseBase):
    def setUp(self):
        super().setUp()
        self.exec_setup_scr()

    def tearDown(self) -> None:
        super().tearDown()
        self.exec_teardown_scr()
        self.logfile.close()
        self.logfile = None


    def test_scr_file(self):
        self.exec_test_scr()

    def parse_script(self):
        file_parser = TcFileParser(self.tc_info.full_filename, self.tc_info.tcid)
        try:
            self.init_scr, self.setup_scr, self.test_scr, self.teardown_scr, self.tcid_list = file_parser.parse_file()
        except SysTcFail as e:
            self.write_log('<ERROR>: ' + e.value)
            raise
        if self.tc_info.tcid > 0 and not str(self.tc_info.tcid) in self.tcid_list:
            self.tcid_list.append(str(self.tc_info.tcid))

    def get_logfile_name(self) -> str:
        return str(self.tc_info.tcid) + '.log'

    @classmethod
    def make_scr_tc(cls, tc_info: TestCaseInfo, tc_suite):
        return cls('test_scr_file', tc_info, tc_suite)


'''
    run init when setup or teardown a fixture (reuset ScriptTcBase method);
    only run setup script section when setting up a fixture
    run teardown section when teardown fixture (reuse ScriptTestCaseBase method)
    overwirte the tearDown() method, do nothing after running fixture setup or teardown
'''
class ScriptFixture(ScriptTestCaseBase):
    #overwrite the TC script behavior, do nothing when finish the setup or teardown of a fixture
    def __init__(self, test_method, tc_info: TestCaseInfo = None, test_suite=None, is_teardown=False):
        super().__init__(test_method, tc_info, test_suite)
        self.is_teardown = is_teardown

    def tearDown(self) -> None:
        super().tearDown()
        self.logfile.close()
        self.logfile = None

    def get_logfile_name(self) -> str:
        return str(self.tc_info.tcid) + '_fixture.log'

    def parse_script(self):
        file_parser = FixtureFileParse(self.tc_info.full_filename, self.tc_info.tcid)
        try:
            if self.is_teardown:
                self.init_scr, self.teardown_scr = file_parser.parse_teardown_fixture()
            else:
                self.init_scr, self.setup_scr = file_parser.parse_setup_fixture()
        except SysTcFail as e:
            self.write_log('<ERROR>: ' + e.value)
            raise
    def test_setup_fixture(self):
        self.exec_setup_scr()

    def test_teardown_fixture(self):
        self.exec_teardown_scr()

    @classmethod
    def make_setup_fixutre(cls, tc_info: TestCaseInfo, tc_suite):
        return cls('test_setup_fixture', tc_info, tc_suite, is_teardown=False)

    @classmethod
    def make_teardown_fixutre(cls, tc_info: TestCaseInfo, tc_suite):
        return cls('test_teardown_fixture', tc_info, tc_suite, is_teardown=True)
