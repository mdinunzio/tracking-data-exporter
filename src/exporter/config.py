import tomllib
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "general": {
        "default_days": 7,
        "output_dir": "~/tracking-exports",
        "prompt_file": "",
    },
}


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and validate TOML config, expanding ~ in paths."""
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    # Merge with defaults
    for section, defaults in DEFAULT_CONFIG.items():
        if section not in config:
            config[section] = {}
        for key, value in defaults.items():
            config[section].setdefault(key, value)

    # Expand ~ in path-like values
    _expand_paths(config)
    return config


def _expand_paths(config: dict[str, Any]) -> None:
    """Recursively expand ~ in string values that look like paths."""
    path_keys = {
        "output_dir", "vault_path", "prompt_file",
        "credentials_file", "token_file", "pickup_dir",
    }
    for section in config.values():
        if not isinstance(section, dict):
            continue
        for key, value in section.items():
            if key in path_keys and isinstance(value, str) and value:
                section[key] = str(Path(value).expanduser())
