from SystemObject import cli_node
from config import properties
import sys
# sys.path.append(properties.project_dir)
# from ftnt_nodes import ftnt_cli

LOCALHOST = cli_node.UbuntuCli(
        ip='localhost',
        port=22,
        # passwd='leo',
        # user='leo')
        passwd='waternet',
        user='leonardo'
        )

Linux111 = cli_node.UbuntuCli(
        ip='172.18.29.111',
        conn_type=cli_node.ConnType.SSH,
        user='leonardo',
        passwd='leonardo',
        timeout=40,
        labels= {
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

Linux101 = cli_node.CentosCli(
        ip='172.18.29.101',
        conn_type=cli_node.ConnType.SSH,
        user='root',
        passwd='fortinet',
        timeout=40)
Linux101.IF_CLIENT = 'eth1'
Linux101.IF_INET = 'eth0'
Linux101.IF_SERVER = 'eth2'
Linux101.IF_MGMT = 'eth3'
Linux101.IP_INET = '172.18.29.101'
Linux101.IP_CLIENT = '10.160.0.101'
Linux101.IP_SERVER = '10.170.0.101'
Linux101.IP_MGMT = '10.150.0.101'
Linux101.OVERSIZE_LIMIT = '30'


Linux105 = cli_node.UbuntuCli(
        ip='172.18.29.105',
        port=22,
        user='leo',
        passwd='leo',
        conn_type=cli_node.ConnType.SSH,
        timeout=20,
        labels={'IF_CLIENT': 'port2',
                'IF_INET': 'port1',
                'IF_SERVER': 'port3',
                'IF_MGMT': 'port4',
                'IP_CLIENT': '10.160.0.105',
                'IP_INET': '172.18.29.105',
                'IP_SERVER': '10.170.0.105',
                'IP_MGMT': '10.150.0.105'
                }
        )

# Fpx_5 = ftnt_cli.FpxCli(
#         ip='172.18.29.5',
#         port=23,
#         passwd='leo',
#         user='leo',
#         labels={'IF_CLIENT': 'port2',
#                 'IF_INET': 'port1',
#                 'IF_SERVER': 'port3',
#                 'IF_MGMT': 'port4',
#                 'IP_CLIENT': '10.160.0.5',
#                 'PROXY_PORT': '8080',
#                 'FTP_PROXY_PORT': '21',
#                 'IF_DEFAULT_ROUTE': 'port1',
#                 'DEFAULT_GATEWAY': '172.18.29.1'
#                 }
#         )
#
# Fpx_2 = ftnt_cli.FpxCli(
#         ip='172.18.29.2',
#         port=23,
#         passwd='admin',
#         user='admin',
#         #version='2.0',
#         labels={'IF_CLIENT': 'port2',
#                 'IF_INET': 'port1',
#                 'IF_SERVER': 'port3',
#                 'IF_MGMT': 'port4',
#                 'IP_INET': '172.18.29.2',
#                 'IP_CLIENT': '10.160.0.2',
#                 'IP_SERVER': '10.170.0.2',
#                 'IP_MGMT': '10.150.0.2',
#                 'PROXY_PORT': '8080',
#                 'SERVER_OUTGOING_IP1': '10.170.0.203',
#                 'SERVER_OUTGOING_IP2': '10.170.0.204',
#                 'IF_DEFAULT_ROUTE': 'port1',
#                 'DEFAULT_GATEWAY': '172.18.29.1'
#                 }
#         )
#
# Fpx_9 = ftnt_cli.FpxCli(
#         ip='172.18.29.9',
#         port=23,
#         passwd='leo',
#         user='leo',
#         labels={'IF_CLIENT': 'port2',
#                 'IF_INET': 'port1',
#                 'IF_SERVER': 'port3',
#                 'IF_MGMT': 'port4',
#                 'IP_INET': '172.18.29.9',
#                 'IP_CLIENT': '10.160.0.9',
#                 'IP_SERVER': '10.170.0.9',
#                 'SERVER_OUTGOING_IP1': '10.170.0.217',
#                 'SERVER_OUTGOING_IP2': '10.170.0.218',
#                 'IP_MGMT': '10.150.0.9',
#                 'PROXY_PORT': '8080',
#                 'IF_DEFAULT_ROUTE': 'port1',
#                 'DEFAULT_GATEWAY': '172.18.29.1'
#                 }
#         )

