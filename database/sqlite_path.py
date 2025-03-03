from pathlib import Path
from typing import Optional

_db_path: Optional[Path] = None


def set_db_path(path: Path) -> None:
    global _db_path
    _db_path = path


def get_db_path() -> Optional[Path]:
    return _db_path
