import time
import re
import argparse

from SystemTestCase.SysTestCase import SysTestCase, SysTcFail
from SystemTestCase.SysTestCase import TcFailAction

from Analyzer.analyzer import TextAnalyzer
from SystemObject.sys_obj import SysObj
from pexpect import spawn
from pexpect import TIMEOUT
from pexpect import EOF
from monitor.pysys_log import pysys_logger


class ConnType:
    TELNET: str = 'TELNET'
    SSH: str = 'SSH'
    HTTP: str = 'HTTP'
    HTTPS: str = 'HTTPS'


class CliDefault:
    PROMPT = r'[$#]\s*$'
    host = 'localhost'
    user = 'admin'
    passwd = ''
    ENTER = '\n'
    CR = '\r'
    terminal_type = 'ansi'
    timeout = 30
    attempts = 10
    wait_time = 3  # wait time between attempts
    login_prompt = r'(?i)login:'
    passwd_prompt = r'(?i)password:'
    SSH_PW_LOGIN_OPTS = "-o'RSAAuthentication=no' -o'PubkeyAuthentication=no'"
    errors = ['command not found']

class CliShell:
    BASH = 'bash'
    LOCAL = 'bash'
    SSH_REMOTE = 'ssh'
    FTP = 'ftp'
    LFTP = 'lftp'
    TELNET = 'telnet'


class CmdParam:
    EXPECT = 'expect'
    EXPECT_ANY = 'expect_any'
    ERROR = 'error'
    WARNING = 'warning'
    TIMEOUT = 'timeout'
    EXPECT_TIMEOUT = 'expect_timeout'
    ADD_ENTER = 'addenter'
    PROMPT = 'prompt'
    ADD_PROMPT = 'add_prompt'
    KEEP_PARAM = 'keep_param'
    FAIL_ACTION = 'fail_action'
    HOSTNAME = 'hostname'
    USER = 'user'
    PASSWD = 'password'
    FW_USER = 'fw_user'
    FW_PASSWD = 'fw_passwd'
    WAIT = 'wait'


class CliNode(spawn, SysObj):
    P_PARAMS_QUOTED = re.compile(r'("[^"]*"|[^\s"]+)')

    def __init__(self, ip='localhost', port=0, user=CliDefault.user, passwd=CliDefault.passwd, hostname='None',
                 conn_type=ConnType.TELNET, labels: dict = {}, enter_str=CliDefault.ENTER, add_enter=True,
                 prompt_resp={}, login_prompt=CliDefault.login_prompt, passwd_prompt=CliDefault.passwd_prompt,
                 is_console=False, terminal_type=CliDefault.terminal_type,
                 timeout=CliDefault.timeout, attempts=CliDefault.attempts, wait_time=CliDefault.wait_time):
        # def __init__(self, host='localhost', user='admin', passwd='', port = 0, enter_str = '\n',
        #              prompt_resp=None, login_prompt='(?i)login:', passwd_prompt='(?i)password:',
        #              isconsole=False, connType='Telnet', terminal_type="ansi", timeout=20):
        SysObj.__init__(self, conn_type, ip, port, user, passwd, hostname, labels)
        spawn.__init__(self, None)

        # super().__init__(None, ip=ip, port=port, user=user, passwd=passwd, labels=labels)
        # super(SysObj, self).__init__(ip=ip, port=port, user=user, passwd=passwd, labels=labels)
        # super(spawn, self).__init__()
        self.prompt_resp = self.init_prompt_resp = prompt_resp or {CliDefault.PROMPT: None}
        # if prompt_resp:
        #     self.prompt_resp: dict = prompt_resp
        # else:
        #     self.prompt_resp: dict = dict.fromkeys([CliDefault.PROMPT])
        # self.encoding='utf-8'
        self.prompts = list(self.prompt_resp.keys())
        self.shell = CliShell.BASH
        self.enter = enter_str
        self.cr = CliDefault.CR
        self.add_enter: bool = add_enter
        self.login_prompt = login_prompt
        self.passwd_prompt = passwd_prompt
        #TODO -- init?
        # self.login_prompt_resp: dict = dict.fromkeys([login_prompt, passwd_prompt])
        self.login_prompt_resp: dict = {login_prompt: user + self.cr, passwd_prompt: passwd + self.cr + self.enter}
        # self.user = user
        # self.passwd = passwd
        self.terminal_type = terminal_type
        self.is_console = is_console
        self.timeout = timeout
        self.attempts = attempts
        self.wait_time = wait_time
        # assert hasattr(ConnType, conn_type)
        # self.conn_type: str = conn_type
        self.logged_in: bool = False
        self.force_password: bool = False
        self.keywords: dict = {}  # command keywords -> functions, instance member for the sack of inheritance
        # self.cmd_params = None  # parseargs object containing parameters for command to execute.
        # self.parm_parser = self._init_parser()
        self.output = ''
        self.sys_errs = CliDefault.errors
        self.tc: SysTestCase = None
        # self.intf_inet = None
        # self.intf_client = None
        # self.intf_server = None
        # self.intf_mgmt = None
        # self.ip_init = None
        # self.ip_client = None
        # self.ip_server = None
        # self.ip_mgmt = None

    def ssh_init_conf(self):
        self.SSH_OPTS = CliDefault.SSH_OPTS
        #TODO more options of ssh connection

    def prompt(self, prompt_resp: dict = None, timeout=-1, merge_prompt=True, refresh_result=True) -> bool:
        # assert isinstance(prompt_resp, dict) or prompt_resp is None
        #TODO to change the prompt result to multiple value (found, failed, timeout, EOF)
        if refresh_result:
            self.output = ''
        if not prompt_resp:
            p_re = self.prompt_resp
        elif merge_prompt:  # do NOT update the self.prompt_resp or prompt_resp! construct a new dict
            p_re = {}
            p_re.update(prompt_resp)
            p_re.update(self.prompt_resp)
        else:  # There should be at least one escape prompt or timeout
            p_re = prompt_resp
        try:
            i = self.expect(list(p_re.keys()), timeout)
            # TODO: may try to avoid converting bytes to string for better performance
            # self.output += str(self.before + self.after, 'utf-8')
            # self.output += str(self.before) + str(self.after)
            self.output += (self.before + self.after).decode()
            resp = list(p_re.values())[i]
            if resp:  # auto response to the matched prompt, not command end, no enter added by default
                self.send(resp)
                time.sleep(0.5)
                return self.prompt(p_re, timeout, False, False)
            return True
        except TIMEOUT:
            # terminate when hang, to allow next command to be sent properly
            # pysys_logger.error('Unexpected timeout when CLI waiting for prompt', exc_info=True)
            self.sendcontrol('c')
            self.prompt(refresh_result=False)
            return False
        except EOF:
            # self.sendcontrol('c')
            # self.prompt(refresh_result=False)
            pysys_logger.warning('Unexpected CLI exit when waiting for prompt', exc_info=True)
            self.proc_err('Unexpected CLI exit when waiting for prompt', TcFailAction.STOP)
        # else:
            # self.output += str(self.before + self.after, 'utf-8')
            # resp = list(p_re.values())[i]
            # if resp:  # auto response to the matched prompt, not command end, not enter added by default
            #     self.send(resp)
            #     return self.prompt(p_re, timeout, False, False, retries)
            # return True

    def login(self, timeout=-1) -> None:
        try:
            if self.conn_type == ConnType.SSH:
                self.ssh_login(timeout)
            elif self.conn_type == ConnType.TELNET:
                self.telnet_login(timeout)
            else:
                raise Exception('Connection types other than SSH or Telnet are yet to support')
        except Exception as e:
            pysys_logger.error('login failed on {}: {}'.format(self.ip, e), exc_info=True)
            self.logged_in = False
            raise SysTcFail(str(e), action=TcFailAction.NEXT)

    def ssh_login(self, timeout=-1) -> None:
        self.logged_in = False
        # p_resp = {'continue connecting': 'yes' + self.enter,
        p_resp = {'yes/no.*\)': 'yes' + self.enter,
                  self.passwd_prompt: self.login_prompt_resp[self.passwd_prompt]}
        p_resp.update(self.prompt_resp)
        ssh_options = '-l{}'.format(self.user)
        if self.force_password:
            ssh_options = ssh_options + ' ' + CliDefault.SSH_PW_LOGIN_OPTS
        if self.port != 0:
            ssh_options = ssh_options + ' -p{}'.format(str(self.port))
        cmd = "ssh %s %s" % (ssh_options, self.ip)
        try:
            self._spawn(cmd)
            if not self.prompt(p_resp, timeout):  # includes timout as failure
                raise Exception("SSH to {} failed. ({})".format(self.ip, cmd))
            self.logged_in = True
        except Exception:
            self.logged_in = False
            raise

    def telnet_login(self, timeout=-1) -> None:
        self.logged_in = False
        opt = [self.ip]
        if self.port != 0:
            opt.append(str(self.port))
        try:
            self._spawn('telnet', opt)
            if not self.prompt(self.login_prompt_resp, timeout):
                raise Exception(" Telnet to {} failed.".format(self.ip))
            self.logged_in = True
        except Exception:
            self.logged_in = False
            raise

    def logout(self) -> None:
        if self.conn_type == ConnType.TELNET:
            self.telnet_logout()
        elif self.conn_type == ConnType.SSH:
            self.ssh_logout()
        else:
            raise Exception('Only SSH and Telnet are support for CLI @ {}'.format(self.ip))

    def telnet_logout(self) -> None:
        """This sends exit to the remote shell. If there are stopped jobs then
        this automatically sends exit twice. """

        self.sendline("exit")
        # index = self.expect([EOF, "(?i)there are stopped jobs"])
        index = self.expect(r'closed', r'(?i)there are stopped jobs')
        if index == 1:
            self.sendline("exit")
            self.expect('closed')
        self.logged_in = False
        self.close()

    def ssh_logout(self) -> None:
        """This sends exit to the remote shell. If there are stopped jobs then
        this automatically sends exit twice. """

        self.sendline("exit")
        # index = self.expect([EOF, "(?i)there are stopped jobs"])
        index = self.expect([r'closed', r'(?i)there are stopped jobs'])
        if index == 1:
            self.sendline("exit")
            self.expect('closed')
        self.logged_in = False
        self.close()

    # def _init_parser(self) -> argparse.ArgumentParser:
    #     parser = argparse.ArgumentParser('Set param for the command to execute.')
    #     parser.add_argument('-t', '--timeout', type=int, default=-1)
    #     parser.add_argument('--addenter', action='store_true', default=True)
    #     parser.add_argument('-v', '--verbose', action='store_true', default=False)
    #     parser.add_argument('-p', '--prompt', default=None)
    #     parser.add_argument('--addpmt', action='store_true', default=False)
    #     parser.add_argument('-e', '--expect', nargs='*', default=None)
    #     parser.add_argument('-r', '--errors', nargs='*', default=None)
    #     parser.add_argument('-w', '--warnings', nargs='*', default=None)
    #     return parser

    # Define the TC command keywords to system object function mapping
    def _init_tc_func(self):
        super()._init_tc_func()
        self.tc_func.update({'SET_PARAMS': self.set_params,
                             'SET_PROMPT': self.set_prompt,
                             'ADD_PROMPT': self.add_prompt,
                             'RRSTORE_PROMPT': self.restore_prompt,
                             'EXPECT': self.tc_expect,
                             'EXPECT_ANY': self.tc_expect_any,
                             'REPORT': self.tc_report,
                            #  'LOG': self.tc_log,
                             'CTRL': self.tc_ctrl,
                             'ENTER': self.tc_enter,
                             'CTRL_C': self.tc_ctrl_c,
                             'SEND': self.send,
                             'SENDLINE': self.sendline,
                             # fortiauto functions
                             'expect': self.arg_expect,
                             'setvar': self.setvar,
                             'compare': self.compare
                             })

    def parse_prompt(self, prompt:str) -> dict:
        if prompt:
            try:
                if re.match('{.+}', prompt):
                    return eval(prompt)
                elif re.match('\[.+\]', prompt):
                    return dict.fromkeys(eval(prompt))
                else:
                    return {prompt: None}
            except Exception as e:
                self.proc_err('Invalid PROMPT format, must be a dict, list or string...' + str(e))
        else:
            return None

    def set_prompt(self, prompt:str):
        # self.prompt_resp = self.parse_prompt(prompt)
        # self.prompts = list(prompt.keys())
        self._set_prompt(self.parse_prompt(prompt))

    def _set_prompt(self, p_resp: dict):
        self.prompt_resp = p_resp
        self.prompts = list(self.prompt_resp.keys())

    def add_prompt(self, prompt:str):
        self._add_prompt(self.parse_prompt(prompt))

    def _add_prompt(self, p_resp:dict):
        self.prompt_resp.update(self.parse_prompt(prompt))
        self.prompts += list(self.prompt_resp.keys())

    def restore_prompt(self):
        self.prompt_resp = self.init_prompt_resp
        self.prompts = list(self.prompt_resp.keys())

    def tc_ctrl_c(self):
        self.tc_ctrl('c')
        # self.tc_log_debug('ctrl-c output: {}'.format(self.output))

    def tc_enter(self):
        self.exec_cmd('')

    def tc_ctrl(self, char: str = ''):
        if len(char) != 1:
            raise AttributeError('"{}" should be a char for CTRL + CHAR command'.format(char))
        self.exec_cmd(char, is_ctrl=True)

    def tc_report(self, report_msg: str):
        self._tc_log(report_msg, 'REPORT')

    def tc_log(self, report_msg: str):
        self._tc_log(report_msg, 'LOG')

    def _tc_log(self, msg: str, level: str):
        if level == 'LOG':
            head_info = '<TC LOG>:'
        elif level == 'REPORT':
            head_info = '<TC REPORT>:'
        elif level == 'ERROR':
            head_info = '<ERROR>:'
        elif level == 'WARNING':
            head_info = '<WARNING>:'
        elif level == 'INFO':
            head_info = '<INFO>:'
        elif level == 'DEBUG':
            head_info = '<DEBUG>:'
        else:
            pysys_logger.error('LOG TYPE "{}" is not supported'.format(level))
        self.logfile.write(bytes('\n' + head_info + ' --- {}\n'.format(msg), 'utf-8'))
        self.logfile.flush()

    def tc_log_warning(self, msg: str):
        self._tc_log(msg, 'WARNING')

    def tc_log_debug(self, msg: str):
        self._tc_log(msg, 'DEBUG')

    def tc_log_info(self, msg: str):
        self._tc_log(msg, 'INFO')

    def tc_log_err(self, msg: str):
        self._tc_log(msg, 'ERROR')

    # def setargs(self, params: str):
    #     self.cmd_params = self.parm_parser.parse_args(params.split())

    def proc_err(self, msg: str, action: TcFailAction = None):
        # self.cmd_params = {}
        self.tc_log_err(msg)
        raise SysTcFail(msg, action=action)

    def tc_expect(self, expect_str: str, flag=re.M):
        for to_find in CliNode.P_COMMA.split(expect_str):
            if not re.search(to_find.strip(), self.output, flag):
                info_text = '"{} "is not found in the CLI output'.format(to_find)
                self.proc_err(ino_text)
        self.tc_log('EXPECT: "{}" is found successfully'.format(expect_str))

    def tc_expect_any(self, expect_str: str, flag=re.M):
        found = False
        expect_list = re.split(r'(?<!\\),', expect_str)
        for to_find in expect_list:
            if re.search(to_find.strip(), self.output, flag):
                found = True
                break
        if found:
            self.tc_log('EXPECT_ANY: Successfully found the an expected text form "{}"'.format(expect_list))
        else:
            info_text = 'EXPECT_ANY: None of the text from "{}" is found in the CLI output'.format(expect_list)
            self.proc_err(ino_text)

    def setvar(self, param: str):
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--pattern', required=True)
        parser.add_argument('-to', '--to_var', required=True)
        arg_list = self.P_PARAMS_QUOTED.split(param)[1::2]
        args = parser.parse_args(arg_list)

        value = ''
        m = re.search(args.pattern, self.output)
        if m:
            self.labels[args.to_var] = m.group(1) or m.group()
        else:
            raise SysTcFail('"{}" is not found in current output'.format(args.pattern))

    def compare(self, param: str):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v1', '--var1', required=True)
        parser.add_argument('-v2', '--var2', required=True)
        parser.add_argument('-for', '--for_tc_id')
        parser.add_argument('-fail', '--fail_on', choices=['match', 'unmatch'], default='unmatch')
        arg_list = self.P_PARAMS_QUOTED.split(param)[1::2]
        args = parser.parse_args(arg_list)

        succ = False
        v1 = self.labels.get(args.var1)
        v2 = self.labels.get(args.var2)
        if v1 and v2:
            if v1 == v2:
                if args.fail_on == 'unmatch':
                    succ = True
            elif args.fail_on == 'match':
                succ = True
        if succ:
            self.tc_log_info('Compare {} == {}'.format(args.var1, args.var2))
        else:
            raise SysTcFail('"{}" is not found in current output'.format(args.pattern))


    def arg_expect(self, expect_str: str, flag=re.M):
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--tofinds', required=True, action='append')
        parser.add_argument('-for', '--for_tc_id')
        parser.add_argument('-fail', '--fail_on', choices=['match', 'unmatch'], default='unmatch')
        parser.add_argument('-a', '--action', type=TcFailAction, choices=list(TcFailAction))
        parser.add_argument('-t', '--timeout', type=int, default=0)
        # parser.add_argument('-fail_match', '--fail_match', action='store_true')
        parser.add_argument('-any', '--match_any', action='store_true')
        arg_list = self.P_PARAMS_QUOTED.split(expect_str)[1::2]
        args = parser.parse_args(arg_list)

        tofinds = [exp_text.strip('(?<!\\)"') for exp_text in args.tofinds]
        fail_match = args.fail_on == 'match'
        analyzer = TextAnalyzer(self.output, tofinds, unexpected=fail_match, find_any=args.match_any)
        if analyzer.analyze():
            self.tc_log_info('EXPECT: "{}" is found successfully'.format(expect_str))
        elif args.timeout:
            errs = None
            if fail_match:
                errs = args.tofinds
                tofinds = None
            self._exec_cmd('', timeout=args.timeout, tofinds=tofinds, tc_errs=errs, any_matches=args.match_any)
        else:
            self.proc_err('EXPECT: "{}" is not found in the output'.format(expect_str), action=args.action)


        # found_any = False
        # missed_any = False
        # matched_str: str = expect_str
        # for to_find in args.tofinds:
        #     if re.search(to_find.strip('[ "]'), self.output, flag):
        #         if args.match_any:
        #             found_any = True
        #             matched_str = to_find
        #             break
        #     else:
        #         if not args.match_any:
        #             missed_any = True
        #             break
        #     # else:
        #     #     info_text = '"{} "is not found in the CLI output'.format(to_find)
        #     #     self.tc_log_err(info_text)
        #     #     raise SysTcFail(info_text)
        #     # self.tc_log('EXPECT: "{}" is found successfully'.format(expect_str))
        # # if found:
        # info_text = '"{} "is found in the CLI output'.format(matched_str)
        # fail_match: bool = args.fail_match or args.fail == 'match'
        # tc_pass = not fail_match
        # if missed_any or args.match_any and not found_any:
        #     info_text = '"{} "is NOT matched in the CLI output'.format(matched_str)
        #     tc_pass = fail_match
        # if tc_pass:
        #     info_text = 'EXPECT - Failed: ' + info_text
        #     self.tc_log(info_text)
        # else:
        #     info_text = 'EXPECT - Successful: ' + info_text
        #     self.tc_log_err(info_text)
        #     raise SysTcFail(info_text, args.action)

    # def exec_ctrl(self, char: str):
    #     assert len(char) == 1
    #     self._exec_cmd(char, )

    def exec_cmd(self, cmd, param=None, cmd_enter=True, is_ctrl=False, wait_for_prompt=True):
        if param:
            cmd += ' ' + param
        if self.cmd_params:
            timeout = self.cmd_params.get(CmdParam.TIMEOUT)
            if not timeout:
                # timeout = -1
                timeout = self.timeout
            else:
                assert type(timeout) is str
                timeout = int(timeout)
            add_enter: bool = True if self.cmd_params.get(CmdParam.ADD_ENTER) else cmd_enter
            # prompt = self.cmd_params.get(CmdParam.PROMPT)
            prompt = self.parse_prompt(self.cmd_params.get(CmdParam.PROMPT))
            merge_prompt: bool = True if self.cmd_params.get(CmdParam.ADD_PROMPT) else False
            tofinds = self.cmd_params.get(CmdParam.EXPECT)
            any_matches = self.cmd_params.get(CmdParam.EXPECT_ANY)
            errs = self.cmd_params.get(CmdParam.ERROR)
            warnings = self.cmd_params.get(CmdParam.WARNING)
            expect_timeout = self.cmd_params.get(CmdParam.EXPECT_TIMEOUT) == 'true'
            fail_action = self.cmd_params.get(CmdParam.FAIL_ACTION)
            wait_for_prompt = self.cmd_params.get(CmdParam.WAIT) != 'false' and self.cmd_params.get(CmdParam.WAIT) != 'FALSE'
        else:
            timeout = self.timeout
            add_enter: bool = self.add_enter
            prompt = None
            merge_prompt: bool = False
            tofinds = any_matches = errs = warnings = None
            expect_timeout = False
            fail_action = None

        try:
            self._exec_cmd(cmd, timeout, add_enter, prompt, merge_prompt,
                           is_ctrl, wait_for_prompt, fail_action,
                           tofinds, any_matches, errs, warnings, expect_timeout)
        finally:  # Clear tc command parameters after command execution
            self.cmd_params = {}

    def _exec_cmd(self, cmd: str, timeout: int = -1, add_enter: bool = True,
                  prompt_resp: dict = None, add_prompt: bool = False,
                  is_ctrl=False, wait_for_prompt=True, fail_action: str = None,
                  tofinds=None, any_matches=None, tc_errs=None, warnings=None, expect_timeout=False):
        if is_ctrl:
            assert len(cmd) == 1
            self.sendcontrol(cmd)
            cmd_info = 'CTRL-' + cmd.upper()
        elif add_enter:
            self.sendline(cmd)
            # cmd_info = cmd if cmd else 'Enter line'
            cmd_info = cmd or 'Enter Line'
        elif cmd:
            self.send(cmd)
            cmd_info = cmd
        else:
            err_info = 'Command to send must not be empty.'
            self.tc_log_err(err_info)
            raise AttributeError(err_info)

        # if tc_errs and type(tc_errs) is str:  # single err in the list, input as string
        #     tc_errs = [tc_errs]
        # elif type(tc_errs) is not list:
        #     tc_errs = None
        # errs = tc_errs if not self.sys_errs else self.sys_errs + tc_errs if tc_errs else self.sys_errs

        if wait_for_prompt:
            # expect prompt and fails the unexpected TIMEOUT results
            if self.prompt(prompt_resp, timeout, add_prompt):
                if expect_timeout: # Tc fails and raise
                    msg_text = 'Expected TIMEOUT was not observed when executing "{}"'.format(cmd_info)
                    self.proc_err(msg_text, fail_action)
            else: # prompt false means timeout
                if expect_timeout:
                    self.tc_log_info('Expected TIMEOUT was observed when executing "{}"'.format(cmd_info))
                else: # Tc fails and raise
                    msg_text = 'Unexpected TIMED OUT when executing "{}"'.format(cmd_info)
                    self.proc_err(msg_text, fail_action)
            # Analyze result when prompt sucesss (no error raise)
            self.analyze(fail_action, tofinds, any_matches, tc_errs, warnings, cmd_info=cmd_info)

            # if fail_action:
            #     fail_action = TcFailAction(fail_action)
            # if tofinds:
            #     analyzer = TextAnalyzer(self.output, tofinds, find_any=False)
            #     if not analyzer.analyze():
            #         msg_text = 'Expected text "{}" was not found when executing "{}"'.format(analyzer.found_texts[0], cmd_info)
            #         self.proc_err(msg_text, fail_action)
            #     else:
            #         self.tc_log_info('Expected text "{}" was found when executing "{}"'.format(tofinds, cmd_info))
            # if any_matches:
            #     analyzer = TextAnalyzer(self.output, any_matches, find_any=True)
            #     if not analyzer.analyze():
            #         msg_text = 'None of the expected text "{}" was not found when executing "{}"'.format(any_matches, cmd_info)
            #         self.proc_err(msg_text, fail_action)
            # if errs:
            #     analyzer = TextAnalyzer(self.output, errs, unexpected=True, find_any=True)
            #     if not analyzer.analyze():
            #         msg_text = 'Error text "{}" was found when executing "{}"'.format(analyzer.found_texts[0], cmd_info)
            #         self.proc_err(msg_text, fail_action)
            # if warnings:
            #     analyzer = TextAnalyzer(self.output, warnings, find_any=False, unexpected=True)
            #     analyzer.analyze()
            #     if analyzer.found_texts:
            #         for warn in analyzer.found_texts:
            #             self.tc_log_warning('"{}" was found when executing "{}".'.format(warn, cmd_info))

    def analyze(self, fail_action=None, tofinds=None, any_matches=None, tc_errs=None, warnings=None, cmd_info=''):
            if fail_action:
                fail_action = TcFailAction(fail_action)
            if tofinds:
                analyzer = TextAnalyzer(self.output, tofinds, find_any=False)
                if not analyzer.analyze():
                    msg_text = 'Expected text "{}" was not found when executing "{}"'.format(analyzer.found_texts[0], cmd_info)
                    self.proc_err(msg_text, fail_action)
                else:
                    self.tc_log_info('Expected text "{}" was found when executing "{}"'.format(tofinds, cmd_info))
            if any_matches:
                analyzer = TextAnalyzer(self.output, any_matches, find_any=True)
                if not analyzer.analyze():
                    msg_text = 'None of the expected text "{}" was not found when executing "{}"'.format(any_matches, cmd_info)
                    self.proc_err(msg_text, fail_action)
            if tc_errs and type(tc_errs) is str:  # single err in the list, input as string
                tc_errs = [tc_errs]
            elif type(tc_errs) is not list:
                tc_errs = None
            errs = tc_errs if not self.sys_errs else self.sys_errs + tc_errs if tc_errs else self.sys_errs
            if errs:
                analyzer = TextAnalyzer(self.output, errs, unexpected=True, find_any=True)
                if not analyzer.analyze():
                    msg_text = 'Error text "{}" was found when executing "{}"'.format(analyzer.found_texts[0], cmd_info)
                    self.proc_err(msg_text, fail_action)
            if warnings:
                analyzer = TextAnalyzer(self.output, warnings, find_any=False, unexpected=True)
                analyzer.analyze()
                if analyzer.found_texts:
                    for warn in analyzer.found_texts:
                        self.tc_log_warning('"{}" was found when executing "{}".'.format(warn, cmd_info))

class WorkStationCli(CliNode):
    def __init__(self, ip='localhost',
                 port: int = 0,
                 user='admin',
                 passwd='',
                 hostname='None',
                 timeout=CliDefault.timeout,
                 conn_type=ConnType.TELNET,
                 is_console=False,
                 prompt_resp=None,
                 labels: dict = {}):
        super().__init__(ip, port, user, passwd, hostname, conn_type,
                         is_console=is_console,
                         prompt_resp=prompt_resp,
                         labels=labels,
                         timeout=timeout)


class LinuxType:
    UBUNTU = 'UBUNTU'
    CENTOS = 'CENTOS'
    OTHERS = 'OTHERS'


class LinuxCli(WorkStationCli):
    def __init__(self, ip='localhost',
                 port: int = 0,
                 user='root',
                 passwd='',
                 hostname='None',
                 conn_type=ConnType.SSH,
                 timeout=CliDefault.timeout,
                 is_console=False,
                 prompt_resp=None,
                 linux_type=LinuxType.UBUNTU,
                 labels: dict = {}):
        super().__init__(ip, port, user, passwd, hostname, conn_type=conn_type,
                         prompt_resp=prompt_resp, timeout=timeout,
                         is_console=is_console, labels=labels)
        self.linux_type = linux_type

    def su(self):
        pysys_logger.error('su function is implemented in sub class of LinuxCli based on the OS type')
        exit(-1)

    def _init_tc_func(self):
        super()._init_tc_func()
        self.tc_func.update({
            'su': self.su,
            'ssh': self.ssh,
            'ftp': self.ftp,
            'ftp-ssl': self.ftps,
            'lftp': self.lftp,
            # 'nslookup': self.nslookup,
            'bye': self.exit,
            'exit': self.exit
        })

    def exit(self):
        if self.shell != CliShell.BASH:
            self.restore_prompt()
            self.shell = CliShell.BASH
        self.exec_cmd('exit')

    def ssh(self, param: str):
        cmd_params: dict = self.cmd_params
        self.cmd_params={}
        cmd_str = 'ssh ' + param
        pw = cmd_params.get(CmdParam.PASSWD) or ''
        # hostname = cmd_params.get(CmdParam.HOSTNAME)
        username = cmd_params.get(CmdParam.USER)
        expect_timeout = cmd_params.get(CmdParam.EXPECT_TIMEOUT) == 'true'
        # prompt = hostname + '.*[$#]' if hostname else CliDefault.PROMPT
        prompt = username + '.*[$#]' if username else CliDefault.PROMPT
        # p_resp = {prompt: None, 'ssh-keygen.*$': None, 'yes/no.*\)': 'yes' + self.enter, CliDefault.passwd_prompt: pw + self.enter}
        p_resp = {prompt: None, 'yes/no.*\)': 'yes' + self.enter, CliDefault.passwd_prompt: pw + self.enter}
        # p_resp.update(self.prompt_resp)

        for i in range(4): # limit ssh_keygen in 3 times
            self._exec_cmd(cmd_str, timeout=self.timeout, add_prompt=True, prompt_resp=p_resp, expect_timeout=expect_timeout)
            self.tc_log_debug('Type of self.output is: ' + str(type(self.output)))
            # m = re.search('ssh\-keygen[^\\]*', self.output)
            m = re.search('ssh\-keygen[^\r]*', self.output)
            if m:
                self.tc_log_debug('current self.output = ' + self.output)
                self.tc_log_debug('ssl-keygen matched group is: ' + m.group())
                self._exec_cmd(m.group(), prompt_resp=self.prompt_resp)
                # self._exec_cmd('')
            else:
                self.analyze(fail_action = cmd_params.get(CmdParam.FAIL_ACTION),
                             tofinds = cmd_params.get(CmdParam.EXPECT),
                             any_matches = cmd_params.get(CmdParam.EXPECT_ANY),
                             tc_errs = cmd_params.get(CmdParam.ERROR),
                             warnings = cmd_params.get(CmdParam.WARNING),
                             cmd_info=cmd_str)
                # self._set_prompt({prompt: None})
                # self.shell = CliShell.SSH_REMOTE
                break
        if m:
            self.proc_err('ssh_keygen fails with {}'.format(m.group()))
        else:
            self._set_prompt({prompt: None})
            self.shell = CliShell.SSH_REMOTE

    def ftp(self, param:str):
        self._ftp('ftp ', param)

    def ftps(self, param:str):
        self._ftp('ftp-ssl ', param)

    def _ftp(self, cmd:str, param:str):
        fail_action = self.cmd_params.get(CmdParam.FAIL_ACTION)
        cmd_params = self.cmd_params
        # cmd_str = 'ftp ' + param
        cmd_str = cmd + param
        user = cmd_params.get(CmdParam.USER) or 'anonymous'
        # if user == 'anonymous':
        #     pw = 'any'
        # else:
        #     pw = cmd_params.get(CmdParam.PASSWD) or ''
        pw = cmd_params.get(CmdParam.PASSWD) or ''
        fw_user = cmd_params.get(CmdParam.FW_USER)
        fw_pw = cmd_params.get(CmdParam.FW_PASSWD)
        if fw_user and fw_pw:
            user = fw_user + ':' + fw_pw + ':' + user
        # hostname = cmd_params.get(CmdParam.HOSTNAME)
        expect_timeout = cmd_params.get(CmdParam.EXPECT_TIMEOUT) == 'true'
        ftp_prompt = 'ftp>'
        p_resp = {ftp_prompt: None, 'Name.*\):': user + self.enter, 'Password:': pw + self.enter}
        fail_action = cmd_params.get(CmdParam.FAIL_ACTION)
        self._exec_cmd(cmd_str, timeout=self.timeout, add_prompt=True, prompt_resp=p_resp, expect_timeout=expect_timeout)

        # m = re.search('^\s*230', self.output)  # 230 Login seccessful
        # if re.search('^\s*230', self.output, re.MULTILINE):  # 230 Login seccessful
        if re.search(ftp_prompt, self.output, re.MULTILINE):
            self._set_prompt({ftp_prompt: None})
            self.shell = CliShell.FTP
            self.analyze(fail_action = fail_action,
                        tofinds = cmd_params.get(CmdParam.EXPECT),
                        any_matches = cmd_params.get(CmdParam.EXPECT_ANY),
                        tc_errs = cmd_params.get(CmdParam.ERROR),
                        warnings = cmd_params.get(CmdParam.WARNING),
                        cmd_info=cmd_str)
        else:
            # m = re.search(ftp_prompt, self.output) # fails to login but gets into ftp shell
            if re.search(ftp_prompt, self.output):  # fails to login but gets into ftp shell
                self.sendline('exit')
            self.proc_err('Fails to login ftp server: ' + cmd_str, action = fail_action)
        self.cmd_params = {}

    def lftp(self, param:str):
        pass

    # def nslookup(self, param:str):
        pass


class CentosCli(LinuxCli):
    def __init__(self, ip='localhost',
                 port: int = 0,
                 user='root',
                 passwd='',
                 hostname='None',
                 conn_type=ConnType.SSH,
                 timeout=CliDefault.timeout,
                 is_console=False,
                 labels: dict = {}):
        super().__init__(ip, port, user, passwd, hostname, conn_type=conn_type,
                         prompt_resp={r'\[{}@.*[$#]\s*$'.format(user): None},
                         timeout=timeout, is_console=is_console,
                         linux_type=LinuxType.CENTOS, labels=labels)

    def su(self):
        root_prompt = r'\[root@.*[$#]\s*$'
        root_p_re = {root_prompt: None}
        if self.prompt_resp.get(root_prompt) is None:
            # self.prompt_resp.update(root_p_re)
            root_p_re.update(self.prompt_resp)
            self.prompt_resp = self.init_prompt_resp = root_p_re        #  put root prompt in the front
        self.prompt_resp.update()
        self._exec_cmd('su', add_prompt=True, prompt_resp={r'Password:': self.passwd + '\n'})


class UbuntuCli(LinuxCli):
    def __init__(self, ip='localhost',
                 port: int = 0,
                 user='root',
                 passwd='',
                 hostname='None',
                 conn_type=ConnType.SSH,
                 timeout=CliDefault.timeout,
                 is_console=False,
                 labels: dict = {}):
        super().__init__(ip, port, user, passwd, hostname,
                         conn_type=conn_type,
                         prompt_resp={r'{}@.*[$#]\s*$'.format(user): None},
                         timeout=timeout, is_console=is_console,
                         linux_type=LinuxType.UBUNTU, labels=labels)

    def su(self):
        root_prompt = r'root@.*[$#]\s*$'
        root_p_re = {root_prompt: None}
        if self.prompt_resp.get(root_prompt) is None:
            # self.prompt_resp.update(root_p_re)
            root_p_re.update(self.prompt_resp)
            self.prompt_resp = self.init_prompt_resp = root_p_re        #  put root prompt in the front
        self._exec_cmd('sudo -s', prompt_resp={r'password.*:': self.passwd + '\n'}, add_prompt=True)
