from monitor import pysys_log

def foo():
    if pysys_log:
        pysys_log.pysys_logger.warning('in modulex.foo')
    else:
        print('pysys_logger is not init in modulex')