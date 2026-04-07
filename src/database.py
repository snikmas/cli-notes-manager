import json
from typing import Any, Dict, List, NamedTuple
import configparser
from pathlib import Path
import logging

from . import DB_WRITE_ERROR, SUCCESS, DB_READ_ERROR, JSON_ERROR
logging.basicConfig(level=logging.INFO)

DEFAULT_DB_PATH = Path.cwd() / '_notes.json'

def get_database_path(config_file: Path) -> Path:
 #   'return the current paht ot the database'
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int:
#    'create notes db'
    try:
        db_path.write_text('{}')
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR

# it's better to do dict
class DBResponse(NamedTuple):
    notes_dict: Dict[str: Dict[str, Any]]
    error: int

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
    
    def read_notes(self) -> DBResponse:
        logging.info('we are in reading')
        try:
            with self._db_path.open('r') as db:
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError: 
                    return DBResponse([], JSON_ERROR)
        except OSError: 
            return DBResponse([], DB_READ_ERROR)
    
    def write_notes(self, notes_dict: Dict[str: Dict[str, Any]]) -> DBResponse:
        try: 
            with self._db_path.open('w') as db:
                json.dump(notes_dict, db, indent=4)
                return DBResponse(notes_dict, SUCCESS)
        except OSError:
            return DBResponse(notes_dict, DB_WRITE_ERROR)