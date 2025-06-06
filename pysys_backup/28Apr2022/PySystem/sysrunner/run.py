#!/usr/bin/python3
# CLI runner of PySystem
"""
usage:

"""

import importlib
import argparse
import json
import os
import sys
import shutil
import numpy

import pandas
from pandas.core.frame import DataFrame

from sysinit import pysys_root
from monitor import pysys_log
# runner_dir = os.path.dirname(os.path.abspath(__file__))
# pysys_root = os.path.abspath(runner_dir + '/..')
# sys.path.append(pysys_root)
from SystemTestCase.sys_suite import SysTestSuite, CsvFields
from SystemTestCase import helpers
from SystemTestCase.SysTestCase import TcFailAction
from monitor.pysys_log import pysys_logger
from executor.sysrunner import SysTestRunner
from config.environment import ENV


def main():
    parser = argparse.ArgumentParser(description='CLI runner for PySystem')
    parser.add_argument('-t', '--tc_base', help='specify TC root dir')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-D', '--debug', action='store_true', help='Enable debug mode of scenario_file execution')
    # parser.add_argument('-g', '--gen_scenario', action='store_true', help='Generate scenario_csv from original TC list CSV')
    parser.add_argument('-s', '--sce_decoded', action='store_true', help='Input scenario is decoded already')
    parser.add_argument('-c', '--conf', help='specify config file (JSON format)')
    parser.add_argument('-P', '--pause_on_fail', action='store_true', help='pause when current TC is fail.')
    parser.add_argument('-A', '--action', type=TcFailAction, choices=list(TcFailAction))
    # parser.add_argument('-p', '--proj_dir', help='specify project root path')
    # parser.add_argument('-e', '--env_dir', help='specify the path of lab environment files')
    # parser.add_argument('-l', '--lab_file', help='specify the file name of environment')
    parser.add_argument('-L', '--log_level', help='specify the logging level')
    parser.add_argument('scenario', help='specify the scenario file to be run.')

    args = parser.parse_args()

    """Parse config file"""
    curr_path = os.getcwd()
    # def_conf = tc_base + '/properties.json'           # default config file from testcase base directory
    sys_conf = pysys_root + '/config/properties.json'  # default config file of Pyststem system
    with open(sys_conf, 'r') as f:
        conf: dict = json.load(f)
        assert len(conf) > 0
    # conf_file = args.conf or def_conf
    conf_file = args.conf
    if conf_file:
        if os.path.isfile(conf_file):
            with open(conf_file, 'r') as f:
                conf.update(json.load(f))
        else:
            err_msg = 'The given config file {} doesn\'t exist'.format(conf_file)
            pysys_logger.error(err_msg)
            raise FileExistsError('err_msg')

    # parse base directory of test cases
    if args.tc_base:
        if os.path.isdir(args.tc_base):
            tc_base = args.tc_base
        else:
            pysys_logger.error('Test Base dir "{}" doesn\'t exist'.format(args.tc_base))
            exit(-1)
    else:
        tc_base = conf.get('tc_base') or curr_path
    tc_base = helpers.format_path(tc_base)

    # Paths of system objects being used in the test
    obj_dirs: list = conf.get('obj_dirs')
    if obj_dirs:
        sys.path.extend(obj_dirs)

    # customize lab environment
    lab_dir: str = conf.get('lab_dir')
    if lab_dir:
        sys.path.append(lab_dir)
        importlib.import_module('environment.environment')

    # Logging path
    log_base: str = conf.get('log_dir')
    if log_base:
        if not log_base.startswith('/'):
            log_base = tc_base + '/' + log_base
    else:
        log_base = tc_base + '/logs'
    log_dir = helpers.gen_logdir(log_base)

    # http_base_dir: str = conf.get('http_dir')
    # if not http_base_dir:
    #     http_base_dir = '/var/www/html'
    # http_base_path: str = conf.get('http_base_path')
    # if not http_base_path:
    #     http_base_path = '/pysystem'
    http_base_dir = conf.get('http_dir') or '/var/www/html'
    http_base_path = conf.get('http_base_path') or '/pysystem'
    # report_url = 'http://localhost{}/logs/current/scenario.html'.format(http_base_path)
    report_url = 'http://{}/{}/logs/current/scenario.html'.format(ENV.CTRL_PC.ip, http_base_path)
    http_dir = http_base_dir + http_base_path
    if not os.path.exists(http_dir):
        os.mkdir(http_dir)
    link_name = http_dir + '/logs'
    if os.path.exists(link_name):
        os.unlink(link_name)
    os.symlink(log_base, link_name, True)

    '''#################################'''
    ''' GUI webdriver environment config'''
    '''#################################'''
    webdriver_dir = helpers.format_path(conf.get('Webdriver_dir'))
    if webdriver_dir:
        os.environ['PATH'] += ':{}'.format(webdriver_dir)
    # assert os.getenv('HOME') == '/root', 'Should start Webdriver in root session (sudo -i)'
    # set Xauthority to allow running Firefox as root in sudo session
    # sudo_user = os.getenv('SUDO_USER')
    # sudo_home = os.path.expanduser('~' + sudo_user)
    # xauth_file = sudo_home + '/.Xauthority'
    # if os.path.exists(xauth_file):
        # shutil.copy(xauth_file, '/root/.')
        # shutil.chown('/root/.Xauthority', 'root')
    xauth = conf.get('Xauthority')
    if xauth:
        os.putenv('XAUTHORITY', xauth)

    # read and parse the scenario_file csv file
    scenario_file: str = args.scenario
    # if not scenario_file.startswith('/'):  # relative path to test base directory
    #     scenario_file = tc_base + '/' + args.scenario
    # tc_tab: DataFrame = csv_scenario_parse(scenario_file, args.gen_scenario)
    tc_tab: DataFrame = csv_scenario_parse(scenario_file, args.sce_decoded)
    test_suite = SysTestSuite(tc_tab, tc_base=tc_base, is_debug=args.debug,
                              pause_fail=args.pause_on_fail, failed_action=args.action,
                              # log_base=log_base, log_dir=log_dir,
                              # http_base_dir=http_base_dir, http_base_path=http_base_path,
                              report_url=report_url, log_dir=log_dir, conf=conf)
    print("Test Scenario is initialized.")
    runner = SysTestRunner()
    runner.run(test=test_suite)


# def csv_scenario_parse(scenario_file: str, gen_scenario: bool) -> DataFrame:
def csv_scenario_parse(scenario_file: str, is_dedoced : bool) -> DataFrame:
    with open(scenario_file, 'r') as f:
        tc_tab = pandas.read_csv(f)
    # if gen_scenario:  # the file is the original csv file of Test cases
    if not is_dedoced:  # the file is the original csv file of Test cases
        # tc_tab: DataFrame = tc_tab[tc_tab.Autotested == 'Yes']  # filter the non-auto TCs
        tc_tab.sort_values(CsvFields.PATH)  #  sort by fiture path
    tc_tab.drop(tc_tab[numpy.isnan(tc_tab.QAID)].index, inplace=True)
    tc_tab.QAID = tc_tab.QAID.astype(int)
    return tc_tab


if __name__ == '__main__':
    main()
