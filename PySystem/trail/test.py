# from monitor import pysys_log
import json
import shutil

from selenium import webdriver
from selenium.common.exceptions import *

from SystemObject.cli_node import CliNode
from SystemObject.gui_node import GuiNode
from SystemTestCase import helpers
from config.environment import ENV
from SystemObject import sys_obj, cli_node
from config import properties
import sys
import os

from sysrunner import pysys_root

sys.path.append(properties.project_dir)
runner_dir: str = os.path.dirname(os.path.abspath(__file__))
pysys_root: str = os.path.abspath(runner_dir + '/..')
sys.path.append(pysys_root)
# os.environ['PATH'] += ':/opt/Webdriver/bin'
# os.environ['XAUTHORITY'] = '/root/.Xauthority'

Linux105 = cli_node.LinuxCli(
        ip='127.0.0.1',
        port='22',
        conn_type=cli_node.ConnType.SSH,
        linux_type='CENTOS',
        labels={'IF_CLIENT': 'port2',
                'IF_INET': 'port1',
                'IF_SERVER': 'port3',
                'IF_MGMT': 'port4'
                }
        )

class TestEnv:
    PC1 = Linux105


def main():
    # p = argparse.ArgumentParser()
    # p.add_argument('-x', '--proxy', action='store_true')
    # p.add_argument('host')
    # p.add_argument('-u')
    #
    # arg_str = '-uleo --proxy localhost'
    # args = arg_str.split()
    # r = p.parse_args(args)
    # print(r)
    # print(r.host)
    # if r.proxy:
    #     print('proxy = True')

    # node = pexpect.spawn(None)
    ''' GUI webdriver environment config'''
    sys_conf = pysys_root + '/config/properties.json'  # default config file of Pyststem system
    with open(sys_conf, 'r') as f:
        conf: dict = json.load(f)
        assert len(conf) > 0
    webdriver_dir = helpers.format_path(conf.get('Webdriver_dir'))
    if webdriver_dir:
        # os.putenv('PATH', os.getenv('PATH') + ':{}'.format(webdriver))
        os.environ['PATH'] += ':{}'.format(webdriver_dir)
    # set Xauthority to allow running Firefox as root in sudo session
    assert os.getenv('HOME') == '/root', 'Should start Webdriver in root session (sudo -i)'
    sudo_user = os.getenv('SUDO_USER')
    sudo_home = os.path.expanduser('~' + sudo_user)
    shutil.copy(sudo_home + '/.Xauthority', '/root/.')
    shutil.chown('/root/.Xauthority', 'root')
    xauth = conf.get('Xauthority')
    if xauth:
        # os.putenv('XAUTHORITY', xauth)
        os.environ['XAUTHORITY'] = xauth

    # d = webdriver.Firefox()
    # d.get('http://www.tired.com')

    fpx2_gui = GuiNode(ip='172.18.29.2')
    fpx2_gui.login()


    g = GuiNode(accept_untrusted_cert=True)
    # g.get('http://www.tired.com')
    try:
        resp = g.get('http://172.18.29.2')
        print(resp)
    except WebDriverException:
        elem = g.browser.find_element_by_id('errorShortDesc2')
        if elem.text.find('SSL_ERROR_UNSUPPORTED_VERSION') >= 0 and g.accept_untrusted_cert:
            button = g.browser.find_element_by_tag_name('button')
            button.click()
    except Exception as e:
        print(e)
        print(g.browser.current_url)



    pc = ENV.PC1
    for node in ENV.__dict__.values():
        if isinstance(node, CliNode):
            node.login()
    cmd = "ssh -ladmin -o'RSAAuthentication=no' -o 'PubkeyAuthentication=no' -p 22 127.0.0.1"
    node = TestEnv.PC1
    node._spawn(cmd)
    # pc._spawn(cmd)
    pc.login()
    # node._spawn('ssh -q -ladmin -oRSAAuthentication=no -o PubkeyAuthentication=no -p 22 127.0.0.1')
    print('non-blocking')
    node.sendline('ls')
    pc.sendline('ls')
    print(node.after)

    # pysys_log.init_logger(log_level='ERROR')
    # pysys_log.pysys_logger.error('pysys log is init in main')
    # modulex.foo()

if __name__ == '__main__':
    main()
