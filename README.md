# FPX Automation Platform – Multi-node Functional Test Runner

Open-source toolkit to run multi-node functional tests (SSH/Telnet) on FortiProxy/FPX devices, with one-click HTML reporting.

![Python](https://img.shields.io/badge/python-3.9%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![CI](https://img.shields.io/badge/CI-passing-brightgreen)

## 🚀 Quick Start (3 minutes)

```bash
# 1. Clone & install
git clone https://github.com/fortinet/fpx-automation-platform.git && cd fpx-automation-platform
./setup_env.sh
# 2. Copy & edit config
cp PySystem/config/config_sample.yaml PySystem/config/config_local.yaml
$EDITOR PySystem/config/config_local.yaml
# 3. Run first scenario
python PySystem/sysrunner/run.py --profile=default Policy-Matching/Explicit-L7/10001
# 4. View report
open http://<CTRL_PC_IP>/pysystem/logs/current/scenario.html
```

## 🔧 Configuration

Connection information is stored in YAML files under `PySystem/config/`.
`config_local.yaml` is loaded automatically if present, otherwise the
framework falls back to `config_sample.yaml`.

Runtime options such as `tc_base`, `sce_root` and the `node_list` are
stored in JSON profiles under `PySystem/config/profiles/`. Use the
`--profile` argument of `run.py` to select one.

Configuration values can be overridden using environment variables. The
variable name is formed from the node name and field, for example
`CTRL_PC_IP=192.168.1.5` or `Linux101_PASSWD=secret`. Nested `labels`
fields can be overridden with an additional level such as
`Linux111_LABELS_IP_CLIENT`.

### Sample Fields

| Key        | Meaning                              |
|------------|--------------------------------------|
| `tc_base`  | Base directory of test cases         |
| `sce_root` | Location of scenarios (CSV files)    |
| `node_list`| Names of nodes defined in YAML config|
| `log_dir`  | Directory under `tc_base` for logs   |
| `obj_dirs` | Additional Python module locations    |
| `lab_dir`  | Path to lab environment modules       |
| `Xauthority` | X11 auth file for GUI tests         |
| `Webdriver_dir` | Directory containing WebDriver binaries |

The bundled profiles use example paths such as `/path/to/fpx_auto/`. These
should be replaced with real locations on your system. If any of the
required keys are missing at runtime `run.py` will exit with an error.

## 🏃 Running Tests

```bash
python PySystem/sysrunner/run.py --profile=default example.csv
```

Reports and logs are placed under `logs/current/` inside the directory
specified by `log_dir`. By default the URL of the HTML report is
`http://<CTRL_PC_IP>/pysystem/logs/current/scenario.html`.

## 🛠 Installation

Python **3.9+** is recommended. Install dependencies with:

```bash
pip install -r requirements.txt
```

The project can also be installed as a package:

```bash
pip install .
```

## 🧯 Troubleshooting

* **No report generated** – check that the `log_dir` location is writable
  and that all dependencies are installed.
* **SSH/Telnet connection fails** – verify the IP/username/password in
  `config_local.yaml` or environment variable overrides.

