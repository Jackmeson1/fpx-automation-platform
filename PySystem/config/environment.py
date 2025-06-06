# from config.elements import *
from config import elements

#
# env = {'PC1': 'Ubuntu105',
#        'FPX1': 'FPX5',
#        'SERVER': 'SERVER101'}

class ENV:
    CTRL_PC = elements.LOCALHOST  # LOCAL must be defined
    # PC1 = elements.Linux105
    # SERVER1 = elements.Linux101
    # SERVER2 = elements.Linux111
    # FPX1 = elements.Fpx_9
    # FPX2 = elements.Fpx_5
    PC1 = None
    SERVER1 = None
    SERVER2 = None
    FPX1 = None
    FPX2 = None
    labels = {}
    node_list = []
