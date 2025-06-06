"""Helper functions for PySystem Test Case
"""
from config.environment import ENV
import os
import datetime


def gen_logdir(path: str) -> str:
    path = format_path(path)
    if not os.path.exists(path):
        os.mkdir(path)
    link_name = path + '/current'
    path += '/{}'.format(datetime.datetime.now())
    os.mkdir(path)
    if os.path.exists(link_name):
        os.unlink(link_name)
    os.symlink(path, link_name, True)
    return path


def format_path(path: str) -> str:
    return '/' + path.strip().strip('/')


def format_col_name(field: str) -> str:
    return field.strip().upper()


def get_node_name(node) -> str:
    node_name = 'LOCAL'
    for k, v in ENV.__dict__.items():
        if v == node:
            node_name = k
    return node_name
