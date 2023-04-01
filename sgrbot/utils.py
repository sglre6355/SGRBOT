from __future__ import annotations

from typing import TYPE_CHECKING

import toml

if TYPE_CHECKING:
    from typing import Any


def load_config_file(path: str, mode: str = "r") -> dict[str, Any]:
    with open(path, mode) as f:
        return toml.load(f)
