import os
import sys

runner_dir = os.path.dirname(os.path.abspath(__file__))
pysys_root = os.path.abspath(runner_dir + '/..')
sys.path.append(pysys_root)

# from monitor import pysys_log
# pysys_log.init_logger()
