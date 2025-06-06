# FPX Automation Platform

This repository contains testing utilities for the FPX platform.

## Configuration

Sensitive connection information is loaded from YAML files in `PySystem/config/`.
A sample file `config_sample.yaml` is provided. To use custom settings:

```bash
cp PySystem/config/config_sample.yaml PySystem/config/config_local.yaml
# Edit config_local.yaml and fill in the real IPs, usernames and passwords
```

The framework will load `config_local.yaml` automatically if it exists,
otherwise it falls back to `config_sample.yaml`.

All configuration fields can also be overridden using environment variables.
The variable name is built from the node name and field, for example
`CTRL_PC_IP` or `Linux101_PASSWD`. Nested `labels` fields can be overridden by
adding the label name, such as `Linux111_LABELS_IP_CLIENT`.
