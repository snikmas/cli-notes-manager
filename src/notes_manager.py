# the module provides the ntoes model controller

from typing import Any, Dict, NamedTuple
from pathlib import Path

from src.database import DatabaseHandler

class CurrentNote(NamedTuple):
    note: Dict[str, Any]
    error:int

class Notes_manager:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)