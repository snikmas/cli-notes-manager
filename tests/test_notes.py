from typer.testing import CliRunner
import pytest
import json

from src import __app_name__, __version__, cli, SUCCESS
from src.notes_manager import Notes_Manager

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ['--version'])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}" in result.stdout


@pytest.fixture
def mock_json_file(tmp_path):
    notes = [
        {"title": "My thoughts", 
         "content": "this is my first thought"}]
    db_file = tmp_path / "notes.json"
    with db_file.open('w') as db:
        json.dump(notes, db, indent=4)
    return db_file    
    

test_data1 = {
    "title": "my english experience",
    "content": "in this notes i would like to introduce my learning english path",
    "tags": []
}
test_data2 = {
    "title": "this is my way to learn chinese",
    "content": "here i wanna share some tips to learn chinese efficiently",
    "tags": ["learning", "languages"]
}

@pytest.mark.parametrize(
    "title, content, tags",
    [
        pytest.param(
            test_data1['title'],
            test_data1['content'],
            test_data1['tags'],
        ),
    ],
)
def test_add(mock_json_file, title, content, tags):
    not_mgr = Notes_Manager(mock_json_file)
    result = not_mgr.add(title, content, tags)
    assert result.error == SUCCESS
    read = not_mgr._db_handler.read_notes()
    assert len(read.notes_list) == 2
