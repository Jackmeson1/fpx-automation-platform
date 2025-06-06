import os
import sys
import types
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'PySystem'))

# Provide dummy modules required by cli_node imports
dummy_logger = types.SimpleNamespace(warning=lambda *a, **k: None,
                                     error=lambda *a, **k: None)
monitor_logger = types.SimpleNamespace(get_logger=lambda name=None: dummy_logger,
                                       init_logger=lambda *a, **k: dummy_logger)
sys.modules['monitor.logger'] = monitor_logger
monitor_pkg = types.ModuleType('monitor')
monitor_pkg.get_logger = monitor_logger.get_logger
monitor_pkg.init_logger = monitor_logger.init_logger
sys.modules['monitor'] = monitor_pkg
sys.modules['SystemTestCase.sys_suite'] = types.ModuleType('sys_suite')
sys.modules['SystemTestCase.sys_suite'].SysTestSuite = object
sys.modules['SystemTestCase.sys_suite'].CsvFields = object
sys.modules['executor.sysrunner'] = types.ModuleType('sysrunner')
sys.modules['executor.sysrunner'].SysTestRunner = object
sys.modules['executor.sysrunner'].TestStatus = type('TestStatus', (), {})
sys.modules['executor.sysrunner'].SysTestResult = object
sys.modules['keyboard'] = types.ModuleType('keyboard')
ENV = types.SimpleNamespace(CTRL_PC=types.SimpleNamespace(ip='localhost'))
sys.modules['config.environment'] = types.SimpleNamespace(ENV=ENV)

from PySystem.SystemObject.cli_node import CliNode, SysTcFail, TcFailAction


class DummyCli(CliNode):
    pass


def test_login_failure_raises(tmp_path, monkeypatch):
    node = DummyCli(ip='1.2.3.4', attempts=1)

    def fake_spawn(*a, **k):
        raise OSError('unreachable')

    monkeypatch.setattr(node, '_spawn', fake_spawn)

    with pytest.raises(SysTcFail) as exc:
        node.login()

    assert exc.value.action == TcFailAction.NEXT
    assert not node.logged_in
