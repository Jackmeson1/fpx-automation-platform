from __future__ import annotations

from abc import ABC, abstractmethod

SSH_PW_LOGIN_OPTS = "-o'RSAAuthentication=no' -o'PubkeyAuthentication=no'"


class BaseConnector(ABC):
    """Abstract interface for CLI connection backends."""

    type: str = ""

    @abstractmethod
    def connect(self, node, timeout: int = -1) -> None:
        """Open the connection for the given node."""

    @abstractmethod
    def disconnect(self, node) -> None:
        """Close the connection for the given node."""


class TelnetConnector(BaseConnector):
    type = 'TELNET'

    def connect(self, node, timeout: int = -1) -> None:
        node.logged_in = False
        opt = [node.ip]
        if node.port:
            opt.append(str(node.port))
        node._spawn('telnet', opt)
        if not node.prompt(node.login_prompt_resp, timeout):
            raise Exception(f" Telnet to {node.ip} failed.")
        node.logged_in = True

    def disconnect(self, node) -> None:
        node.sendline('exit')
        index = node.expect(r'closed', r'(?i)there are stopped jobs')
        if index == 1:
            node.sendline('exit')
            node.expect('closed')
        node.logged_in = False
        node.close()


class SSHConnector(BaseConnector):
    type = 'SSH'

    def connect(self, node, timeout: int = -1) -> None:
        node.logged_in = False
        p_resp = {'yes/no.*\)': 'yes' + node.enter,
                  node.passwd_prompt: node.login_prompt_resp[node.passwd_prompt]}
        p_resp.update(node.prompt_resp)
        ssh_options = f'-l{node.user}'
        if getattr(node, 'force_password', False):
            ssh_options += ' ' + SSH_PW_LOGIN_OPTS
        if node.port:
            ssh_options += f' -p{node.port}'
        cmd = f"ssh {ssh_options} {node.ip}"
        node._spawn(cmd)
        if not node.prompt(p_resp, timeout):
            raise Exception(f"SSH to {node.ip} failed. ({cmd})")
        node.logged_in = True

    def disconnect(self, node) -> None:
        node.sendline('exit')
        index = node.expect([r'closed', r'(?i)there are stopped jobs'])
        if index == 1:
            node.sendline('exit')
            node.expect('closed')
        node.logged_in = False
        node.close()
