from SystemTestCase import SysTestCase


class TcExecutor(object):
    def __init__(self):
        pass

    def run_tc(self, tc_content: str) -> None:
        setup_steps, test_steps, teardown_steps = self.get_sections(tc_content)
        SysTestCase()

    def get_sections(self, tc_content: str) -> ():
        pass

