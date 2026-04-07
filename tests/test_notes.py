from typer.testing import CliRunner
import pytest
import json

from src import __app_name__, __version__, cli, SUCCESS
from src import config
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


def test_cli_add_with_tags(tmp_path, monkeypatch):
    db_file = tmp_path / "notes.json"
    db_file.write_text("[]")

    config_file = tmp_path / "config.ini"
    config_file.write_text(f"[General]\ndatabase = {db_file}\n")
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_file)

    result = runner.invoke(
        cli.app,
        [
            "add",
            "--title",
            "CLI note",
            "--content",
            "created from test",
            "--tags",
            "python",
            "--tags",
            "testing,cli",
        ],
    )

    assert result.exit_code == 0
    saved_notes = json.loads(db_file.read_text())
    assert len(saved_notes) == 1
    assert saved_notes[0]["tags"] == ["python", "testing", "cli"]


def test_cli_init_then_add(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_file = config_dir / "config.ini"
    db_file = tmp_path / "notes.json"

    monkeypatch.setattr(config, "CONFIG_DIR_PATH", config_dir)
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_file)

    init_result = runner.invoke(
        cli.app,
        ["init", "--db-path", str(db_file)],
    )

    assert init_result.exit_code == 0
    assert config_file.exists()
    assert db_file.exists()

    add_result = runner.invoke(
        cli.app,
        ["add", "--title", "Integrated", "--content", "flow works"],
    )

    assert add_result.exit_code == 0
    saved_notes = json.loads(db_file.read_text())
    assert len(saved_notes) == 1
    assert saved_notes[0]["title"] == "Integrated."
