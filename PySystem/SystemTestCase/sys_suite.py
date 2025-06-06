import unittest
from typing import List
from unittest import TestResult
from sysrunner.sysinit import pysys_root

from SystemTestCase.SysTestCase import SysTestCase, TestCaseInfo, TcFailAction
from SystemTestCase.script_testcase import ScriptTC, ScriptFixture
from SystemTestCase.tc_parser import TcFileParser
from monitor.pysys_log import pysys_logger
from SystemTestCase import helpers
import pandas
from pandas.core.frame import DataFrame
import numpy
import os
import shutil
from lxml import etree
import webbrowser

from executor.sysrunner import SysTestResult, TestStatus


class SceFileFormat:
    CSV = 'csv'
    XML = 'xml'
    JSON = 'json'


class CvsTcStatus:
    NOTRUN = ''
    PASSED = 'Passed'
    FAILED = 'Failed'
    WARNING = 'Warning'


class ScenarioStatus:
    INIT = 'INIT'
    PAUSED = 'PAUSED'
    RUNNING = 'RUNNING'
    DONE = 'DONE'


class CsvFields:
    PATH = 'Path'
    TCID = 'QAID'
    OBJECTIVE = 'Objective'
    PRIORITY = 'Priority'
    RESULT = 'Result'
    BUILD = 'Build'
    TESTER = 'Tester'
    AUTO = 'Autotested'
    PLATFORM = 'Platform'
    BIOS = 'BIOS'


class SysTestSuite(unittest.TestSuite):
    def __init__(self, scenario=None, tests=(), wait_time=60, fetch_interval=5,
                 is_debug=False, pause_fail=False, failed_action=None, skip_fixture=False,
                 # tc_base: str = '.',  log_base='logs', log_dir='logs/current',
                 # http_base_dir='/var/www/html', http_base_path='/pysystem', conf={},
                 tc_base='.', log_dir='logs/current', report_url='', conf={}):
        super().__init__(tests)
        self.is_debug = is_debug
        self.pause_fail = pause_fail
        self.skip_fixture = skip_fixture
        self.failed_tcid_list: list = []

        self.wait_time = wait_time
        self.interval = fetch_interval
        self.test_done: bool = False
        # self.timeout: bool = False
        self.rm_tc_set_none: bool = False
        self.tc_queue: list = []
        self.scenario = scenario
        self.sce_df: DataFrame = None
        self.sce_status = ScenarioStatus.INIT
        self.failed_action = failed_action or TcFailAction.NEXT.value
        self.init_fname: str = conf.get('init_fname')
        self.init_fallback: bool = conf.get('init_fallback')
        self.fixture_fname: str = conf.get('fixture_fname')
        self.fixture_fallback: bool = conf.get('fixture_fallback')

        self.conf: dict = conf
        # self.tc_root_dir: str = helpers.format_path(tc_base)
        self.tc_root_dir: str = tc_base
        # self.log_base: str = log_base
        # self.log_dir: str = helpers.gen_logdir(log_base)   # create log folder for current run
        self.log_dir = log_dir
        # self.curr_fixture_path: str = '/'
        self.curr_fixture_list: list = []
        self.curr_tcid: int = -1
        self.scenario_format = SceFileFormat.CSV
        self.report = ReportHtml(url=report_url, base_path=log_dir)
        # self.http_base_dir = http_base_dir
        # self.http_base_path = http_base_path
        # self._init_http_path()
        # self.report.url = 'http://localhost{}/logs/current/scenario.html'.format(http_base_path)

        self.col_tcid: pandas.core.frame.Series = None
        self.col_status: pandas.core.frame.Series = None
        self.col_path: pandas.core.frame.Series = None

    def _init_http_path(self):
        http_dir = self.http_base_dir + self.http_base_path
        if not os.path.exists(http_dir):
            os.mkdir(http_dir)
        link_name = http_dir + '/logs'
        if os.path.exists(link_name):
            os.unlink(link_name)
        os.symlink(self.log_base, link_name, True)

    def run(self, result: TestResult) -> TestResult:
        # TODO: may threading of scenario reading help improving the performance?
        #threading.Thread(target=self._read_scenario).start()
        # timeout = False
        # while not (timeout or result.shouldStop):
        #     t = 0
        #     while not timeout:
        #         wait for self.wait_time for the new TC parsed and added to the suite
                # if len(self._tests) == 0 or self._tests[-1] is None:
                #     time.sleep(self.interval)
                #     t += self.interval
                #     timeout = t >= self.wait_time
                # else:  # there's tc in the test suite to run
                #     super().run(result, debug=self.is_debug)
                #     break
        self._read_scenario()
        if not self._tests:
            print('No TestCases in the test suite. Please check test suite file and the tc files in the folder.')
            exit(-1)
        self.sce_status = ScenarioStatus.RUNNING
        # self.init_report_html()
        self.report.init_report_html(tests=self._tests)
        return super().run(result)

    def _read_scenario(self):
        # TODO: read scenario file thread function, read and parse scenario file and add TCs to the suite
        if self.scenario_format == SceFileFormat.XML:
            self._read_xml_scenario()
        elif self.scenario_format == SceFileFormat.JSON:
            self._read_json_scenario()
        else:  # CSV (default format)
            self._read_csv_scenario()

    def _read_json_scenario(self):
        # TODO: read scenario  in json file
        pysys_logger.error('JSON scenario file is not yet support')
        exit(-1)

    def _read_xml_scenario(self):
        # TODO: read scenario  in xml file
        pysys_logger.error('JSON scenario file is not yet support')
        exit(-1)

    def _read_csv_scenario(self):
        self.sce_df = self.scenario if isinstance(self.scenario, DataFrame) else pandas.read_csv(self.scenario)
        self.sce_df.QAID = self.sce_df.QAID.astype(int)
        self.col_tcid = self.sce_df[CsvFields.TCID]
        self.col_status = self.sce_df[CsvFields.RESULT]
        self.col_path = self.sce_df[CsvFields.PATH]
        for i, row in self.sce_df.iterrows():
            fixture_path_val: str = row[CsvFields.PATH]
            tc_id = row[CsvFields.TCID]
            tc_desc = row[CsvFields.OBJECTIVE] or ''
            if not numpy.isnan(tc_id):
                self.curr_tcid = tc_id
                fixture_path_list = SysTestSuite.get_fixture_path_list(fixture_path_val)
                tc_full_fname = self.tc_root_dir + '/' + '/'.join(fixture_path_list) + '/' + str(tc_id)
                if os.path.isfile(tc_full_fname):
                    if len(fixture_path_val.strip()) > 0:  # when path field is empty, fixture doesn't change
                        self.nevigate_to(fixture_path_list)
                    tc_info = TestCaseInfo(is_debug=self.is_debug, full_filename=tc_full_fname,
                                           fixture_path_list=self.curr_fixture_list,
                                           tc_id=self.curr_tcid, tc_desc=tc_desc, log_dir=self.log_dir)
                    tc = ScriptTC.make_scr_tc(tc_info, self)
                    tc.tcid_list = TcFileParser(tc_full_fname, self.curr_tcid).get_tcid_list()
                    self.addTest(tc)

    @staticmethod
    def get_fixture_path_list(path_val: str) -> list:
        path_list: list = path_val.strip('/').split('/')
        path_list = path_list[:1] + path_list[3:]  # remove task and release from path
        return path_list

    def update_status(self, tcid_list: list, tc_status, update_csv=True):
        tcid_filter = self.col_tcid.isin(tcid_list)
        # tc_status = result.tc_status
        if update_csv and self.scenario_format == SceFileFormat.CSV:
            if tc_status == TestStatus.SUCCESS:
                self.col_status[tcid_filter] = CvsTcStatus.PASSED
            elif tc_status == TestStatus.FAILURE or tc_status == TestStatus.ERROR:
                self.col_status[tcid_filter] = CvsTcStatus.FAILED
                self.failed_tcid_list += tcid_list
                list(set(self.failed_tcid_list))
            elif tc_status == TestStatus.WARNING:
                self.col_status[tcid_filter] = CvsTcStatus.WARNING
            else:  # Skip or notrun
                self.col_status[tcid_filter] = CvsTcStatus.NOTRUN
        else: # JSON, XML, not yet support
            #TODO support SML, JSON format scenario
            pysys_logger.error('scenario file other than CVS format is yet supported')
            exit(-1)
        self.sce_df.to_json(self.log_dir + '/scenario.json')

    """Override the method in PyUnit suite.py. generate info to update html report"""
    def _removeTestAtIndex(self, index):
        tc: SysTestCase = self._tests[index]
        if tc.shouldStop or index >= len(self._tests) - 1:
            self.sce_status = ScenarioStatus.DONE
            next_tc = None
        else:
            next_tc = self._tests[index + 1]
        move_next = not (isinstance(tc, ScriptFixture) and isinstance(next_tc, ScriptFixture))
        # self.update_report_html(tc, move_next)
        self.report.update_report_html(tc, move_next, self.sce_status)
        super()._removeTestAtIndex(index)

    # ''' Override the method in PyUnit suite. pop TC and update scenario status report.'''
    # def _removeTestAtIndex(self, index):
    #     """Stop holding a reference to the TestCase at index."""
    #     try:
    #         test = self._tests[index]
    #     except TypeError:
    #         support for suite implementations that have overridden self._tests
            # pysys_logger.error('failed to run test in suite in method {}'.format(self._removeTestAtIndex.__name__))
            # raise
            # pass
        # else:
        #     Some unittest tests add non TestCase/TestSuite objects to
        #     the suite.
            # if hasattr(test, 'countTestCases'):
            #     self._removed_tests += test.countTestCases()
            # if self.rm_tc_set_none:
            #     self._tests[index] = None
            # else:  # By default - pop TC/Fixture from the list
            #     self._tests.pop(index)

    def nevigate_to(self, to_list: str):
        # curr_list: list = self.curr_fixture_path.strip('/').split('/')
        # to_list: list = to_path_list.strip('/').split('/')
        # TODO: might change the normalize the to_path before pass in, avoid comparing list when curr == to
        # to_list = to_list[:1] + to_list[3:]  # remove task and release from path
        # deep_curr = len(curr_list)
        deep_curr = len(self.curr_fixture_list)
        deep_to = len(to_list)

        deep_anchor = min(deep_curr, deep_to)  # when nevigating up/down within same ancestor path
        for i in range(deep_anchor):
            if self.curr_fixture_list[i] != to_list[i]:  # not within the same ancestor path
                deep_anchor = i
                break

        for i in range(deep_curr, deep_anchor, -1):
            path = self.tc_root_dir + '/' + '/'.join(self.curr_fixture_list[:i])
            # fixture_file = SysTestCase.get_fixture_file(self.tc_root_dir + '/' + '/'.join(self.curr_fixture_list[:i]))
            # fixture_file = SysTestCase.get_fixture_file(path)
            fixture_file = self.get_fixture_file(path)
            # if fixture_file:
            if (not self.skip_fixture or self.dont_skip_fixture(path)) and fixture_file:
                fixture_info = TestCaseInfo(is_debug=self.is_debug, full_filename=fixture_file, tc_id=self.curr_tcid,
                                            fixture_path_list=to_list, log_dir=self.log_dir)
                fixture = ScriptFixture.make_teardown_fixutre(fixture_info, self)
                self.addTest(fixture)
            # init_file = SysTestCase.get_init_file(self.tc_root_dir + '/' + '/'.join(self.curr_fixture_list[:i]))
            # if init_file:
            #     init_info = TestCaseInfo(is_debug=self.is_debug, full_filename=init_file, tc_id=self.curr_tcid,
            #                                 fixture_path_list=to_list, log_dir=self.log_dir)
            #     fixture_init = ScriptFixture.make_teardown_fixutre(init_info, self)
            #     self.addTest(fixture_init)
        for i in range(deep_anchor + 1, deep_to + 1):
            path = self.tc_root_dir + '/' + '/'.join(to_list[:i])
            #init_file = SysTestCase.get_init_file(path)
            init_file = self.get_init_file(path)
            if init_file:
                init_info = TestCaseInfo(is_debug=self.is_debug, full_filename=init_file, tc_id=self.curr_tcid,
                                         fixture_path_list=to_list, log_dir=self.log_dir)
                fixture_init = ScriptFixture.make_setup_fixutre(init_info, self)
                self.addTest(fixture_init)
            # fixture_file = SysTestCase.get_fixture_file(self.tc_root_dir + '/' + '/'.join(to_list[:i]))
            # fixture_file = SysTestCase.get_fixture_file(path)
            fixture_file = self.get_fixture_file(path)
            # if fixture_file:
            if (not self.skip_fixture or self.dont_skip_fixture(path)) and fixture_file:
                fixture_info = TestCaseInfo(is_debug=self.is_debug, full_filename=fixture_file, tc_id=self.curr_tcid,
                                            fixture_path_list=to_list, log_dir=self.log_dir)
                fixture = ScriptFixture.make_setup_fixutre(fixture_info, self)
                self.addTest(fixture)

        self.curr_fixture_list = to_list
        # self.curr_fixture_path = '/' + '/'.join(to_list)

    def get_fixture_file(self, path: str): #, file_name: str = 'fixture.prov'):
        if path[-1] != '/':
            path += '/'
        if self.fixture_fname:
            fixture_file = path + self.fixture_fname
            if not os.path.exists(fixture_file):
                if self.fixture_fallback:
                    fixture_file = path + 'fixture.prov'
                    if not os.path.exists(fixture_file):
                        fixture_file = None
                else:
                    fixture_file = None
        else:
            fixture_file = path + 'fixture.prov'
            if not os.path.exists(fixture_file):
                fixture_file = None
        return fixture_file

    def get_init_file(self, path: str):
        if path[-1] != '/':
            path += '/'
        if self.init_fname:
            init_file = path + self.init_fname
            if not os.path.exists(init_file):
                if self.init_fallback:
                    init_file = path + 'init.prov'
                    if not os.path.exists(init_file):
                        init_file = None
                else:
                    init_file = None
        else:
            init_file = path + 'init.prov'
            if not os.path.exists(init_file):
                init_file = None
        return init_file

    @staticmethod
    def dont_skip_fixture(path: str) -> bool:
        if path[-1] != '/':
            path += '/'
        return os.path.exists(path + 'dont_skip')

    def update_report_html(self, tc: SysTestCase, move_next: bool):
        curr_tc = self.report.testcases[self.report.curr_tc_index]
        curr_tc.attrib['href'] = tc.log_fname
        curr_span = curr_tc.getparent()
        curr_class = curr_span.get('class')
        curr_running_status = self.report.running_status.get('status')
        # status level could only escalate
        tc_status_updated = False
        if curr_class == ReportParm.TC_INIT and tc.status == TestStatus.SUCCESS:
            curr_tc.attrib['status'] = curr_span.attrib['class'] = ReportParm.TC_PASS
            tc_status_updated = True
        elif (curr_class == ReportParm.TC_INIT or curr_class == ReportParm.TC_PASS) and tc.status == TestStatus.WARNING:
            curr_tc.attrib['status'] = curr_span.attrib['class'] = ReportParm.TC_WARN
            tc_status_updated = True
        elif (curr_class == ReportParm.TC_INIT or curr_class == ReportParm.TC_PASS or curr_class == ReportParm.TC_WARN) \
                and (tc.status == TestStatus.ERROR or tc.status == TestStatus.FAILURE):
            curr_tc.attrib['status'] = curr_span.attrib['class'] = ReportParm.TC_ERROR
            tc_status_updated = True

        # running_status_updated = curr_running_status != self.sce_status
        # if running_status_updated:
        if curr_running_status != self.sce_status:
            self.report.running_status.text = self.sce_status
            self.report.running_status.attrib['status'] = self.sce_status

        if move_next:
            # self.report.testcases[self.report.curr_tc_index].attrib.pop('id')
            curr_tc.attrib.pop('id')
            if self.report.curr_tc_index < len(self.report.testcases) - 1:
                self.report.curr_tc_index += 1
                # self.report.testcases[self.report.curr_tc_index].attrib['id'] = ReportParm.CURR_TC
                curr_tc = self.report.testcases[self.report.curr_tc_index]
                curr_tc.attrib['id'] = ReportParm.CURR_TC
        if move_next or tc_status_updated:
            self.report.file.seek(0)
            self.report.file.truncate()
            self.report.file.write(etree.tostring(self.report.document))
            self.report.file.flush()
            self.report.tc_update_file.seek(0)
            self.report.tc_update_file.truncate()
            # self.report.tc_update_file.write(self.report.testcases[self.report.curr_tc_index].get('title'))
            self.report.tc_update_file.write(curr_tc.get('title') + ':' + curr_tc.get('status'))
            self.report.tc_update_file.flush()
        if self.sce_status == ScenarioStatus.DONE:
            self.report.file.close()
            self.report.tc_update_file.close()

    def init_report_html(self):
        # TODO: might merge this with nevigate_to and read_scenario loop less
        # global pysys_root
        pysys_report = pysys_root + '/report'
        report_template = pysys_report + '/template.html'
        shutil.copy(pysys_report + '/default.css', self.log_dir)
        shutil.copy(pysys_report + '/mktree.css', self.log_dir)
        shutil.copy(pysys_report + '/mktree.js', self.log_dir)
        shutil.copy(pysys_report + '/update.js', self.log_dir)
        shutil.copy(pysys_report + '/scenario.gif', self.log_dir)
        shutil.copy(pysys_report + '/plus.gif', self.log_dir)
        shutil.copy(pysys_report + '/minus.gif', self.log_dir)
        shutil.copy(pysys_report + '/bullet.gif', self.log_dir)
        # with open(report_template, 'r') as f:
        #     c = f.read()
        # self.report.document = tree = lxml.etree.HTML(c)
        tree: etree._Element = etree.parse(report_template, etree.HTMLParser())
        self.report.document = tree
        self.report.expand_all, self.report.collapse_all = tree.xpath('//body/a')[:2]
        self.report.root = elem = tree.find('body/ul')
        self.report.hierarchy = tree.find('body//*[@id="{}"]'.format(ReportParm.hierarchy))
        self.report.running_status = tree.find('body//*[@id="{}"]'.format(ReportParm.RUNNING_STATUS))
        self.report.running_status.attrib['status'] = self.report.running_status.text = ScenarioStatus.RUNNING
        has_fixture = False
        curr_path_list = None
        for tc in self._tests:
            if isinstance(tc, ScriptFixture):
                has_fixture = True
            elif isinstance(tc, ScriptTC):
                if tc.tc_info.fixture_path_list and curr_path_list != tc.tc_info.fixture_path_list:
                    elem = self.report.root
                    for folder in tc.tc_info.fixture_path_list:
                        if folder not in [e.strip() for e in elem.xpath('li/span/text()')]:
                            elem = self._add_path_elem(elem, folder)
                        else:
                            elem = elem.find('li/ul')
                if has_fixture:
                    self._add_fixture_elem(elem, str(tc.tc_info.tcid))
                    has_fixture = False
                self._add_tc_elem(elem, ' | '.join(tc.tcid_list))
                curr_path_list = tc.tc_info.fixture_path_list
            else:
                raise TypeError('TC other than ScriptTC are not yet supported.')
                exit(-1)
        report_fname = self.log_dir + '/scenario.html'
        # with open(report_scenario, 'wb') as f:
        #     f.write(etree.tostring(tree))
        # tree.write(report_scenario)
        self.report.document = tree
        self.report.testcases = self.report.root.findall('.//a')
        self.report.curr_tc_index = 0
        curr_tc = self.report.testcases[0]
        curr_tc.attrib['id'] = ReportParm.CURR_TC
        self.report.file = open(report_fname, 'wb')
        self.report.file.write(etree.tostring(tree))
        self.report.file.flush()
        self.report.tc_update_file = open(self.log_dir + '/tc_update', 'w')
        self.report.tc_update_file.write(curr_tc.get('title') + ':' + curr_tc.get('status'))
        self.report.tc_update_file.flush()
        webbrowser.open(self.report.url)
        # webdriver.Firefox().get(self.report.url)

    @staticmethod
    def _add_path_elem(curr_elem, folder) -> etree._Element:
        """
        <ul>  <--- curr_elem
        <li class="liOpen"> <--- set default class to liOpen, so that the tree is expanded by default
          <img src="scenario.gif" onClick="expandOrCollapse(this,'<elem_id>','Scenario'); return false;" title="Expand Scenario"/>
          <span class="tree_init"> PATH1 </span>
          <ul>  <--- nevigate to here
          </ul>
        </li>
        </ul>
        """
        elem = etree.SubElement(curr_elem, 'li', {'class': 'liOpen'})
        etree.SubElement(elem, 'img',
                         attrib={'src': 'scenario.gif',
                                 'onClick': 'expandOrCollapse(this, "{}", "Scenario"); return false;'.format(folder),
                                 'title': 'Expand Scenario'})
        etree.SubElement(elem, 'span', attrib={'class': 'tree_init'}).text = folder
        return etree.SubElement(elem, 'ul')

    @staticmethod
    def _add_fixture_elem(curr_elem, tc_id: str):
        SysTestSuite._add_tc_elem(curr_elem, tc_id + '_fixture')

    @staticmethod
    def _add_tc_elem(curr_elem, tc_title: str):
        """
        <ul> <---- # curr_elem
          <span class= "test_list_warn">
            <a TITLE="997866_fixture" href="887966_fixture.log" TARGET="testFrame"">
              887966_fixture -&nbsp;
            </a>
          </span>
          <br>
        </ul>
        """
        elem = etree.SubElement(curr_elem, 'span', attrib={'class': ReportParm.TC_INIT})
        etree.SubElement(elem, 'a',
                         attrib={'title': tc_title, 'status': ReportParm.TC_INIT, 'target': 'testFrame'}
                         ).text = tc_title
        etree.SubElement(elem, 'br')


class ReportHtml:
    def __init__(self, testsuite=None, url='', file='', tc_update_file='', report_dir='', base_path=''):
        self.document: etree._ElementTree = None
        self.hierarchy: etree._Element  = None
        self.running_status: etree._Element  = None
        self.expand_all: etree._Element  = None
        self.collapse_all: etree._Element  = None
        self.root: etree._Element  = None
        self.curr_tc_index = 0
        self.testcases = []
        self.file = None
        self.tc_update_file = None
        self.testsuite: SysTestSuite = testsuite
        self.report_dir = None  # same as log_dir by default
        self.url = url
        self.base_path = base_path

    def init_report_html(self, tests=()):
        # TODO: might merge this with nevigate_to and read_scenario loop less
        # global pysys_root
        pysys_report = pysys_root + '/report'
        report_template = pysys_report + '/template.html'
        shutil.copy(pysys_report + '/default.css', self.base_path)
        shutil.copy(pysys_report + '/mktree.css', self.base_path)
        shutil.copy(pysys_report + '/mktree.js', self.base_path)
        shutil.copy(pysys_report + '/update.js', self.base_path)
        shutil.copy(pysys_report + '/scenario.gif', self.base_path)
        shutil.copy(pysys_report + '/plus.gif', self.base_path)
        shutil.copy(pysys_report + '/minus.gif', self.base_path)
        shutil.copy(pysys_report + '/bullet.gif', self.base_path)
        # with open(report_template, 'r') as f:
        #     c = f.read()
        # self.document = tree = lxml.etree.HTML(c)
        tree: etree._Element = etree.parse(report_template, etree.HTMLParser())
        self.document = tree
        self.expand_all, self.collapse_all = tree.xpath('//body/a')[:2]
        self.root = elem = tree.find('body/ul')
        self.hierarchy = tree.find('body//*[@id="{}"]'.format(ReportParm.hierarchy))
        self.running_status = tree.find('body//*[@id="{}"]'.format(ReportParm.RUNNING_STATUS))
        self.running_status.attrib['status'] = self.running_status.text = ScenarioStatus.RUNNING
        has_fixture = False
        curr_path_list = None
        # for tc in self._tests:
        for tc in tests:
            if isinstance(tc, ScriptFixture):
                has_fixture = True
            elif isinstance(tc, ScriptTC):
                if tc.tc_info.fixture_path_list and curr_path_list != tc.tc_info.fixture_path_list:
                    elem = self.root
                    for folder in tc.tc_info.fixture_path_list:
                        if folder not in [e.strip() for e in elem.xpath('li/span/text()')]:
                            elem = self._add_path_elem(elem, folder)
                        else:
                            elem = elem.find('li/span[.="{}"]/../ul'.format(folder))
                if has_fixture:
                    self._add_fixture_elem(elem, str(tc.tc_info.tcid))
                    has_fixture = False
                # self._add_tc_elem(elem, ' | '.join(tc.tcid_list))
                self._add_tc_elem(elem, ' | '.join(tc.tcid_list) + ' - ' + tc.tc_info.desc)
                curr_path_list = tc.tc_info.fixture_path_list
            else:
                raise TypeError('TC other than ScriptTC are not yet supported.')
                exit(-1)
        report_fname = self.base_path + '/scenario.html'
        # with open(report_scenario, 'wb') as f:
        #     f.write(etree.tostring(tree))
        # tree.write(report_scenario)
        self.document = tree
        self.testcases = self.root.findall('.//a')
        self.curr_tc_index = 0
        curr_tc = self.testcases[0]
        curr_tc.attrib['id'] = ReportParm.CURR_TC
        self.file = open(report_fname, 'wb')
        self.file.write(etree.tostring(tree))
        self.file.flush()
        self.tc_update_file = open(self.base_path + '/tc_update', 'w')
        self.tc_update_file.write(curr_tc.get('title') + ':' + curr_tc.get('status'))
        self.tc_update_file.flush()
        webbrowser.open(self.url)
        # webdriver.Firefox().get(self.url)

    def update_report_html(self, tc: SysTestCase, move_next: bool, sce_status=ScenarioStatus.RUNNING):
        curr_tc = self.testcases[self.curr_tc_index]
        curr_tc.attrib['href'] = tc.log_fname
        curr_span = curr_tc.getparent()
        curr_class = curr_span.get('class')
        curr_running_status = self.running_status.get('status')
        # status level could only escalate
        tc_status_updated = False
        if curr_class == ReportParm.TC_INIT and tc.status == TestStatus.SUCCESS:
            curr_tc.attrib['status'] = curr_span.attrib['class'] = ReportParm.TC_PASS
            tc_status_updated = True
        elif (curr_class == ReportParm.TC_INIT or curr_class == ReportParm.TC_PASS) and tc.status == TestStatus.WARNING:
            curr_tc.attrib['status'] = curr_span.attrib['class'] = ReportParm.TC_WARN
            tc_status_updated = True
        elif (curr_class == ReportParm.TC_INIT or curr_class == ReportParm.TC_PASS or curr_class == ReportParm.TC_WARN) \
                and (tc.status == TestStatus.ERROR or tc.status == TestStatus.FAILURE):
            curr_tc.attrib['status'] = curr_span.attrib['class'] = ReportParm.TC_ERROR
            tc_status_updated = True

        # running_status_updated = curr_running_status != self.sce_status
        # if running_status_updated:
        if curr_running_status != sce_status:
            self.running_status.text = sce_status
            self.running_status.attrib['status'] = sce_status

        if move_next:
            # self.testcases[self.curr_tc_index].attrib.pop('id')
            curr_tc.attrib.pop('id')
            if self.curr_tc_index < len(self.testcases) - 1:
                self.curr_tc_index += 1
                # self.testcases[self.curr_tc_index].attrib['id'] = ReportParm.CURR_TC
                curr_tc = self.testcases[self.curr_tc_index]
                curr_tc.attrib['id'] = ReportParm.CURR_TC
        if move_next or tc_status_updated:
            self.file.seek(0)
            self.file.truncate()
            self.file.write(etree.tostring(self.document))
            self.file.flush()
            self.tc_update_file.seek(0)
            self.tc_update_file.truncate()
            # self.tc_update_file.write(self.testcases[self.curr_tc_index].get('title'))
            self.tc_update_file.write(curr_tc.get('title') + ':' + curr_tc.get('status'))
            self.tc_update_file.flush()
        if sce_status == ScenarioStatus.DONE:
            self.file.close()
            self.tc_update_file.close()

    @staticmethod
    def _add_path_elem(curr_elem, folder) -> etree._Element:
        """
        <ul>  <--- curr_elem
        <li class="liOpen"> <--- set default class to liOpen, so that the tree is expanded by default
          <img src="scenario.gif" onClick="expandOrCollapse(this,'<elem_id>','Scenario'); return false;" title="Expand Scenario"/>
          <span class="tree_init"> PATH1 </span>
          <ul>  <--- nevigate to here
          </ul>
        </li>
        </ul>
        """
        elem = etree.SubElement(curr_elem, 'li', {'class': 'liOpen'})
        etree.SubElement(elem, 'img',
                         attrib={'src': 'scenario.gif',
                                 'onClick': 'expandOrCollapse(this, "{}", "Scenario"); return false;'.format(folder),
                                 'title': 'Expand Scenario'})
        etree.SubElement(elem, 'span', attrib={'class': 'tree_init'}).text = folder
        return etree.SubElement(elem, 'ul')

    @staticmethod
    def _add_fixture_elem(curr_elem, tc_id: str):
        SysTestSuite._add_tc_elem(curr_elem, tc_id + '_fixture')

    @staticmethod
    def _add_tc_elem(curr_elem, tc_title: str):
        """
        <ul> <---- # curr_elem
          <span class= "test_list_warn">
            <a TITLE="997866_fixture" href="887966_fixture.log" TARGET="testFrame"">
              887966_fixture -&nbsp;
            </a>
          </span>
          <br>
        </ul>
        """
        elem = etree.SubElement(curr_elem, 'span', attrib={'class': ReportParm.TC_INIT})
        etree.SubElement(elem, 'a',
                         attrib={'title': tc_title, 'status': ReportParm.TC_INIT, 'target': 'testFrame'}
                         ).text = tc_title
        etree.SubElement(elem, 'br')


class ReportParm:
    RUNNING_STATUS = 'running_status'
    hierarchy = 'hierarchy'
    CURR_TC = 'curr_tc'
    TC_PASS = 'test_list_pass'
    TC_WARN = 'test_list_warn'
    TC_ERROR = 'test_list_erro'
    TC_INIT = 'test_list_init'
