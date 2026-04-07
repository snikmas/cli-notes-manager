from pathlib import Path
import typer
from . import __app_name__, __version__, ERRORS
from . import config, database, notes_manager
import logging 

logging.basicConfig(level=logging.INFO)


app = typer.Typer(no_args_is_help=True, suggest_commands=True)

@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_PATH),
        "--db-path", 
        "-db",
        prompt="notes database location?",
    ), 
) -> None:
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file: failed {ERRORS[app_init_error]}',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with {ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The notes database is {db_path}", fg=typer.colors.GREEN)


def get_notes_manager() -> notes_manager.Notes_Manager:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please, run "src init',
             fg=typer.colors.RED
        )
        raise typer.Exit(1)
    if db_path.exists():
        return notes_manager.Notes_Manager(db_path)
    else:
        typer.secho('Database not found. Please, run "src init"',
        fg=typer.colors.RED,
        )
        raise typer.Exit(1)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


def _normalize_tags(tags: str | None) -> list[str]:
    if not tags:
        return []
    tags = tags.split(' ')
    
    return tags

@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        '-v',
        help="Show the app's version and exit",
        callback=_version_callback,
        is_eager=True
    )
) -> None :
    pass

#do i need to create.. folders?
notes = []

@app.command("add")
def add_note(title: str = typer.Option(..., "--title", help="the title for a note"), 
             content: str = typer.Option(..., "--content", help="the content for a note"), 
             tags: str | None = typer.Option(None, '--tags', help="Repeat for multiple tags or use comma-separated values")):
    not_mng = get_notes_manager()
    note, error = not_mng.add(title, content, _normalize_tags(tags))
    if error:
        typer.secho(
            f"Error during adding: {ERRORS.get(error, error)}",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f'''
    ID: {note['id']}
    Title: {note['title']}
    Content: {note['content']}
    Tags: {note['tags']}
    Created_at: {note['created_at']}
''', fg=typer.colors.GREEN)


@app.command("delete")
def delete_note(title: str | None = typer.Option(None, '--title', help='Delete by title'),
                id: str | None = typer.Option(None, '--id', help='Delete by ID')):
    
    if (title and id):
        typer.secho(f"Error during command: you must write only title OR id note!", fg=typer.colors.RED)
        raise typer.Exit(1) 
    not_mng = get_notes_manager()
    res = not_mng.delete(title, id)
    

@app.command("update")
def update_note(title: str | None = typer.Option(None, '--title', help='Update by name'),
                id: str | None = typer.Option(None, '--id', help='Update by ID'),
                new_title: str | None = typer.Option(None, '--new_title', help='New title'),
                new_content: str | None = typer.Option(None, '--new_content', help='New content')):
    pass

@app.command('find')
def find_note(title: str | None = typer.Option(None, '--title', help='Find by title'),
                d: str | None = typer.Option(None, '--id', help='Find by ID')):
    pass

@app.command('get_all')
def get_all():
    pass


if __name__ == '__main__':
    app()
