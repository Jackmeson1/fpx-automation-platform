import os
import sys
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'PySystem'))

# Provide dummy modules required by run.py
sys.modules['sysinit'] = types.SimpleNamespace(pysys_root='.')
pysys_logger = types.SimpleNamespace(warning=lambda *a, **k: None)
sys.modules['monitor.pysys_log'] = types.SimpleNamespace(pysys_logger=pysys_logger)
sys.modules['monitor'] = types.ModuleType('monitor')

def _gen_logdir(path: str) -> str:
    path = '/' + str(path).strip('/')
    if not os.path.exists(path):
        os.makedirs(path)
    log_dir = os.path.join(path, 'current')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

helpers = types.SimpleNamespace(format_path=lambda p: '/' + str(p).strip('/'), gen_logdir=_gen_logdir)
sys.modules['SystemTestCase.helpers'] = helpers
sys.modules['SystemTestCase.sys_suite'] = types.ModuleType('sys_suite')
sys.modules['SystemTestCase.sys_suite'].SysTestSuite = object
sys.modules['SystemTestCase.sys_suite'].CsvFields = object
sys.modules['SystemTestCase.SysTestCase'] = types.ModuleType('SysTestCase')
sys.modules['SystemTestCase.SysTestCase'].TcFailAction = type('TcFailAction', (), {})
sys.modules['executor.sysrunner'] = types.ModuleType('sysrunner')
sys.modules['executor.sysrunner'].SysTestRunner = object
ENV = types.SimpleNamespace(CTRL_PC=types.SimpleNamespace(ip='localhost'))
sys.modules['config.environment'] = types.SimpleNamespace(ENV=ENV)

import importlib.util

spec = importlib.util.spec_from_file_location(
    "run", os.path.join(ROOT, "PySystem", "sysrunner", "run.py")
)
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)


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


def test_setup_report_dir_symlink_fail(tmp_path, monkeypatch, capsys):
    log_base = tmp_path / 'logs'
    log_base.mkdir()
    log_dir = run.helpers.gen_logdir(str(log_base))
    http_base_dir = tmp_path / 'html'
    http_base_dir.mkdir()

    def fake_symlink(src, dst, *a, **k):
        raise PermissionError('no')

    monkeypatch.setattr(os, 'symlink', fake_symlink)
    report_url = run.setup_report_dir(str(log_base), str(http_base_dir), '/p', str(log_dir))
    out = capsys.readouterr().out
    assert report_url.startswith('file://')
    assert 'Please open' in out

