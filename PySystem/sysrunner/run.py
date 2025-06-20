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
from monitor import init_logger, get_logger
# runner_dir = os.path.dirname(os.path.abspath(__file__))
# pysys_root = os.path.abspath(runner_dir + '/..')
# sys.path.append(pysys_root)
from SystemTestCase.sys_suite import SysTestSuite, CsvFields
from SystemTestCase import helpers
from SystemTestCase.SysTestCase import TcFailAction
logger = get_logger(__name__)
from executor.sysrunner import SysTestRunner
from config.environment import ENV


def setup_report_dir(log_base: str, http_base_dir: str, http_base_path: str, log_dir: str) -> str:
    """Prepare report directory and return the report URL."""
    http_base_path = helpers.format_path(http_base_path)
    report_url = 'http://{}{}/logs/current/scenario.html'.format(ENV.CTRL_PC.ip, http_base_path)
    http_dir = http_base_dir + http_base_path
    link_name = http_dir + '/logs'
    use_local_path = False
    try:
        if not os.path.exists(http_dir):
            os.makedirs(http_dir)
        if not os.access(http_dir, os.W_OK):
            raise PermissionError('Directory not writable')
        if os.path.exists(link_name):
            os.unlink(link_name)
        os.symlink(log_base, link_name, True)
    except PermissionError as e:
        logger.warning('Cannot access %s: %s. Falling back to project logs directory.', http_dir, e)
        use_local_path = True
    except OSError as e:
        logger.warning('Failed to create symlink %s -> %s: %s', link_name, log_base, e)
        use_local_path = True

    local_report_path = log_dir + '/scenario.html'
    if use_local_path:
        report_url = 'file://' + local_report_path
        print('Report URL: {}'.format(report_url))
        print('Please open {} manually.'.format(local_report_path))
    else:
        print('Report URL: {}'.format(report_url))
    return report_url


def main():
    examples = (
        "Examples:\n"
        "  python run.py scenario.csv\n"
        "  python run.py -t tests -H /pysystem scenario.csv\n"
        "\u793a\u4f8b:\n"
        "  python run.py -s \u5355\u72ec\u6a21\u5f0f script.py"
    )
    parser = argparse.ArgumentParser(
        description='CLI runner for PySystem',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=examples
    )
    parser.add_argument('-t', '--tc_base', help='specify TC root dir')
    parser.add_argument('-s', '--standalone', action='store_true', default=False, help='Stand alone mode')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Verbose output')
    parser.add_argument('-D', '--debug', action='store_true', default=False,
                        help='Enable debug mode of scenario_file execution')
    # parser.add_argument('-sce', '--sce_decoded', action='store_true', help='Input scenario is decoded already')
    parser.add_argument('-sk', '--skip_fixture', action='store_true', default=False,
                        help='Skip fixture conf (prov files)')
    parser.add_argument('-c', '--conf', help='specify config file (JSON format)')
    parser.add_argument('--profile', help='load config profile from config/profiles')
    parser.add_argument('-H', '--html_path', help='specify the html report base url path')
    parser.add_argument('-P', '--pause_on_fail', action='store_true', default=False,
                        help='pause when current TC is fail')
    parser.add_argument('-A', '--action', type=TcFailAction, choices=list(TcFailAction),
                        default=TcFailAction.NEXT,
                        help='action when a testcase fails: continue, next or stop')
    # parser.add_argument('-p', '--proj_dir', help='specify project root path')
    # parser.add_argument('-e', '--env_dir', help='specify the path of lab environment files')
    # parser.add_argument('-l', '--lab_file', help='specify the file name of environment')
    parser.add_argument('-L', '--log_level', default='INFO',
                        help='specify the logging level (default: INFO)')
    # parser.add_argument('scenario', help='specify the scenario file to be run.')
    parser.add_argument('target',
                        help='specify the scenario file or testcase script (standalone mode) to be run')

    args = parser.parse_args()

    """Parse config file"""
    curr_path = os.getcwd()
    # def_conf = tc_base + '/properties.json'           # default config file from testcase base directory
    sys_conf = pysys_root + '/config/properties.json'  # default config file of Pyststem system
    with open(sys_conf, 'r') as f:
        conf: dict = json.load(f)
        assert len(conf) > 0

    REQUIRED_PROFILE_FIELDS = [
        'obj_dirs', 'tc_base', 'sce_root', 'node_list',
        'lab_dir', 'log_dir', 'Xauthority', 'Webdriver_dir'
    ]
    if args.profile:
        prof_path = os.path.join(pysys_root, 'config', 'profiles', f'{args.profile}.json')
        if not os.path.isfile(prof_path):
            raise FileNotFoundError(f'Profile {args.profile} not found: {prof_path}')
        with open(prof_path, 'r') as f:
            prof_conf = json.load(f)
        missing = [k for k in REQUIRED_PROFILE_FIELDS if k not in prof_conf]
        if missing:
            raise KeyError(f'Profile {args.profile} missing required keys: {", ".join(missing)}')
        conf.update(prof_conf)

    conf_file = args.conf
    if conf_file:
        if os.path.isfile(conf_file):
            with open(conf_file, 'r') as f:
                conf.update(json.load(f))
        else:
            err_msg = 'The given config file {} doesn\'t exist'.format(conf_file)
            logger.error(err_msg)
            raise FileExistsError('err_msg')

    # parse base directory of test cases
    if args.tc_base:
        if os.path.isdir(args.tc_base):
            tc_base = args.tc_base
        else:
            logger.error('Test Base dir "{}" doesn\'t exist'.format(args.tc_base))
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
        importlib.import_module('environment')
    # Initialize nodes from profile
    node_names = conf.get('node_list') or []
    if node_names:
        from config import elements
        for n in node_names:
            if hasattr(elements, n):
                setattr(ENV, n, getattr(elements, n))

    # Logging path
    log_base: str = conf.get('log_dir')
    if log_base:
        # if not log_base.startswith('/'):
            # log_base = tc_base + '/' + log_base
        log_base = tc_base + helpers.format_path(log_base)
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
    http_base_path = args.html_path or conf.get('http_base_path') or '/pysystem'
    report_url = setup_report_dir(log_base, http_base_dir, http_base_path, log_dir)

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
    # scenario_file: str = args.scenario
    # scenario_file = 'standalone.csv' if args.standalone else args.target
        
    # if not scenario_file.startswith('/'):  # relative path to test base directory
    #     scenario_file = tc_base + '/' + args.scenario
    target_file = args.target
    if not args.standalone and not os.path.isabs(target_file):
        sce_root = conf.get('sce_root') or tc_base
        target_file = os.path.join(sce_root, target_file)

    tc_tab = get_standalon_sec if args.standalone else csv_scenario_parse(target_file)
    test_suite = SysTestSuite(tc_tab, tc_base=tc_base, is_debug=args.debug,
                              pause_fail=args.pause_on_fail, failed_action=args.action,
                              skip_fixture = args.skip_fixture,
                              # log_base=log_base, log_dir=log_dir,
                              # http_base_dir=http_base_dir, http_base_path=http_base_path,
                              report_url=report_url, log_dir=log_dir, conf=conf)
    print("Test Scenario is initialized.")
    runner = SysTestRunner()
    try:
        runner.run(test=test_suite)
    except Exception as e:
        logger.error('Test execution aborted: %s', e, exc_info=True)

def csv_scenario_parse(scenario_file: str) -> DataFrame:
    with open(scenario_file, 'r') as f:
        tc_tab = pandas.read_csv(f)
    tc_tab.sort_values(CsvFields.PATH)  #  sort by fiture path
    tc_tab.drop(tc_tab[numpy.isnan(tc_tab.QAID)].index, inplace=True)
    tc_tab.QAID = tc_tab.QAID.astype(int)
    return tc_tab

# prepare standalone mode scenario file
def get_standalone_sec(tc_file: str, tc_base: str) -> DataFrame:
    path, tcid = tc_file.rsplit('/', 1)
    with open('standalone.csv', 'r') as f:
        tc_tab = pandas.read_csv(f)
    tc_tab.at[0, 'QAID'] = tc_id
    path = os.path.abspath(path)
    path = path.lstrip(tc_base)
    path = '/' + path.split('/', 1)[0] + '/0/standalone/' + path.split('/', 1)[1]
    tc_tab.at[0, 'Path'] = path

if __name__ == '__main__':
    main()
