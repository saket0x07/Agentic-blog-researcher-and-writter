from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config as _root_config

for _name in dir(_root_config):
    if _name.startswith("_"):
        continue
    globals()[_name] = getattr(_root_config, _name)

__all__ = [name for name in globals() if not name.startswith("_")]
