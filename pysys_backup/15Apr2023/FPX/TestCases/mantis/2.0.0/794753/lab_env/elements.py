"""
Define the Customer Lab elements
"""
from SystemObject.gui_node import BrowserType
from ftnt_nodes import ftnt_cli, ftnt_gui
from SystemObject import cli_node, gui_node

LOCALHOST = cli_node.UbuntuCli(
    ip='localhost',
    port=22,
    passwd='leo',
    user='leo'
)

CTRL_SERVER_116 = cli_node.UbuntuCli(
    ip='172.18.29.116',
    port=22,
    passwd='leo',
    user='leo'
)

Linux111 = cli_node.UbuntuCli(
    ip='172.18.29.111',
    conn_type=cli_node.ConnType.SSH,
    user='leonardo',
    passwd='leonardo',
    timeout=40,
    labels={
        'FQDN': 'server111.ftnt.net',
        'IF_CLIENT': 'eth1',
        'IF_INET': 'eth0',
        'IF_SERVER': 'eth2',
        'IF_MGMT': 'eth3',
        'IP_INET': '172.18.29.111',
        'IP_CLIENT': '10.160.0.111',
        'IP_SERVER': '10.170.0.111',
        'IP_MGMT': '10.150.0.111',
        'OVERSIZE_LIMIT': '30'
    }
)

Linux117 = cli_node.CentosCli(
    ip='172.18.29.117',
    conn_type=cli_node.ConnType.SSH,
    user='root',
    passwd='fortinet',
    timeout=40)
Linux117.FQDN = 'server117.ftnt.net'
Linux117.IF_CLIENT = 'eth1'
Linux117.IF_INET = 'eth0'
Linux117.IF_SERVER = 'eth2'
Linux117.IF_MGMT = 'eth3'
Linux117.IP_INET = '172.18.29.117'
Linux117.IP_CLIENT = '10.160.0.117'
Linux117.IP_SERVER = '10.170.0.117'
Linux117.IP_MGMT = '10.150.0.117'
Linux117.OVERSIZE_LIMIT = '30'

Linux101 = cli_node.CentosCli(
    ip='172.18.29.101',
    conn_type=cli_node.ConnType.SSH,
    user='root',
    passwd='fortinet',
    timeout=40)
Linux101.FQDN = 'server101.ftnt.net'
Linux101.IF_CLIENT = 'eth7'
Linux101.IF_INET = 'eth5'
Linux101.IF_SERVER = 'eth6'
Linux101.IF_MGMT = 'eth4'
Linux101.IP_INET = '172.18.29.101'
Linux101.IP_CLIENT = '10.160.0.101'
Linux101.IP_SERVER = '10.170.0.101'
Linux101.IP_MGMT = '10.150.0.101'
Linux101.OVERSIZE_LIMIT = '30'

Linux103 = cli_node.UbuntuCli(
    ip='172.18.29.103',
    port=22,
    user='leo',
    passwd='leo',
    conn_type=cli_node.ConnType.SSH,
    timeout=40,
    labels={'IF_CLIENT': 'eth7',
            'IF_INET': 'eth5',
            'IF_SERVER': 'eth6',
            'IF_MGMT': 'eth8',
            'IP_CLIENT': '10.160.0.103',
            'IP_INET': '172.18.29.103',
            'IP_SERVER': '10.170.0.103',
            'IP_MGMT': '10.150.0.103',
            'FQDN': 'client103.ftnt.net'
            }
)

Linux105 = cli_node.UbuntuCli(
    ip='172.18.29.105',
    port=22,
    user='leo',
    passwd='leo',
    conn_type=cli_node.ConnType.SSH,
    timeout=40,
    labels={'IF_CLIENT': 'eth7',
            'IF_INET': 'eth5',
            'IF_SERVER': 'eth6',
            'IF_MGMT': 'eth8',
            'IP_CLIENT': '10.160.0.105',
            'IP_INET': '172.18.29.105',
            'IP_SERVER': '10.170.0.105',
            'IP_MGMT': '10.150.0.105',
            'FQDN': 'client105.ftnt.net'
            }
)

Linux106 = cli_node.UbuntuCli(
    ip='172.18.29.106',
    port=22,
    user='leo',
    passwd='leo',
    conn_type=cli_node.ConnType.SSH,
    timeout=40,
    labels={'IF_CLIENT': 'ens192',
            'IF_INET': 'ens160',
            'IF_SERVER': 'ens224',
            'IF_MGMT': 'ens256',
            'IP_CLIENT': '10.160.0.106',
            'IP_INET': '172.18.29.106',
            'IP_SERVER': '10.170.0.106',
            'IP_MGMT': '10.150.0.106',
            'FQDN': 'client105.ftnt.net'
            }
)

Fpx_15 = ftnt_cli.FpxCli(
    ip='172.18.29.15',
    # port=23,
    user='admin',
    passwd='',
    conn_type=cli_node.ConnType.TELNET,
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_CLIENT': '10.160.0.15',
            'IP_SERVER': '10.170.0.15',
            'IP_MGMT': '10.150.0.15',
            'PROXY_PORT': '8080',
            'FTP_PROXY_PORT': '2121',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '172.18.29.1',
            'CP_FQDN': 'fpx15.fpxlab3.local'
            }
)

Fpx_11 = ftnt_cli.FpxCli(
    ip='172.18.29.11',
    port=22,
    conn_type=cli_node.ConnType.SSH,
    passwd='',
    user='admin',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '172.18.29.11',
            'IP_CLIENT': '10.160.0.11',
            'IP_SERVER': '10.170.0.11',
            'IP_MGMT': '10.150.0.11',
            'PROXY_PORT': '8080',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '172.18.29.1',
            'CP_FQDN': 'fpx11.fpxlab3.local'
            }
)

Fpx_8 = ftnt_cli.FpxCli(
    ip='172.18.29.8',
    port=22,
    conn_type=cli_node.ConnType.SSH,
    passwd='',
    user='admin',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '172.18.29.8',
            'IP_CLIENT': '10.160.0.8',
            'IP_SERVER': '10.170.0.8',
            'IP_MGMT': '10.150.0.8',
            'PROXY_PORT': '8080',
            'SERVER_OUTGOING_IP1': '10.170.0.208',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '172.18.29.1',
            'CP_FQDN': 'fpx8.fpxlab3.local'
            }
)

Fpx_7 = ftnt_cli.FpxCli(
    ip='172.18.29.7',
    port=22,
    conn_type=cli_node.ConnType.SSH,
    passwd='',
    user='admin',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '172.18.29.7',
            'IP_CLIENT': '10.160.0.7',
            'IP_SERVER': '10.170.0.7',
            'IP_MGMT': '10.150.0.7',
            'PROXY_PORT': '8080',
            'SERVER_OUTGOING_IP1': '10.170.0.207',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '172.18.29.1',
            'CP_FQDN': 'fpx7.fpxlab3.local'
            }
)

Fpx_2 = ftnt_cli.FpxCli(
    ip='172.18.29.2',
    port=22,
    conn_type=cli_node.ConnType.SSH,
    passwd='',
    user='admin',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '172.18.29.2',
            'IP_CLIENT': '10.160.0.2',
            'IP_SERVER': '10.170.0.2',
            'IP_MGMT': '10.150.0.2',
            'PROXY_PORT': '8080',
            'SERVER_OUTGOING_IP1': '10.170.0.203',
            'SERVER_OUTGOING_IP2': '10.170.0.204',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '172.18.29.1',
            'CP_FQDN': 'fpx2.fpxlab3.local'
            }
)

FpxGui_2 = ftnt_gui.FpxGui(
    ip='172.18.29.2',
    # port=80,
    conn_type=gui_node.GuiType.HTTP,
    browser_type=BrowserType.FIREFOX,
    accept_untrusted_cert=True,
    passwd='',
    user='admin',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '172.18.29.2',
            'IP_CLIENT': '10.160.0.2',
            'IP_SERVER': '10.170.0.2',
            'IP_MGMT': '10.150.0.2',
            'PROXY_PORT': '8080',
            'SERVER_OUTGOING_IP1': '10.170.0.203',
            'SERVER_OUTGOING_IP2': '10.170.0.204',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '172.18.29.1'
            }
)

Fpx_9 = ftnt_cli.FpxCli(
    ip='172.18.29.9',
    port=23,
    passwd='leo',
    user='leo',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '172.18.29.9',
            'IP_CLIENT': '10.160.0.9',
            'IP_SERVER': '10.170.0.9',
            'SERVER_OUTGOING_IP1': '10.170.0.217',
            'SERVER_OUTGOING_IP2': '10.170.0.218',
            'IP_MGMT': '10.150.0.9',
            'PROXY_PORT': '8080',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '172.18.29.1',
            'CP_FQDN': 'fpx9.fpxlab3.local'
            }
)

Fgt_4 = ftnt_cli.FgtCli(
    ip='172.18.29.4',
    port=23,
    passwd='leo',
    user='leo',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '172.18.29.4',
            'IP_CLIENT': '10.160.0.4',
            'IP_SERVER': '10.170.0.4',
            'IP_MGMT': '10.150.0.4',
            'PROXY_PORT': '8080',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '172.18.29.1'
            }
)

Fpx_10 = ftnt_cli.FpxCli(
    ip='172.18.29.10',
    passwd='',
    user='admin',
    version='2.0',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '172.18.29.10',
            'IP_CLIENT': '10.160.0.10',
            'IP_SERVER': '10.170.0.10',
            'IP_MGMT': '10.150.0.10'
            }
)
