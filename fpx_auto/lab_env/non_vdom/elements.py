"""
Define the Customer Lab elements
"""
# import sys
# proj_dirs: tuple = ('/Project/fpx_auto',)
# for proj_dir in proj_dirs:
#         sys.path.append(proj_dir)
from SystemObject.gui_node import BrowserType
from ftnt_nodes import ftnt_cli, ftnt_gui
from SystemObject import cli_node, gui_node

# localhost must be defined
LOCALHOST = cli_node.UbuntuCli(
    ip='localhost',
    port=22,
    passwd='leo',
    user='leo'
)

CTRL_SERVER_116 = cli_node.UbuntuCli(
    #ip='172.18.29.116',
    ip='10.150.0.116',
    port=22,
    passwd='leo',
    user='leo'
)

Linux111 = cli_node.UbuntuCli(
    #ip='172.18.29.111',
    ip='10.150.0.111',
    conn_type=cli_node.ConnType.SSH,
    hostname='ubuntu111',
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
        'DEFAULT_GATEWAY': '172.18.29.1',
        'OVERSIZE_LIMIT': '30'
    }
)

Linux117 = cli_node.CentosCli(
    #ip='172.18.29.117',
    ip='10.150.0.117',
    conn_type=cli_node.ConnType.SSH,
    hostname='centos117',
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
Linux117.DEFAULT_GATEWAY = '172.18.29.1'

Linux110 = cli_node.CentosCli(
    #ip='172.18.29.110',
    ip='10.150.0.110',
    conn_type=cli_node.ConnType.SSH,
    hostname='host110',
    user='root',
    passwd='fortinet',
    timeout=40)
Linux110.FQDN = 'server110.ftnt.net'
Linux110.IF_CLIENT = 'eth7'
Linux110.IF_INET = 'eth5'
Linux110.IF_SERVER = 'eth6'
Linux110.IF_MGMT = 'eth4'
Linux110.IP_INET = '172.18.29.110'
Linux110.IP_CLIENT = '10.160.0.110'
Linux110.IP_SERVER = '10.170.0.110'
Linux110.IP_MGMT = '10.150.0.110'
Linux110.OVERSIZE_LIMIT = '30'
#Linux110.DEFAULT_GATEWAY = '172.18.29.1'
Linux110.DEFAULT_GATEWAY = '10.150.0.4'

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
Linux101.DEFAULT_GATEWAY = '172.18.29.1'

Linux103 = cli_node.UbuntuCli(
    #ip='172.18.29.103',
    ip='10.150.0.103',
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
            'DEFAULT_GATEWAY': '172.18.29.1',
            'FQDN': 'client103.ftnt.net'
            }
)

Linux105 = cli_node.UbuntuCli(
    #ip='172.18.29.105',
    ip='10.150.0.105',
    port=22,
    user='leo',
    passwd='leo',
    conn_type=cli_node.ConnType.SSH,
    timeout=30,
    labels={'IF_CLIENT': 'ens192',
            'IF_INET': 'ens160',
            'IF_SERVER': 'ens224',
            'IF_MGMT': 'ens256',
            'IP_CLIENT': '10.160.0.105',
            'IP_CLIENT_SEC': '10.160.0.104',
            'IP_INET': '172.18.29.105',
            'IP_SERVER': '10.170.0.105',
            'IP_MGMT': '10.150.0.105',
            'DEFAULT_GATEWAY': '172.18.29.1',
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
            'DEFAULT_GATEWAY': '172.18.29.1',
            'FQDN': 'client106.ftnt.net'
            }
)

Linux109 = cli_node.UbuntuCli( # TP_client
    ip='172.18.29.109',
    #ip='10.150.0.109',
    port=22,
    user='leo',
    passwd='leo',
    conn_type=cli_node.ConnType.SSH,
    timeout=40,
    labels={
            'IF_CLIENT': 'ens256',
            'IP_CLIENT': '10.150.0.109',
            'DEFAULT_GATEWAY': '172.18.29.1',
            'FQDN': 'client109.ftnt.net'
            }
)

Fpx_69 = ftnt_cli.FpxCli(
    ip='172.18.20.69',
    port=22,
    conn_type=cli_node.ConnType.SSH,
    passwd='',
    user='admin',
    hostname='FPX69',
    labels={'IF_CLIENT': 'port6',
            'IF_INET': 'port4',
            'IF_MGMT': 'port1',
            'IP_INET': '10.1.1.69',
            'IP_MGMT': '10.150.0.69',
            'PROXY_PORT': '8080',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '10.1.1.1',
            'CP_FQDN': 'fpx69.fpxlab1.local'
            }
)


Fpx_15 = ftnt_cli.FpxCli(
    #ip='172.18.29.15',
    ip='10.150.0.15',
    # port=23,
    user='admin',
    passwd='',
    hostname='FPX15',
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
            'ICAP_SERVICE': 'FPX15_ICAP_SERVICE',
            'CP_FQDN': 'fpx15.fpxlab1.local'
            }
)

Fpx_2 = ftnt_cli.FpxCli(
    #ip='172.18.29.2',
    ip='10.150.0.2',
    port=23,
    conn_type=cli_node.ConnType.TELNET,
    passwd='',
    user='admin',
    hostname='FPX2',
    # version='7.0',
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
            'CP_FQDN': 'fpx2.fpxlab1.local'
            }
)

Fpx_az_32 = ftnt_cli.FpxCli(
    ip='52.6.17.72',
    port=22,
    conn_type=cli_node.ConnType.SSH,
    passwd='',
    user='admin',
    # version='7.0',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '10.0.0.32',
            'IP_CLIENT': '10.0.1.32',
            'IP_SERVER': '10.0.2.32',
            'IP_MGMT': '10.0.3.32',
            'PROXY_PORT': '8080',
            'SERVER_OUTGOING_IP1': '10.0.0.132',
            'SERVER_OUTGOING_IP2': '10.0.0.133',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '10.0.0.1'
            }
)

Fpx_az_32_GUI = ftnt_gui.FosGui(
    ip='52.6.17.72',
    conn_type=gui_node.GuiType.HTTP,
    browser_type=BrowserType.FIREFOX,
    passwd='PWD4fortinet',
    user='leo',
    # version='7.0',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '10.0.0.32',
            'IP_CLIENT': '10.0.1.32',
            'IP_SERVER': '10.0.2.32',
            'IP_MGMT': '10.0.3.32',
            'PROXY_PORT': '8080',
            'SERVER_OUTGOING_IP1': '10.0.0.132',
            'SERVER_OUTGOING_IP2': '10.0.0.133',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '10.0.0.1'
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
    #ip='172.18.29.10',
    ip='10.150.0.10',
    passwd='',
    hostname='FPX10',
    user='admin',
    version='2.0',
    labels={'IF_CLIENT': 'port2',
            'IF_INET': 'port1',
            'IF_SERVER': 'port3',
            'IF_MGMT': 'port4',
            'IP_INET': '172.18.29.10',
            'IP_CLIENT': '10.160.0.10',
            'IP_SERVER': '10.170.0.10',
            'IP_MGMT': '10.150.0.10',
            'PROXY_PORT': '8080',
            'FTP_PROXY_PORT': '2121',
            'IF_DEFAULT_ROUTE': 'port1',
            'DEFAULT_GATEWAY': '172.18.29.1',
            'ICAP_SERVICE': 'FPX10_ICAP_SERVICE',
            'CP_FQDN': 'fpx10.fpxlab3.local'
            }
)
