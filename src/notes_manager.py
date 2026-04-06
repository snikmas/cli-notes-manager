# the module provides the ntoes model controller

from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, NamedTuple
import uuid

from . import DB_READ_ERROR
from .database import DatabaseHandler

class CurrentNote(NamedTuple):
    note: Dict[str, Any]
    error: int


class Notes_Manager:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, 
            title: str, 
            content: str,
            tags: List[str] | None = None) -> CurrentNote:
        # add a new ntoe to the db
        full_title = title
        full_content = content

        if not full_title.endswith("."): 
            full_title += '.'
        
        if not full_content.endswith("."): 
            full_content += '.'

        now = datetime.now(timezone.utc)
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")

        #short uuid for personal app
        short_id = str(uuid.uuid4()).replace('-', '')[:8]
        note = {
            "id": short_id,
            "title": full_title,
            "content": full_content,
            "tags": tags or [],
            "created_at": formatted
        }

        read = self._db_handler.read_notes()
        if read.error == DB_READ_ERROR:
            return CurrentNote(note, read.error)
        read.notes_list.append(note)

        write = self._db_handler.write_notes(read.notes_list)
        return CurrentNote(note, write.error)
