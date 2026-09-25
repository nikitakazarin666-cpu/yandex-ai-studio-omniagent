import json
import os
from pathlib import Path


DEFAULT_CONFIG_PATH = "/etc/omniagent.config.json"


def load_agent_config():
    config_path = Path(
        os.getenv("OMNIAGENT_CONFIG", DEFAULT_CONFIG_PATH)
    )

    if not config_path.exists():
        raise FileNotFoundError(
            f"Agent config not found: {config_path}"
        )

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    return config
