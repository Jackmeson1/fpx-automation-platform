# FPX Automation Platform

This repository hosts utilities and helpers used for system level testing of the FPX platform.

## ✨ Quick Start

```bash
# 1) copy the sample configuration and edit it
cp PySystem/config/config_sample.yaml PySystem/config/config_local.yaml
#    modify config_local.yaml with real IPs and credentials

# 2) pick or edit a runtime profile
cp PySystem/config/profiles/default.json PySystem/config/profiles/my.json
#    edit fields such as node_list or sce_root as needed

# 3) run one scenario
python PySystem/sysrunner/run.py --profile=my Policy-Matching/Explicit-L7/10001

# 4) open the report in your browser
#    (CTRL_PC IP + http_base_path + "/logs/current/scenario.html")
#    e.g. http://10.0.0.1/pysystem/logs/current/scenario.html
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

## 🧯 Troubleshooting

* **No report generated** – check that the `log_dir` location is writable
  and that all dependencies are installed.
* **SSH/Telnet connection fails** – verify the IP/username/password in
  `config_local.yaml` or environment variable overrides.

