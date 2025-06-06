# the CLI system objects of ftnt products
import re

from SystemObject.cli_node import CliNode, CliDefault, ConnType


class FtntCli(CliNode):
    def __init__(self, ip: str, port: int = 0, user: str = 'admin', passwd: str = '', conn_type=ConnType.TELNET,
                 version: str = '', labels: dict = {}, timeout=CliDefault.timeout):
        super().__init__(ip, port, user, passwd, conn_type, labels=labels, timeout=timeout)
        self.version = version


class FosCli(FtntCli):
    P_LABEL = re.compile(r'\[\s*(\w+)\s*\]$')
    P_EDIT_ID = re.compile(r'edit\s+(\d+|"(.+)")')
    P_GET_ENTRY = re.compile(r'==\s*\[\s*(\w+)\s*\]')

    def __init__(self, ip: str, port: int = 0, user: str = 'admin', passwd: str = '', conn_type=ConnType.TELNET,
                 version: str = '', labels: dict = {}, timeout=CliDefault.timeout):
        super().__init__(ip, port, user, passwd, conn_type, version, labels) # , timeout=timeout)
        self.prompt_resp.update({'(y/n)': 'y', '-More--': '\033'})  # e.g. for purge command, down key for --More--
        self.sys_errs = ['Command fail', 'Unknown action']

    def _init_tc_func(self):
        super()._init_tc_func()
        self.tc_func.update({'edit': self.edit,
                             'edi': self.edit,
                             'ed': self.edit,
                             'DEL_EXCEPT': self.del_except,
                             'FIND_ENTRY': self.find_entry_id,
                             'GO_TO_ROOT': self.go_to_root
                             }
                            )

    def del_except(self, param: str):
        keep_list = param.split()
        for entry in self._get_entry_list():
            if entry not in keep_list:
                self.exec_cmd('del', entry)

    def go_to_root(self):
        self.sendline()
        self.expect(CliDefault.PROMPT)
        if b')' in self.before:
            self.sendline('abort')
            self.expect(CliDefault.PROMPT)
            self.go_to_root()

    def edit(self, param):
        m = FosCli.P_LABEL.match(param)
        if m:
            key = m.group(1)
            self.exec_cmd('edit 0')
            self.exec_cmd('show')
            m = FosCli.P_EDIT_ID.search(self.output)
            edit_num = m.group(2) or m.group(1) if m else '0'
            self.labels[key] = edit_num
        else:
            self.exec_cmd('edit', param)

    def _get_entry_list(self) -> list:
        self.exec_cmd('get')
        return FosCli.P_GET_ENTRY.findall(self.output)

    def show(self):
        self.exec_cmd('show')

    def show_full(self):
        self.exec_cmd('show full')

    def find_entry_id(self, param: str):
        param_list = FosCli.P_COMMA.split(param)
        key = param_list[0]
        search_strs = param_list[1:]
        self.show_full()
        m = FosCli.P_EDIT_ID.search(self.output)
        # entry_list = []
        edit_id = None
        while m and edit_id is None:
            edit_id = m.group(2) or m.group(1)
            start_loc = m.end()
            m = FosCli.P_EDIT_ID.search(self.output[start_loc:])
            end_loc = m.start() if m else None
            for s in search_strs:
                if re.search(s, self.output[start_loc:end_loc]) is None:
                    edit_id = None
                    break
            # if found:
            #     entry_list.append(edit_id)
        # if entry_list:
            # self.labels[key] = entry_list
        if edit_id:
            self.labels[key] = edit_id


class FpxCli(FosCli):
    def __init__(self, ip: str, port: int = 23, user: str = 'admin', passwd: str = '', conn_type=ConnType.TELNET,
                 version: str = '2.0', labels: dict = {}, timeout=CliDefault.timeout):
        super().__init__(ip, port, user, passwd, conn_type, version, labels, timeout=timeout)


class FgtCli(FosCli):
    def __init__(self, ip: str, port: int = 23, user: str = 'admin', passwd: str = '', conn_type=ConnType.TELNET,
                 version: str = '6.4', labels: dict = {}, timeout=CliDefault.timeout):
        super().__init__(ip, port, user, passwd, conn_type, version, labels, timeout=timeout)

