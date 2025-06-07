import os
import sys
import types
import importlib.util
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'PySystem'))

# Dummy modules for dependencies
dummy_logger = types.SimpleNamespace(warning=lambda *a, **k: None,
                                     error=lambda *a, **k: None)
monitor_logger = types.SimpleNamespace(get_logger=lambda name=None: dummy_logger,
                                       init_logger=lambda *a, **k: dummy_logger)
sys.modules['monitor.logger'] = monitor_logger
monitor_pkg = types.ModuleType('monitor')
monitor_pkg.get_logger = monitor_logger.get_logger
monitor_pkg.init_logger = monitor_logger.init_logger
sys.modules['monitor'] = monitor_pkg
class _Spawn(object):
    def __init__(self, *a, **k):
        pass
sys.modules["pexpect"] = types.SimpleNamespace(spawn=_Spawn, TIMEOUT=None, EOF=None)
# Stub numpy and pandas modules
sys.modules.setdefault("numpy", types.ModuleType("numpy"))
sys.modules.setdefault("pandas", types.ModuleType("pandas"))
sys.modules["yaml"] = types.ModuleType("yaml")
sys.modules["yaml"].safe_load = lambda *a, **k: {"CTRL_PC": {"class": "UbuntuCli", "ip": "localhost"}}
sys.modules.setdefault("pandas.core", types.ModuleType("pandas.core"))
sys.modules.setdefault("pandas.core.frame", types.ModuleType("pandas.core.frame"))
sys.modules["pandas"].read_csv = lambda *a, **k: None
sys.modules["pandas.core.frame"].DataFrame = object


sys.modules['sysinit'] = types.SimpleNamespace(pysys_root='.')

# Helpers required by run.py

def _gen_logdir(path: str) -> str:
    path = '/' + str(path).strip('/')
    if not os.path.exists(path):
        os.makedirs(path)
    log_dir = os.path.join(path, 'current')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

helpers = types.SimpleNamespace(format_path=lambda p: '/' + str(p).strip('/'),
                                gen_logdir=_gen_logdir)
sys.modules['SystemTestCase.helpers'] = helpers
sys.modules['SystemTestCase.sys_suite'] = types.ModuleType('sys_suite')
sys.modules['SystemTestCase.sys_suite'].SysTestSuite = object
sys.modules["SystemTestCase"] = types.ModuleType("SystemTestCase")
sys.modules["SystemTestCase"].SysTestCase = object
sys.modules['SystemTestCase.sys_suite'].CsvFields = object
sys.modules['SystemTestCase.SysTestCase'] = types.ModuleType('SysTestCase')
sys.modules["SystemTestCase.SysTestCase"].TcFailAction = type("TcFailAction", (), {"NEXT": "NEXT"})
sys.modules["SystemTestCase.SysTestCase"].SysTestCase = object
sys.modules["SystemTestCase.tc_mapping"] = types.ModuleType("tc_mapping")
sys.modules["SystemTestCase.tc_mapping"].TcFuncMapping = object
sys.modules['executor.sysrunner'] = types.ModuleType('sysrunner')
class _SysTcFail(Exception):
    def __init__(self, *a, action=None, **k):
        super().__init__(*a)
        self.action = action
sys.modules["SystemTestCase.SysTestCase"].SysTcFail = _SysTcFail
sys.modules['executor.sysrunner'].SysTestRunner = object
sys.modules['executor.sysrunner'].TestStatus = type('TestStatus', (), {})
sys.modules['executor.sysrunner'].SysTestResult = object

ENV = types.SimpleNamespace(CTRL_PC=types.SimpleNamespace(ip='localhost'))
sys.modules['config.environment'] = types.SimpleNamespace(ENV=ENV)

spec = importlib.util.spec_from_file_location(
    'run', os.path.join(ROOT, 'PySystem', 'sysrunner', 'run.py')
)
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)

from PySystem.SystemObject.cli_node import CliNode, SysTcFail, TcFailAction
from PySystem.config import elements


class DummyCli(CliNode):
    pass


def test_elements_loaded():
    assert elements.CTRL_PC.ip == 'localhost'


def test_setup_report_dir_no_permission(tmp_path, monkeypatch, capsys):
    log_base = tmp_path / 'proj' / 'logs'
    log_base.mkdir(parents=True)
    log_dir = run.helpers.gen_logdir(str(log_base))
    http_base_dir = tmp_path / 'html'
    http_base_dir.mkdir()
    monkeypatch.setattr(os, 'access', lambda *a, **k: False)
    report_url = run.setup_report_dir(str(log_base), str(http_base_dir), '/pysystem', str(log_dir))
    out = capsys.readouterr().out
    assert report_url.startswith('file://')
    assert 'Please open' in out
    assert os.path.exists(log_dir)


def test_login_failure_raises(monkeypatch):
    node = DummyCli(ip='1.2.3.4', attempts=1)

    def fake_spawn(*a, **k):
        raise OSError('unreachable')

    monkeypatch.setattr(node, '_spawn', fake_spawn, raising=False)

    with pytest.raises(SysTcFail) as exc:
        node.login()

    assert exc.value.action == TcFailAction.NEXT
    assert not node.logged_in
