import os
import yaml
from SystemObject import cli_node

# Path to configuration files
_conf_dir = os.path.dirname(os.path.abspath(__file__))
_sample_cfg = os.path.join(_conf_dir, 'config_sample.yaml')
_local_cfg = os.path.join(_conf_dir, 'config_local.yaml')


def _load_config():
    cfg_file = _local_cfg if os.path.exists(_local_cfg) else _sample_cfg
    with open(cfg_file, 'r') as f:
        config = yaml.safe_load(f) or {}

    def _override(prefix, data):
        for k, v in data.items():
            env_key = f"{prefix}_{k}".upper()
            if isinstance(v, dict):
                _override(env_key, v)
            else:
                env_val = os.getenv(env_key)
                if env_val is not None:
                    if isinstance(v, int):
                        try:
                            data[k] = int(env_val)
                        except ValueError:
                            data[k] = env_val
                    else:
                        data[k] = env_val
    for name, info in config.items():
        _override(name, info)
    return config


_cfg = _load_config()


def _create_node(params: dict):
    cls_name = params.pop('class', 'UbuntuCli')
    cls = getattr(cli_node, cls_name)
    if 'conn_type' in params and isinstance(params['conn_type'], str):
        params['conn_type'] = getattr(cli_node.ConnType, params['conn_type'])
    labels = params.get('labels') or {}
    node = cls(**{k: v for k, v in params.items() if k != 'labels'})
    for k, v in labels.items():
        setattr(node, k, v)
    if labels:
        node.labels = labels
    return node

# Export nodes as module attributes
for _name, _params in _cfg.items():
    globals()[_name] = _create_node(dict(_params))
