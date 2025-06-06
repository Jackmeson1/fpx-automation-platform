import re
from monitor import get_logger

logger = get_logger(__name__)
from config.environment import ENV
from collections import OrderedDict
from SystemTestCase.SysTestCase import SysTcFail


class TcSection:
    INIT = 'INIT'
    SETUP = 'SETUP'
    TEST = 'TEST'
    TEARDOWN = 'TEARDOWN'
    TCID_LIST = 'TCID'


class NameSpace:
    LOCAL = 'LOCAL'
    GLOBAL = 'GLOBAL'
    OTHER = 'OTHER'


class TcFileParser(object):
    P_SECTION = re.compile(r'<\s*(\w+)\s*>')
    P_LITERAL = re.compile(r'"(.*)"')
    P_LABEL = re.compile(r'\[\s*(\w+)\s*(:\s*(\w+))?\s*\]')
    P_LOCAL_LABEL = re.compile(r'\[\s*(\w+)\s*\]')
    P_LEGCY_LABEL = re.compile(r'(\w+):(\w+)')
    P_COLON_LABEL = re.compile(r'(\w+):(\w+)')
    P_VARIABLE = re.compile(r'\(\$(\w+)\)')
    P_SET_NODE = re.compile(r'\[\s*(\w+)\s*\]')
    P_SET_LABEL = re.compile(r'(\w+)\s*=\s*(.+)')
    P_SET_LIST = re.compile(r'(\w+)\s*=\s*\[([\w, \'\s\"]*)\]')
    P_SET_PARAMS = re.compile(r'@\s*\((.*)\)$')

    def __init__(self, file: str, tc_id: int):
        self.file = file
        self.tcid = str(tc_id)
        self.curr_node = None
        self.labels: dict = {}
        # if parse_file is None:
        #     self.parse_file = self.default_parse_file
        # else:
        #     self.parse_file = parse_file

    def parse_file(self, sections_to_parse: list = TcSection.__dict__.values()) -> tuple:
        setup_scr, test_scr, teardown_scr, init_scr = [], [], [], []
        tcid_list: list = [self.tcid]
        script: list = None
        section_parsed = []
        with open(self.file, 'r') as f:
            scr_started = False
            section = None
            # i = 0
            try:
                # for line in f:
                for i, line in enumerate(f):
                    # i += 1
                    line = line.strip()
                    m = TcFileParser.P_SECTION.match(line)
                    if m:
                        section: str = m.group(1)
                        if section == TcSection.INIT:
                            script = init_scr
                        elif section == TcSection.SETUP:
                            script = setup_scr
                        elif section == TcSection.TEST:
                            script = test_scr
                        elif section == TcSection.TEARDOWN:
                            script = teardown_scr
                        elif section == TcSection.TCID_LIST:
                            script = tcid_list
                        else:
                            logger.error('Section label {} in {} is not supported.'.format(section, self.file))
                            raise Exception('Section label {} in {} is not supported.'.format(section, self.file))
                            # TODO: log section label is not supported
                            pass
                        scr_started = True
                        """stop parsing when all desired sections are parsed"""
                        parse_done = True
                        for sc in sections_to_parse:
                            if sc not in section_parsed:
                                parse_done = False
                                break
                        if parse_done:
                            break
                        section_parsed.append(section)
                    elif section not in sections_to_parse:
                        """only parse the desired sections,"""
                        pass
                    elif not scr_started or line is None or len(line) == 0 or line.startswith('#'):
                        pass
                    elif script is tcid_list:
                        # tcid_list += self._parse_tcid_line(line)
                        # tcid_list = list(set(tcid_list))
                        # add_tc_list = list(set(self._parse_tcid_line(line)))
                        # tcid_list += add_tc_list.remove(self.tcid) if self.tcid in add_tc_list else add_tc_list
                        tcid_list += self._parse_tcid_line(line)
                        tcid_list = list(OrderedDict.fromkeys(tcid_list).keys())
                    else:
                        key, param = self.default_parse_line(line)
                        '''Should defer set Label to script runtime so that parameters could be modify on the fly. '''
                        # if key == TcDirective.SET_LABEL:
                        #     node = param[0]
                        #     if node:
                        #         node.labels[param[1]] = param[2]
                        #     else:
                        #         self.labels[param[1]] = param[2]
                        # elif key == TcDirective.SET_LIST:
                        #     #TODO: set list directive
                        #     pass
                        # else:
                        #     script.append((key, param))
                        script.append((i, (key, param)))
            except Exception as e:
                err_msg = 'Error occours @ line {} when parsing tc {}: '.format(i, self.tcid) + str(e) 
                logger.error(err_msg)
                raise SysTcFail(err_msg)
        return init_scr, setup_scr, test_scr, teardown_scr, tcid_list

    @staticmethod
    def _parse_tcid_line(line: str) -> list:
        # line = re.match(r'[\d\s,]+\d', line).group().strip()
        # return re.split(r'[,\s]+', line)
        m = re.match(r'[\d\s,]+\d', line)
        return re.split(r'[,\s]+', m.group().strip()) if m else []

    def get_tcid_list(self) -> list:
        return self.parse_file([TcSection.TCID_LIST])[-1]


    # def fetch_label(self, m) -> str:
    #     try:
    #         if m.group(3):  # [Node:Label]
    #             node = getattr(ENV, m.group(1))
    #             key = m.group(3)
            # else:  # [Label]: 1st - local labels; 2nd - labels in current node; 3rd - variables in current node
            #     key = m.group(1)
            #     local_label = self.labels.get(key)
            #     if local_label:  # found label in local labels
            #         return local_label
            #     node: SysObj = self.curr_node
            # pysys_logger.debug('To fetch Label {} from node @{}'.format(m.group(), node.ip))
            # return node.labels.get(key) or getattr(node, key)
        # except (AttributeError, NameError, KeyError):
            # # TODO: log error and set TC fail
            # print('Label error')
            # pysys_logger.error('Label: "{}" is not valid.'.format(key))
            # raise

    ''' param format: @ x = a; y = b1,b2,b3
        a is string and b1,b2,b3 is list of str
    '''
    @staticmethod
    def parse_cmd_params(param_text: str) -> dict:
        # param_text = param_text.strip()
        # param_text = TcFileParser.P_LABEL.sub(self.fetch_label, param_text)
        param_list = [x.strip() for x in param_text.split(';')]
        param_dict: dict = {}
        for param_str in param_list:
            key, value_str = param_str.split('=', maxsplit=1)
            key = key.rstrip()
            value_list = [v.strip() for v in re.split(r'(?<!\\),', value_str)]
            # param_dict[key] = value_str.strip() if len(value_str) == 1 else value_list
            param_dict[key] = value_list[0] if len(value_list) == 1 else value_list
        return param_dict

    def default_parse_line(self, line: str) -> tuple:
        # set tc_command parameter
        m = TcFileParser.P_SET_PARAMS.match(line)
        if m:
            return TcDirective.SET_PARAMS, TcFileParser.parse_cmd_params(m.group(1))
        # set local or global variable or list
        m = TcFileParser.P_SET_LIST.match(line)
        if m:
            return TcDirective.SET_LABEL, (m.group(1), [x.strip() for x in m.group(2).split(',')])
        m = TcFileParser.P_SET_LABEL.match(line)
        if m:
            # right_val = TcFileParser.P_LABEL.sub(self.fetch_label, m.group(2))
            # return TcDirective.SET_LABEL, (self.curr_node, m.group(1), right_val)
            return TcDirective.SET_LABEL, (m.group(1), m.group(2).rstrip())
        # Set current Node
        m = TcFileParser.P_SET_NODE.match(line)
        if m:
            node_name = m.group(1)
            if hasattr(ENV, node_name):
                self.curr_node = getattr(ENV, node_name)
            elif node_name == NameSpace.GLOBAL:
                self.curr_node = ENV
            elif node_name == NameSpace.LOCAL:
                self.curr_node = None
            else:
                # TODO: log invalid node name and set fail
                logger.error('wrong Node Name {} is specified in script'.format(node_name))
                raise AttributeError('Invalid nodename {}. Node name must be [LOCAL],\
                                     [GLOBAL] or a node defined in ENV class of properties.'.format(node_name))
            return TcDirective.SET_NODE, self.curr_node
        if line[0] == '!':
            return TcDirective.EXEC, line[1:].strip()
        if line[:3] == '*->':
            return TcDirective.BREAKPOINT, None
        else:
            line_parts: list = line.split(maxsplit=1)
            key = line_parts[0]
            if len(line_parts) == 2:  # line format 'cmd parameter(s)'
                param = line_parts[1].strip()
                # param = TcFileParser.P_LABEL.sub(self.fetch_label, param)
            else:
                param = None
            return key, param


class FixtureFileParse(TcFileParser):
    def __int__(self, file: str, tc_id: str, is_teardown: bool = False):
        super().__init__(file, tc_id)
        self.is_teardown = is_teardown

    def parse_setup_fixture(self) -> tuple:
        return self.parse_file()

    def parse_teardown_fixture(self) -> tuple:
        return self.parse_file(True)

    def parse_file(self, is_teardown=False) -> tuple:
        parse_sections = [TcSection.INIT, TcSection.TEARDOWN] if is_teardown else [TcSection.INIT, TcSection.SETUP]
        init_scr, setup_scr, test_scr, teardown_scr, tcid_list = super().parse_file(parse_sections)
        return [init_scr, teardown_scr] if is_teardown else [init_scr, setup_scr]


class TcDirective:
    SET_NODE = 10
    SET_LABEL = 11
    EXEC = 12
    SET_PARAMS = 13
    BREAKPOINT = 14


class DictNameSpace:
    def __init__(self, mapping_dict: dict):
        self.__dict__.update(mapping_dict)
