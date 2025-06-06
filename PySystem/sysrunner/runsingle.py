#!/usr/bin/python3
import os
import sys
from unittest import TextTestRunner, TestSuite
runner_dir: str = os.path.dirname(os.path.abspath(__file__))
pysys_root: str = os.path.abspath(runner_dir + '/..')
sys.path.append(pysys_root)
# import sysrunner.system_init
import argparse
import importlib.util
import logging
from SystemTestCase.SysTestCase import TestCaseInfo
from SystemTestCase.script_testcase import ScriptTC
from SystemTestCase.sys_suite import SysTestSuite
from config import properties
from monitor import pysys_log
import json

sys.path.append(properties.tc_base_dir)
sys.path.append(properties.project_dir)
for path in properties.sys_obj_dir:
    sys.path.append(path)



def main():
    parser = argparse.ArgumentParser(description='parser of cli parameters of runbare.py')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-c', '--conf', help='specify config file (JSON format)')
    parser.add_argument('-p', '--proj_dir', help='specify project root path')
    parser.add_argument('-t', '--tc_base', help='specify TC root dir')
    parser.add_argument('-e', '--env_dir', help='specify the path of lab environment files')
    parser.add_argument('-l', '--lab_file', help='specify the file name of environment')
    parser.add_argument('-L', '--log_level', help='specify the logging level')
    parser.add_argument('tc_file')

    args = parser.parse_args()

    #incert args for debugging
    sys.argv.append('trail/demoscript')

    runner_dir: str = os.path.dirname(os.path.abspath(__file__))
    pysys_root: str = os.path.abspath(runner_dir + '/..')
    # if args.conf:
    #     spec = importlib.util.spec_from_file_location("cust_properties", args.conf)
    #     cust_conf = importlib.util.module_from_spec(spec)
    #     spec.loader.exec_module(cust_conf)
    #     # foo.MyClass()
    # else:
    #     pass

    conf_data: dict = {}
    # Pysystem default properties file
    with open(pysys_root +'/config/properties.json', 'r') as f:
        conf_data.update(json.load(f))

    tc_base = conf_data.get('tc_base')  # set tc_dir if the tc_base is not empty in default properties.json
    if args.tc_base:
        tc_base = args.tc_base
    elif tc_base is None or tc_base == '':    # set to current dir only when it is not set by args or default properties
        tc_base = os.getcwd()

    #load customed configured properties
    conf_file = args.conf if args.conf else tc_base + '/properties.json'
    if os.path.isfile(conf_file):
        with open(conf_file, 'r') as f:
            conf_data.update(json.load(f))

    logger = pysys_log.init_logger(conf_data.get('log_file'),
                                   conf_data.get('log_level'),
                                   conf_data.get('console_level'))

    #logger.info('argv is set as : {}'.format(sys.argv[-1]))
    tc_full_path = tc_base + '/' + args.tc_file
    to_fixture_path = os.path.dirname(tc_full_path)

    tc_info = TestCaseInfo(full_filename=tc_full_path)
    tc = ScriptTC(tc_info, 'test_scr_file')
    scenario = SysTestSuite()
    scenario.curr_fixture_path = tc_base
    scenario.nevigate_to(to_fixture_path)
    scenario.addTest(tc)
    runner = TextTestRunner()
    runner.run(scenario)
    print('....end....')
    # scenario.run()
    # tc.run()


if __name__ == '__main__':
    main()
