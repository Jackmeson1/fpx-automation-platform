# Base class of System Object
from monitor.pysys_log import pysys_logger
from logging import _checkLevel
from SystemTestCase.tc_mapping import TcFuncMapping

# class DictNameSpace:
#     def __init__(self, mapping_dict: dict):
#         self.__dict__.update(mapping_dict)


class SysObj(TcFuncMapping):
    def __init__(self, conn_type,
                 ip: str = 'localhost',
                 port=0,
                 user='admin',
                 passwd='',
                 labels: dict = None):
        super().__init__()
        self.conn_type = conn_type
        self.ip = ip
        self.port = port
        self.user = user
        self.passwd = passwd
        self.labels: dict = labels
        self.node_name: str = ''
        # self.tc_func: dict = {}
        # self.cmd_params: dict = None

    def _init_tc_func(self):
        super()._init_tc_func()
        self.tc_func.update({
            'SYS_LOG': SysObj.sys_log
        })

    '''
    CRITICAL = 50
    ATAL = CRITICAL
    RROR = 40
    ARNING = 30
    ARN = WARNING
    NFO = 20
    EBUG = 10
    OTSET = 0
    '''

    @staticmethod
    def sys_log(log_params: dict):
        pysys_logger.log(_checkLevel(log_params.get('LEVEL'), log_params.get('msg')))
