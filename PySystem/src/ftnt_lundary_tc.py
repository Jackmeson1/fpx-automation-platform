from SystemTestCase.SysTestCase import SysTestCase
# from subprocess import call, check_output, run
import subprocess
from monitor import get_logger

logger = get_logger(__name__)

class DemoTc(SysTestCase):
    def __init__(self, test_method, tc_data_set: dict):
        super().__init__(test_method)
        self.tc_data_set = tc_data_set

    def setUp(self):
        super().setUp()
        print('@SETUP {}'.format(self.tc_data_set['tc_name']))

    def test_exec_tc(self) -> None :
        if self.tc_data_set['tc_name'] is not None:
            print('TEST... ' + self.tc_data_set['tc_name'])
            # call('echo "TC: === echo in test..."')
            # call(['ifconfig'])
            subprocess.call('echo "I like potatos"', shell=True)
            r = subprocess.run(['ifconfig'], stdout=subprocess.PIPE).stdout
            print(r)
            logger.warning('log info in test for report')
            # call(['ping www.google.com'])
            # call(['curl http://www.tired.com -kv'])

    def tearDown(self):
        print('@TEARDOWN')
