# from config.elements import *
#
# #
# # env = {'PC1': 'Ubuntu105',
# #        'FPX1': 'FPX5',
# #        'SERVER': 'SERVER101'}
#
# class ENV:
#     PC1 = Linux105
#     SERVER1 = Linux101
#     FPX1 = Fpx_2
#     FPX2 = Fpx_5

# from elements import *
# import elements as em
from . import elements as em
from config.environment import ENV

# ENV.CTRL_PC = em.LOCALHOST  # LOCAL must be defined
ENV.CTRL_PC = em.CTRL_SERVER_116  # LOCAL must be defined
ENV.PC1 = em.Linux105
ENV.SERVER1 = em.Linux101
ENV.PC2 = em.Linux106
ENV.SERVER2 = em.Linux111
ENV.FPX1 = em.Fpx_2
# ENV.FPX1_GUI = em.FpxGui_2
ENV.FPX2 = em.Fpx_10
