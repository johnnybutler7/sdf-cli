import tempfile
from pathlib import Path

from sdf_cli.config.verification import load_verification_config


def load_config(content: str):
    return load_verification_config(write_config(content))


def write_config(content: str) -> Path:
    path = Path(tempfile.mkdtemp()) / "verification.yml"
    path.write_text(content.lstrip(), encoding="utf-8")
    return path
